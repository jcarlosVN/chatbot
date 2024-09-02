#from fastapi import FastAPI
from fasthtml.common import *
from typing import List
from  openai import *
import openai_FC
from dotenv import load_dotenv

# Configuración del cliente OpenAI
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Configuración de la app con daisyui y tailwind para el componente del chat
hdrs = (picolink, Script(src="https://cdn.tailwindcss.com"),
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"))
app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto")

# Componente de mensaje de chat (renderiza una burbuja de chat)
def ChatMessage(msg, user):
    bubble_class = "chat-bubble-primary" if user else 'chat-bubble-secondary'
    chat_class = "chat-end" if user else 'chat-start'
    return Div(cls=f"chat {chat_class}")(
               Div('user' if user else 'assistant', cls="chat-header"),
               Div(msg, cls=f"chat-bubble {bubble_class}"),
               Hidden(msg, name="messages")
           )

# Campo de entrada para el mensaje del usuario, también se usa para limpiar el campo de entrada después de enviar un mensaje
def ChatInput():
    return Input(name='msg', id='msg-input', placeholder="a veeer tu mensaje...",
                 cls="input input-bordered w-full", hx_swap_oob='true')

# Ruta para favicon.ico para evitar error 404
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(content="", media_type="image/x-icon")

# Pantalla principal
@app.get
def index():
    page = Form(hx_post="/send", hx_target="#chatlist", hx_swap="beforeend")(
           Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
           Div(cls="flex space-x-2 mt-2")(Group(ChatInput(), Button("Send", cls="btn btn-primary")))
           )
    return Titled('Chatbot Demo', page)

# Manejar el envío del formulario
@app.post("/send")
def send(msg:str, messages:List[str]=None):
    if not messages: 
        messages = []
    messages.append(msg.rstrip())

    # Utilizando la configuración y funciones del archivo openai_FC.py
    assistant_id = openai_FC.assistant_id  # ID del asistente predefinido
    thread_id = openai_FC.thread_id  # ID del hilo predefinido
    
    # Recuperar el asistente y el hilo
    assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.retrieve(thread_id)

    # Ejecutar mensajes en el hilo con el asistente
    new_message = openai_FC.run_messages(thread, assistant, msg)
    
    return (ChatMessage(msg, True),    # Mensaje del usuario
            ChatMessage(new_message.rstrip(), False), # Respuesta del chatbot
            ChatInput()) # Limpiar el campo de entrada con un OOB swap

# Servir la aplicación
serve(port=5002, host="127.0.0.1")