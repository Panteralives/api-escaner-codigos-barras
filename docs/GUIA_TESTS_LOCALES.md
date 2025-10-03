
Primero, necesitas asegurarte de tener todo lo necesario en tu computadora.

Instala Python: Si no lo tienes, descarga e instala Python 3.11 o una versión más reciente desde python.org.

Abre una terminal (o Símbolo del sistema):

En Windows, puedes buscar "cmd" o "PowerShell".
En macOS o Linux, puedes buscar "Terminal".
Clona el repositorio de GitHub: Si no tienes los archivos en tu computadora, clona el repositorio con este comando:

git clone https://github.com/Panteralives/api-escaner-codigos-barras.git



Navega a la carpeta del proyecto:

cd api-escaner-codigos-barras



Ahora que estás en la carpeta del proyecto, sigue estos pasos.

(Recomendado) Crea un entorno virtual: Esto aísla las dependencias de tu proyecto y evita conflictos.

python -m venv venv



Luego, activa el entorno virtual:

En Windows:
.\venv\Scripts\activate



En macOS y Linux:
source venv/bin/activate



Instala las dependencias del proyecto: El proyecto tiene un script para facilitar esto. Ejecuta:

python run.py --install



Inicializa la base de datos: Esto preparará la base de datos para los tests y la aplicación.

python run.py --init-db



¡Ejecuta los tests! Ahora que todo está instalado, puedes correr los tests con pytest:

pytest tests/



Esto ejecutará todos los archivos de testeo dentro de la carpeta tests/ y te mostrará los resultados. Si hay errores, los verás en la terminal.

Una vez que hayas corregido los errores y los tests pasen correctamente, sigue estos pasos para subir tus cambios.

Añade tus cambios al área de preparación (staging): Este comando añade todos los archivos que has modificado.

git add .



Crea un "commit" con tus cambios: Un commit es como una instantánea de tus cambios. Asegúrate de escribir un mensaje descriptivo.

git commit -m "Arreglados los errores y tests funcionando correctamente"



Sube tus cambios a GitHub: Este comando empuja tus commits al repositorio remoto en GitHub.

git push



¡Y eso es todo! Con estos pasos, podrás testear el código en tu máquina local y mantener tu repositorio de GitHub actualizado.
