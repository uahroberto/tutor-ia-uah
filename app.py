from flask import Flask

# 1. Crear la aplicación de Flask
app = Flask(__name__)

# 2. Definir la primera "ruta" o "endpoint"
@app.route("/")
def hola_mundo():
    # Lo que la API devolverá
    return "¡Hola Mundo! Soy tu Tutor de IA."

# 3. Código para poder ejecutar el servidor con "python app.py"
if __name__ == '__main__':
    app.run(debug=True)