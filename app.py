from flask import Flask, request, jsonify # Añadimos jsonify para las respuestas de chat
import os
import sys 
from dotenv import load_dotenv

# --- IMPORTACIONES DE RAG COMPLETAS ---
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS 
from langchain.chains import ConversationalRetrievalChain 
from langchain.chat_models import ChatOpenAI 
# --- FIN DE IMPORTACIONES RAG ---


# --- VARIABLES GLOBALES (Motor de Chat y Almacenamiento) ---
chat_engine = None
chat_history = []
db_store = None 
# --- FIN VARIABLES GLOBALES ---


# --- 1. CONFIGURACIÓN ---
app = Flask(__name__)

# Configuración del path para la carpeta de subidas (uploads)
current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
sys.path.append(current_dir)

# --- CARGAR LA CLAVE SECRETA ---
load_dotenv() # Carga la clave OPENAI_API_KEY desde el archivo .env


# --- 2. ENDPOINT: INICIO (GET) ---
@app.route("/")
def hola_mundo():
    return "¡Hola Mundo! Soy tu Tutor de IA."


# -------------------------------------------------------------------------
# --- ENDPOINT 3: SUBIDA DE ARCHIVOS Y CONSTRUCCIÓN DE MOTOR (/upload) ---
# -------------------------------------------------------------------------

@app.route("/upload", methods=['POST'])
def subir_archivo():
    # Accedemos a las variables globales para poder modificarlas
    global chat_engine, chat_history, db_store 
    
    # 1. Comprobación de que el archivo existe
    if 'file' not in request.files:
        return "Error: No se encontró ningún archivo ('file').", 400
    
    file = request.files['file']

    # 2. Comprobaciones de formato
    if file.filename == '':
        return "Error: El archivo no tiene nombre.", 400
    if not file.filename.lower().endswith('.pdf'):
        return "Error: Por favor, sube un archivo con extensión .PDF", 400

    
    # 3. Guardar el archivo
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    # --- 4. LLAMADA AL NÚCLEO DE IA Y CONSTRUCCIÓN DEL MOTOR ---
    print(f"\n[INFO] Iniciando procesamiento de IA y construcción del motor...")
    
    try:
        # A. Crea la Base de Vectores (Vectorización)
        db_store = crear_base_de_vectores(filepath)
        
        if db_store:
            # B. Crea el Motor de Chat
            chat_engine = crear_motor_de_chat(db_store)
            chat_history = [] # Reinicia el historial
            
            return (f"¡Archivo '{file.filename}' subido y procesado! "
                    f"Motor de chat listo para chatear.", 200)
        else:
            return "¡Archivo subido, pero falló la creación de la base de vectores!", 500
    
    except Exception as e:
        print(f"[ERROR CRÍTICO AL CONSTRUIR EL MOTOR DE IA] {e}")
        return f"Error interno: {e}", 500


# -----------------------------------------------------------------
# --- ENDPOINT 4: MOTOR DE CHAT (/chat) ---
# -----------------------------------------------------------------

@app.route("/chat", methods=['POST'])
def handle_chat():
    global chat_engine, chat_history
    
    # 1. Comprueba si la base de datos de documentos está lista
    if chat_engine is None:
        return jsonify({"error": "No se ha procesado ningún PDF. Por favor, usa /upload primero."}), 400
    
    # 2. Obtiene los datos del JSON (Pregunta)
    # Usamos request.get_json() porque curl enviará datos JSON
    try:
        data = request.get_json(force=True)
        pregunta = data.get('question', '')
    except:
        return jsonify({"error": "Petición JSON no válida. Asegúrate de usar 'Content-Type: application/json'."}), 400

    if not pregunta:
        return jsonify({"error": "La pregunta no puede estar vacía."}), 400
    
    # 3. Llama al motor de chat
    respuesta = chatear(pregunta, chat_engine, chat_history)
    
    # 4. Actualiza el historial (pregunta y respuesta)
    chat_history.append((pregunta, respuesta))
    
    print(f"[CHAT] Pregunta: {pregunta}")
    print(f"[CHAT] Respuesta: {respuesta}")

    return jsonify({"answer": respuesta})


# =========================================================================
# === FUNCIONES DE RAG PEGADAS DE IA_CORE.PY (Vectorización y Motor) ===
# =========================================================================

# app.py (dentro de la sección de Funciones RAG)

# 1. Función que genera la Base de Vectores (Vector Store)
def crear_base_de_vectores(filepath):
    """Carga el PDF, lo trocea, lo vectoriza y lo almacena en FAISS."""
    
    # --- CÓDIGO CORREGIDO: Cargar la clave directamente del entorno ---
    # Obtenemos la clave *antes* de la creación de embeddings
    openai_key = os.getenv("OPENAI_API_KEY") 
    
    if not openai_key:
        print("[ERROR] NO se encontró la clave OPENAI_API_KEY. Fallo de autenticación.")
        # Lanza una excepción para que el try/except del /upload la capture
        raise ValueError("Clave de OpenAI no encontrada. Verifica tu archivo .env")

    # --- INICIO DEL BLOQUE TRY/EXCEPT ---
    try:
        # A. Cargar y Trocear (El trabajo que ya funcionó)
        loader = PyPDFLoader(filepath)
        documentos = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200 
        )
        trozos_de_texto = text_splitter.split_documents(documentos)
        
        # B. Vectorización: Convertir texto en números
        embeddings = OpenAIEmbeddings(openai_api_key=openai_key) # <-- Pasamos la clave directamente

        # C. Almacenamiento: Base de datos FAISS
        db = FAISS.from_documents(trozos_de_texto, embeddings)
        print(f"[INFO] Base de vectores creada con {db.index.ntotal} fragmentos.")
        return db
    
    except Exception as e:
        print(f"[ERROR] Error al crear la base de vectores: {e}")
        # Propagamos la excepción para que el endpoint /upload la gestione
        raise e

# 2. Función que crea el Motor de Chat
def crear_motor_de_chat(db):
    """Crea la cadena de chat que busca en la DB y genera la respuesta."""
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
    
    motor_chat = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=db.as_retriever(),
        return_source_documents=False
    )
    return motor_chat

# 3. Función para chatear
def chatear(pregunta: str, motor_chat, historial_chat):
    """Envía la pregunta al motor de chat."""
    # El historial se pasa como lista de tuplas [(pregunta, respuesta), ...]
    respuesta = motor_chat({"question": pregunta, "chat_history": historial_chat})
    return respuesta['answer']


# --- 4. EJECUCIÓN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
