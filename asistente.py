from modelo import ModeloGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    message_to_dict,
    messages_from_dict
)
from pathlib import Path
import json


class AsistenteAcademico:

    def __init__(self):

        self.modelo = ModeloGroq()
        self.archivo = Path(__file__).parent / "historial.json"
        self.max_mensajes = 6
        self.especialidad = self.seleccionar_especialidad()
        self.mensaje_sistema = self.crear_mensaje_sistema()
        self.historial = self.cargar_historial()

    def seleccionar_especialidad(self):

        print("\n=== SELECCIONA UNA ESPECIALIDAD ===")
        print("1. Tutor de Programacion")
        print("2. Tutor de Inteligencia Artificial")
        print("3. Tutor de Bases de Datos")

        while True:

            opcion = input("\nSelecciona una opcion: ").strip()

            if opcion == "1":
                return "Programacion"
            elif opcion == "2":
                return "Inteligencia Artificial"
            elif opcion == "3":
                return "Bases de Datos"
            else:
                print("Opcion incorrecta. Intenta nuevamente.")

    def crear_mensaje_sistema(self):

        instrucciones = {

            "Programacion": """
            Eres un tutor universitario especializado en Programacion.

            Responde siempre en español.
            Utiliza lenguaje sencillo y claro.
            Explica los conceptos de programacion paso a paso.
            Incluye ejemplos de codigo cuando sea conveniente.
            Ayuda al estudiante a comprender los temas.
            Si desconoces una respuesta, reconócelo.
            """,

            "Inteligencia Artificial": """
            Eres un tutor universitario especializado en Inteligencia Artificial.

            Responde siempre en español.
            Utiliza lenguaje sencillo y claro.
            Explica los conceptos de inteligencia artificial paso a paso.
            Incluye ejemplos cuando sea conveniente.
            Ayuda al estudiante a comprender los temas.
            Si desconoces una respuesta, reconócelo.
            """,

            "Bases de Datos": """
            Eres un tutor universitario especializado en Bases de Datos.

            Responde siempre en español.
            Utiliza lenguaje sencillo y claro.
            Explica los conceptos de bases de datos paso a paso.
            Incluye ejemplos cuando sea conveniente.
            Ayuda al estudiante a comprender los temas.
            Si desconoces una respuesta, reconócelo.
            """

        }

        return SystemMessage(
            content=instrucciones[self.especialidad]
        )

    
    def generar_respuesta(self, pregunta):

        self.historial.append(
            HumanMessage(content=pregunta)
        )

        try:
            mensajes = self.ventana_contexto()
            respuesta = self.modelo.generar_respuesta(mensajes)
            if respuesta is None:
                print("La IA no genero una respuesta.")
                self.historial.pop()
                return

        except Exception as error:
            self.historial.pop()
            print("\nError al consultar el modelo:")
            print(error)
            return

        print("\nIA:", respuesta.content)
        self.historial.append(respuesta)
        self.guardar_historial()


    def ventana_contexto(self):

        conversacion = [
            mensaje for mensaje in self.historial
            if not isinstance(mensaje, SystemMessage)
            ]

        return [
            self.mensaje_sistema
            ] + conversacion[-self.max_mensajes:]

    # CARGAR HISTORIAL

    def cargar_historial(self):

        if self.archivo.exists():

            try:

                with open(
                    self.archivo,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    datos = json.load(archivo)

                historial = messages_from_dict(datos)

                #conservar los mensajes pero nuevas instrucciones

                historial = [
                    mensaje for mensaje in historial
                    if not isinstance(mensaje, SystemMessage)
                ]

                historial.insert(0, self.mensaje_sistema)
                print("Historial recuperado desde JSON.")
                return historial

            except (json.JSONDecodeError, KeyError, ValueError, TypeError):

                print("Historial dañado. Se iniciara uno nuevo.")
        print("Iniciando una nueva conversacion.")
        return [self.mensaje_sistema]

    # GUARDAR HISTORIAL

    def guardar_historial(self):

        datos = [
            message_to_dict(mensaje)
            for mensaje in self.historial
        ]

        temporal = self.archivo.with_suffix(".tmp")

        with open(
            temporal,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=4
            )
        temporal.replace(self.archivo)

    def nueva_conversacion(self):
        self.historial = [
            self.mensaje_sistema
        ]
        self.guardar_historial()
        print("\nSe inicio una nueva conversacion.")
        print("El historial anterior fue eliminado.")

    def mostrar_historial(self):
        print("=====================================================================================================================================")
        print("=== HISTORIAL DE CONVERSACION ===")

        if len(self.historial) == 1:
            print("No hay mensajes en la conversacion.")
            return

        for mensaje in self.historial:
            if isinstance(mensaje, SystemMessage):
                continue
            elif isinstance(mensaje, HumanMessage):
                print("=====================================================================================================================================")
                print("\nUsuario:", mensaje.content)
            elif isinstance(mensaje, AIMessage):
                print("\nIA:", mensaje.content)

    # CONVERSAR

    def conversar(self):
        print("\n=== ASISTENTE ACADEMICO ===")
        print("Especialidad:", self.especialidad)

        print("\nComandos disponibles:")
        print("nuevo - Iniciar una nueva conversacion")
        print("historial - Mostrar los mensajes")
        print("salir - Terminar el programa")

        while True:

            pregunta = input("\nUsuario: ").strip()
            if pregunta.lower() == "salir":
                print("Conversacion finalizada.")
                break
            elif pregunta.lower() == "nuevo":
                self.nueva_conversacion()
                continue
            elif pregunta.lower() == "historial":
                self.mostrar_historial()
                continue
            if not pregunta:
                continue
            self.generar_respuesta(pregunta)
