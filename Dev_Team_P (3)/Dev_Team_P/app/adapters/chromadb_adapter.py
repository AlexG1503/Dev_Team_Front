import chromadb
import numpy as np
from typing import List
from app.core import ports
from app.core import models
from app.helpers.vectorize_documents import document_to_vectors, get_openai_embeddings


class ChromaDBAdapter(ports.DocumentRepositoryPort):
    def __init__(self, number_of_vectorial_results: int) -> None:
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("documents")
        self._number_of_vectorial_results = number_of_vectorial_results

    # Inserta un documento y genera embeddings utilizando OpenAI
    def save_document(self, document: models.Document, content: str, openai_client) -> None:
        embeddings_document = document_to_vectors(content, openai_client)

        # Si el documento tiene varios embeddings, se combinan promediando
        if len(embeddings_document) > 1:
            combined_embedding = np.mean(embeddings_document, axis=0).tolist()
        else:
            combined_embedding = embeddings_document[0]

        # Añade el documento a la colección en ChromaDB con su respectivo embedding
        self.collection.add(
            ids=[document.document_id],
            embeddings=[combined_embedding],  # Se asegura que sea una lista de embeddings
            documents=[content]
        )

    # Recupera documentos a partir de los embeddings generados por la consulta
    def get_documents(self, query: str, openai_client, n_results: int | None = None) -> List[models.Document]:
        if not n_results:
            n_results = self._number_of_vectorial_results

        # Genera un embedding para la consulta mediante OpenAI
        query_embedding = get_openai_embeddings(query, openai_client)

        # Realiza la búsqueda en la base de datos usando el embedding de la consulta
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

        # Procesa los resultados obtenidos y devuelve una lista de documentos
        documents = []
        for i, doc_id_list in enumerate(results['ids']):
            for doc_id in doc_id_list:
                documents.append(models.Document(id=doc_id, content=results['documents'][i][0]))
        return documents

    # Obtiene los vectores almacenados en la colección
    def get_vectors(self):
        data = self.collection.get(include=['embeddings', 'documents'])

        data_formateada = {
            'ids': data.get('ids', []),
            'embeddings': data.get('embeddings', []).tolist() if data.get('embeddings') is not None else None,  # Convierte a lista si es un array
            'documents': data.get('documents', []),
        }

        return data_formateada
