"""
Advanced Authentication and User Management
Sistema completo de autenticación JWT con roles y permisos
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import os

from ...db.models_advanced import User, AuditLog, UserRole
from ...db.database import get_db_engine

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Dependency para obtener sesión de DB
def get_db():
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === UTILIDADES DE AUTENTICACIÓN ===

def hash_password(password: str) -> str:
    """Hash de password con bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decodificar y validar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Obtener usuario actual desde token JWT"""
    payload = decode_access_token(credentials.credentials)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user

def require_role(allowed_roles: List[UserRole]):
    """Decorator de dependency para requerir roles específicos"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return role_checker

# === MODELOS PYDANTIC ===

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.CASHIER
    phone: Optional[str] = None

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === ENDPOINTS DE AUTENTICACIÓN ===

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Autenticar usuario y generar token JWT"""
    
    # Buscar usuario
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    
    # Log de auditoría
    audit_log = AuditLog(
        user_id=user.id,
        action="LOGIN",
        table_name="users",
        record_id=user.id,
        new_values={"last_login": user.last_login.isoformat()}
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "permissions": _get_user_permissions(user.role)
        }
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cerrar sesión (invalidar token)"""
    
    # Log de auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="LOGOUT",
        table_name="users",
        record_id=current_user.id
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

# === ENDPOINTS DE GESTIÓN DE USUARIOS ===

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: CreateUserRequest, 
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario (solo Admin/Manager)"""
    
    # Verificar que username y email no existan
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Crear usuario
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        phone=user_data.phone,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log de auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="CREATE",
        table_name="users",
        record_id=new_user.id,
        new_values={
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role.value
        }
    )
    db.add(audit_log)
    db.commit()
    
    return new_user

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: Session = Depends(get_db)
):
    """Listar usuarios con filtros"""
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: Session = Depends(get_db)
):
    """Obtener usuario específico"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: Session = Depends(get_db)
):
    """Actualizar usuario"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Guardar valores antiguos para auditoría
    old_values = {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active
    }
    
    # Actualizar campos
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log de auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        table_name="users",
        record_id=user.id,
        old_values=old_values,
        new_values=update_data
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Eliminar usuario (solo Admin)"""
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log de auditoría antes de eliminar
    audit_log = AuditLog(
        user_id=current_user.id,
        action="DELETE",
        table_name="users",
        record_id=user.id,
        old_values={
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }
    )
    db.add(audit_log)
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}

@router.patch("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar password del usuario actual"""
    
    # Verificar password actual
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Actualizar password
    current_user.password_hash = hash_password(password_data.new_password)
    
    # Log de auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        table_name="users",
        record_id=current_user.id,
        new_values={"password_changed": datetime.utcnow().isoformat()}
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Password changed successfully"}

# === ENDPOINTS DE AUDITORÍA ===

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: Session = Depends(get_db)
):
    """Obtener logs de auditoría"""
    
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "user": {
                "id": log.user.id if log.user else None,
                "username": log.user.username if log.user else "System"
            },
            "action": log.action,
            "table_name": log.table_name,
            "record_id": log.record_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]

# === UTILIDADES ===

def _get_user_permissions(role: UserRole) -> List[str]:
    """Obtener permisos basados en el rol"""
    permissions_map = {
        UserRole.ADMIN: [
            "all_permissions", "manage_users", "view_reports", 
            "manage_products", "process_sales", "manage_config"
        ],
        UserRole.MANAGER: [
            "view_reports", "manage_products", "process_sales", 
            "manage_customers", "view_users"
        ],
        UserRole.CASHIER: [
            "process_sales", "view_products", "manage_customers"
        ],
        UserRole.INVENTORY: [
            "manage_products", "view_inventory_reports", "manage_stock"
        ]
    }
    return permissions_map.get(role, [])

@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Obtener permisos del usuario actual"""
    return {
        "user": current_user.username,
        "role": current_user.role.value,
        "permissions": _get_user_permissions(current_user.role)
    }