#Tutor de IA (RAG) para Apuntes Universitarios

## Objetivo del Proyecto
Este proyecto fue desarrollado para demostrar la implementación de un flujo completo de RAG (Retrieval-Augmented Generation), permitiendo a los usuarios interactuar y hacer preguntas contextualizadas sobre documentos PDF subidos.

## ⚙️ Arquitectura Técnica (Stacks)
* **Backend / API:** Python 3.12, Flask (Servidor REST).
* **Inteligencia Artificial (RAG):** LangChain (Core), OpenAI Embeddings (Vectorización), FAISS (Base de Vectores en memoria) y GPT-3.5-turbo (Generación de Chat).
* **Gestión del Proyecto:** Git y GitHub Kanban Board (demostración de metodología Ágil).

## Cómo Poner en Marcha el Proyecto (Setup)

### 1. Requisitos
* Tener **Python 3.12** instalado.
* Tener una **API Key de OpenAI** con saldo activo (sino generará error por saldo insuficiente)

### 2. Configuración del Entorno
1.  Clonar el repositorio:
    ```bash
    git clone [https://github.com/uahroberto/tutor-ia-uah.git](https://github.com/uahroberto/tutor-ia-uah.git)
    cd tutor-ia-uah
    ```
2.  Crear y activar el entorno virtual:
    ```bash
    python3.12 -m venv venv-312
    source venv-312/bin/activate
    ```
3.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
    *(Nota: Crea un archivo `requirements.txt` con `pip freeze > requirements.txt`)*.

### 3. Configuración de Claves
Crea un archivo llamado `.env` en la raíz del proyecto con tu clave secreta: OPENAI_API_KEY="sk-Insertar-Clave-Secreta-Aqui"

### 4. Ejecución
1.  Arrancar el servidor:
    ```bash
    python app.py
    ```
2.  Abrir otra terminal y subir el PDF:
    ```bash
    curl -X POST -F "file=@uploads/documento.pdf" [http://127.0.0.1:5000/upload](http://127.0.0.1:5000/upload)
    ```
3.  Chatear con el documento:
    ```bash
    curl -X POST [http://127.0.0.1:5000/chat](http://127.0.0.1:5000/chat) -H "Content-Type: application/json" -d '{"question": "¿Cuál es la conclusión principal?"}'
    ```
