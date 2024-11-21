from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import docx
import openai  # Importa la biblioteca de OpenAI
from dotenv import load_dotenv  # Importa dotenv para gestionar variables de entorno

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Configura la clave API de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder='../frontend/frontend-app/static')
app.secret_key = 'supersecretkey'  # Clave secreta para la sesión

# Configuración de la carpeta de carga
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Almacenamiento de contenido procesado por archivo
processed_files = {}

# Configuración de OpenAI
openai.api_key = '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'

# Datos de ejemplo
usuarios = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "medico", "password": "medico123", "role": "medico"}
]

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para extraer texto de archivos
def extract_text(file_path):
    filename = os.path.basename(file_path)
    file_extension = filename.rsplit('.', 1)[1].lower()
    if file_extension == 'pdf':
        return extract_pdf(file_path)
    elif file_extension == 'docx':
        return extract_docx(file_path)
    elif file_extension == 'txt':
        return extract_txt(file_path)
    return ""

def extract_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_docx(file_path):
    text = ''
    doc = docx.Document(file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def extract_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

@app.route('/')
def serve_frontend():
    if 'username' in session:
        return send_from_directory(app.static_folder, 'login.html')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return send_from_directory(app.static_folder, 'index.html')
    return redirect(url_for('login'))

@app.route('/roles.html')
def serve_roles():
    if 'username' in session:
        return send_from_directory(app.static_folder, 'roles.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in usuarios if u['username'] == username and u['password'] == password), None)
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return 'Invalid credentials', 401
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if next((u for u in usuarios if u['username'] == username), None):
            return 'Username already exists', 400
        usuarios.append({"username": username, "password": password, "role": "user"})
        return redirect(url_for('login'))
    return send_from_directory(app.static_folder, 'register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'file' not in request.files:
        return jsonify({"message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Extraer el contenido del archivo
        content = extract_text(file_path)
        # Guardar el contenido procesado
        processed_files[filename] = content
        return jsonify({"message": f"File {filename} uploaded and processed successfully."})
    return jsonify({"message": "File type not allowed"})

@app.route('/files', methods=['GET'])
def list_files():
    if 'username' not in session:
        return redirect(url_for('login'))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return redirect(url_for('login'))
    data = request.get_json()
    file_name = data.get('file_name')
    query = data.get('query')
    if file_name not in processed_files:
        return jsonify({"message": "File not found or not processed yet"}), 404
    content = processed_files[file_name]

    # Usa la API de OpenAI para responder la consulta
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente que ayuda a responder preguntas basadas en el contenido de un archivo."},
                {"role": "user", "content": f"Contenido del archivo: {content}. Pregunta: {query}"}
            ],
            max_tokens=150
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({"message": "Query response", "response": answer})
    except Exception as e:
        return jsonify({"message": "Error with OpenAI API", "error": str(e)}), 500

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

