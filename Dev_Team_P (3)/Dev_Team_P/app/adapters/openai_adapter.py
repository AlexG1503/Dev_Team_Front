import openai
from app.core import ports


class OpenAIAdapter(ports.LlmPort):
    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        self._client = openai.OpenAI(api_key=api_key)
        # Configura el modelo de OpenAI y sus parámetros
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    # Genera un texto basado en el prompt y el contexto de recuperación
    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                # Define el contexto del sistema para la respuesta
                {"role": "system",
                 "content": f"The context is: {retrieval_context}, please respond to the following question: "},
                # Introduce el prompt del usuario como mensaje
                {"role": "user", "content": prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        # Devolver el contenido generado en la respuesta
        return response.choices[0].message.content
