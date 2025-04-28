# Utiliza una imagen base ligera y especifica en lugar de una imagen general
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /usr/src/app

# Copia primero solo el archivo de requisitos para aprovechar el cache de Docker
COPY requirements.txt ./

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicacion al contenedor
COPY . .

# Ejecutar las migraciones de la base de datos
RUN python manage.py migrate

# Expone el puerto en el que escucha la aplicacion
EXPOSE 8000

# Define el comando predeterminado para ejecutar la aplicacion
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]