FROM odoo:17.0

# Instala dependencias adicionales si es necesario
USER root
RUN apt-get update && apt-get install -y python3-pip
USER odoo

RUN pip3 install PyJWT

# Copia los archivos del módulo a la carpeta de addons
COPY ./custom_addons /mnt/extra-addons