from flask import Flask, request
import os

# --- 1. CONFIGURACIÓN ---
app = Flask(__name__)

# Definir la carpeta donde se guardarán los archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- 2. ENDPOINT: INICIO (GET) ---
@app.route("/")
def hola_mundo():
    return "¡Hola Mundo! Soy tu Tutor de IA."

# --- 3. ENDPOINT: SUBIDA DE ARCHIVOS (POST) ---
@app.route("/upload", methods=['POST'])
def subir_archivo():
    # 1. Comprobar si la petición tiene el archivo
    if 'file' not in request.files:
        return "Error: No se encontró ningún archivo ('file') en la petición", 400

    file = request.files['file']

    # 2. Comprobar si el archivo tiene nombre (no es vacío)
    if file.filename == '':
        return "Error: El archivo no tiene nombre", 400

    # 3. Guardar el archivo de forma segura
    if file:
        # Crear la carpeta 'uploads' si no existe
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        return f"¡Archivo '{file.filename}' subido con éxito a la carpeta uploads!", 200

# --- 4. EJECUCIÓN ---
if __name__ == '__main__':
    app.run(debug=True)