# Vetsoft

Aplicación web para veterinarias utilizada en la cursada 2024 de Ingeniería y Calidad de Software. UTN-FRLP

## Dependencias

-   python 3
-   Django
-   sqlite
-   playwright
-   ruff

## Instalar dependencias

`pip install -r requirements.txt`

## Iniciar la Base de Datos

`python manage.py migrate`

## Iniciar app

`python manage.py runserver`

## Ejecutar Proyecto Dockerizado

1. Construir la imagen docker: `build -t vetsoft-app:version .` (Se debe indicar una version inicial de la imagen)

2. Desplegar el contenedor, ejecutar: `docker run -p 8000:8000 --env-file .env vetsoft-app:version` (Se debe renombrar el archivo "env-example" por ".env" y agregar en el archivo el valor de las variables de entorno propias)

3. Accede a la dirección localhost:8000 para empezar a utilizar la aplicación