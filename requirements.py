import os
import subprocess

# Ruta donde se almacenarán los paquetes para la función Lambda
lambda_package_folder = "./"

# Crea la carpeta si no existe
if not os.path.exists(lambda_package_folder):
    os.makedirs(lambda_package_folder)

# Función para instalar los paquetes en la carpeta destino
def install_requirements(requirements_file):
    try:
        subprocess.run([
            "pip3.8",
            "install",
            "--upgrade",
            "--target",
            lambda_package_folder,
            "-r",
            requirements_file
        ], check=True)
        print(f"Paquetes instalados en {lambda_package_folder} con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error durante la instalación: {e}")

# Punto de entrada
if __name__ == "__main__":
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        install_requirements(requirements_file)
    else:
        print(f"Archivo {requirements_file} no encontrado.")
