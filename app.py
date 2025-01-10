from flask import Flask, request, render_template_string
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel
from dotenv import load_dotenv
import os
from flask import redirect


# Importar la función format_content desde formatters.py
from formatters import format_content

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración del agente
hf_token = os.getenv("HF_TOKEN")
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel(token=hf_token))

# Crear la aplicación Flask
app = Flask(__name__)

# Variable global para almacenar el historial de la conversación
conversation_history = []

# Límite máximo de entradas en el historial
MAX_HISTORY_LENGTH = 20

# Plantilla HTML con Tailwind CSS
HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Interactivo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        #chat-history {
            scrollbar-width: thin;
            scrollbar-color: #4a5568 #cbd5e0;
        }
        #chat-history::-webkit-scrollbar {
            width: 8px;
        }
        #chat-history::-webkit-scrollbar-thumb {
            background-color: #4a5568;
            border-radius: 4px;
        }
        #chat-history::-webkit-scrollbar-track {
            background-color: #cbd5e0;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="flex flex-col h-screen">
        <!-- Cabecera -->
<div class="bg-white shadow-md p-4 flex justify-between items-center">
    <h1 class="text-2xl font-bold text-center">Chat Interactivo</h1>
    <form method="POST" action="/clear-history">
        <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600">
            Limpiar historial
        </button>
    </form>
</div>

        <!-- Historial de la conversación -->
        <div id="chat-history" class="flex-1 overflow-y-auto p-6 space-y-4">
            {% for entry in history %}
                <div class="flex {% if entry.role == 'Usuario' %}justify-end{% else %}justify-start{% endif %}">
                    <div class="{% if entry.role == 'Usuario' %}bg-blue-500 text-white{% else %}bg-gray-200 text-black{% endif %} rounded-lg p-3 max-w-2xl">
                        <strong>{{ entry.role }}:</strong> 
                        <div class="mt-1">
                            {{ format_content(entry.content)|safe }}
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <!-- Formulario para enviar preguntas -->
        <div class="bg-white shadow-lg p-4">
            <form method="POST" class="flex space-x-2">
                <input type="text" name="question" placeholder="Escribe tu pregunta aquí..." 
                    class="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">
                    Enviar
                </button>
            </form>
        </div>
    </div>

    <!-- Script para mantener el scroll al final del historial -->
    <script>
        const chatHistory = document.getElementById('chat-history');
        chatHistory.scrollTop = chatHistory.scrollHeight;
    </script>
    <!-- Script para manejar la limpieza del historial -->
<script>
    function clearHistory() {
        fetch('/clear-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (response.ok) {
                // Limpiar el historial en la interfaz
                const chatHistory = document.getElementById('chat-history');
                chatHistory.innerHTML = '';
            } else {
                console.error('Error al limpiar el historial');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
</script>
</body>
</html>
'''


@app.route('/clear-history', methods=['POST'])
def clear_history():
    global conversation_history
    conversation_history = []  # Limpiar el historial
    return redirect('/')  # Redirigir a la página principal


def build_context(history):
    """
    Construye el contexto de la conversación a partir del historial.
    """
    context = ""
    for entry in history:
        context += f"{entry['role']}: {entry['content']}\n"
    return context


@app.route('/', methods=['GET', 'POST'])
def index():
    global conversation_history
    answer = None

    if request.method == 'POST':
        question = request.form['question']

        # Agregar la pregunta al historial
        conversation_history.append({"role": "Usuario", "content": question})

        # Limitar el historial a un máximo de entradas
        if len(conversation_history) > MAX_HISTORY_LENGTH:
            conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]

        # Construir el contexto de la conversación
        context = build_context(conversation_history)

        # Ejecutar la pregunta con el historial como contexto
        full_query = f"{context}\nAgente: Responde en español. {question}"
        answer = agent.run(full_query)

        # Agregar la respuesta al historial
        conversation_history.append({"role": "Agente", "content": answer})

        # Limitar el historial nuevamente (por si acaso)
        if len(conversation_history) > MAX_HISTORY_LENGTH:
            conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]

    return render_template_string(HTML, answer=answer, history=conversation_history, format_content=format_content)


if __name__ == '__main__':
    app.run(debug=True)
