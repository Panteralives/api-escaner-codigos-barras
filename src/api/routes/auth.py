from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import Usuario as UsuarioModel
from ..schemas import Token, Usuario, UsuarioCreate
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario
    """
    # Verificar si el username ya existe
    existing_user = db.query(UsuarioModel).filter(
        UsuarioModel.username == user.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El nombre de usuario ya existe"}
        )
    
    # Verificar si el email ya existe
    existing_email = db.query(UsuarioModel).filter(
        UsuarioModel.email == user.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El email ya está registrado"}
        )
    
    # Crear usuario
    hashed_password = get_password_hash(user.password)
    db_user = UsuarioModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión y obtener token JWT
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Credenciales incorrectas"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=Usuario)
async def read_users_me(
    current_user: UsuarioModel = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual
    """
    return current_user


@router.get("/verify")
async def verify_token(
    current_user: UsuarioModel = Depends(get_current_active_user)
):
    """
    Verificar si el token es válido
    """
    return {"valid": True, "username": current_user.username}