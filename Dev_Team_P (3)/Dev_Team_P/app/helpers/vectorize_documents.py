import tiktoken

# Obtiene los embeddings de OpenAI para un texto específico
def get_openai_embeddings(text: str, openai_client) -> list[float]:
    response = openai_client._client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding  # Devuelve la lista de embeddings como flotantes

# Convierte el contenido de un documento en vectores de embeddings utilizando OpenAI
def document_to_vectors(content: str, openai_client) -> list[list[float]]:
    chunks = chunk_text(content, max_tokens=2048)  # Divide el contenido en fragmentos
    content_vectors = [get_openai_embeddings(chunk, openai_client) for chunk in chunks]
    return content_vectors  # Devuelve una lista de listas de embeddings

# Divide un texto largo en fragmentos más pequeños basados en la cantidad de tokens permitidos
def chunk_text(text: str, max_tokens: int) -> list[str]:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    # Divide el texto en fragmentos con un máximo de max_tokens tokens por fragmento
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    chunk_texts = [tokenizer.decode(chunk) for chunk in chunks]  # Decodifica los fragmentos a texto
    return chunk_texts
