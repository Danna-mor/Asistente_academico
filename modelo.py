from langchain_groq import ChatGroq
from dotenv import load_dotenv


class ModeloGroq:
    def __init__(self):
        load_dotenv()
        self.modelo = ChatGroq(model="openai/gpt-oss-20b",temperature=0.7)

    def generar_respuesta(self, mensajes):
        respuesta = self.modelo.invoke(mensajes)
        return respuesta
