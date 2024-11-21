import pydantic
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from app import usecases
from app.api import dependencies


rag_router = APIRouter()

@rag_router.post("/save-document/")
def save_document(file: UploadFile = File(...),
                  rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Guarda el archivo recibido en MongoDB
    rag_service.save_document(file)
    return {"status": "Document saved successfully"}

@rag_router.get("/generate-answer/")
def generate_answer(query: str,
                    rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Genera una respuesta basada en la consulta proporcionada
    return rag_service.generate_answer(query)

@rag_router.get("/get-document/")
def get_document(document_id: str,
                 rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Obtiene un documento a partir de su ID
    document = rag_service.get_document(document_id)
    if document:
        return document
    return {"status": "Document not found"}

@rag_router.post("/sing-up/")
def sing_up(username: str, password: str,
            rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Registra un nuevo usuario en el sistema
    rag_service.sing_up(username, password)
    return {"status": "User created successfully"}

@rag_router.get("/get-vectors/")
async def get_vectors(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Devuelve los vectores almacenados
    return rag_service.get_vectors()


@rag_router.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de RG"}
