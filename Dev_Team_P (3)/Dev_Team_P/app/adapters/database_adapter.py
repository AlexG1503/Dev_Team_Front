from app.core import ports, models
from pymongo import MongoClient
from app.core.models import Document


class MongoDbAdapter(ports.DatabasePort):
    def __init__(self, url: str = "mongodb://some-m:27017") -> None:
        self.client = MongoClient(url)
        self.db = self.client["rag_db"]
        self.users = self.db["users"]
        self.documents = self.db["documents"]


    # Insertar un nuevo usuario en la base de datos
    def save_user(self, username: str, password: str) -> None:
        self.users.insert_one({"username": username, "password": password})

    # Recuperar un usuario a partir de su nombre de usuario
    def get_user(self, username: str) -> models.User:
        user = self.users.find_one({"username": username})
        return models.User(username=user["username"], password=user["password"])

    # Insertar un nuevo documento en la base de datos
    def save_document(self, document: models.Document) -> None:
        self.documents.insert_one({"document_id": document.document_id, "nombre": document.nombre, "ruta": document.ruta})

    # Recuperar un documento utilizando su ID
    def get_document(self, document_id: str) -> Document | None:
        document = self.documents.find_one({"document_id": document_id})
        if document:
            return models.Document(document_id=document["document_id"], nombre=document["nombre"], ruta=document["ruta"])
        return None
