import os
from fastapi import UploadFile
from app.core.models import Document
from app.core import ports
from app.helpers.strategies_poc import FileReader


class RAGService:
    def __init__(self, db: ports.DatabasePort, document_repo: ports.DocumentRepositoryPort,
                 openai_adapter: ports.LlmPort) -> None:
        self.db = db
        self.document_repo = document_repo
        self.openai_adapter = openai_adapter

    # Genera una respuesta utilizando documentos relevantes para la consulta
    def generate_answer(self, query: str) -> str:
        documents = self.document_repo.get_documents(query, self.openai_adapter)
        print(f"Documents: {documents}")

        # Combina el contenido de los documentos para formar el contexto
        context = " ".join([doc.content for doc in documents])

        # Genera el texto de respuesta usando el contexto obtenido
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)

    # Guarda un archivo subido y procesa su contenido
    def save_document(self, file: UploadFile) -> None:
        # Obtiene el nombre del archivo subido
        file_name = file.filename

        # Crea la carpeta 'media' si no existe
        os.makedirs('media', exist_ok=True)

        # Guarda el archivo en la carpeta 'media'
        file_path = os.path.join('media', file_name)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        # Crea un modelo de documento con los valores iniciales
        document = Document(nombre=file_name, ruta=file_path)

        # Lee el contenido del documento utilizando el lector adecuado según el tipo de archivo
        content = FileReader(document.ruta).read_file()
        print(document,content)

        # Guarda la información del documento en la base de datos (MongoDB)
        self.db.save_document(document)

        # Realiza el embedding del contenido, lo divide en fragmentos y lo guarda en ChromaDB
        self.document_repo.save_document(document, content, self.openai_adapter)

    # Registra un nuevo usuario en la base de datos
    def sing_up(self, username: str, password: str) -> None:
        self.db.save_user(username, password)

    # Obtiene un documento desde la base de datos usando su ID
    def get_document(self, document_id: str) -> Document:
        return self.db.get_document(document_id)

    # Obtiene los vectores almacenados en el repositorio de documentos
    def get_vectors(self):
        return self.document_repo.get_vectors()
