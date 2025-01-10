def format_content(content):
    """
    Formatea el contenido para mejorar su presentación.
    - Detecta párrafos y los envuelve en <p>.
    - Detecta enlaces y los convierte en clickables.
    - Detecta listas y las formatea como <ul> y <li>.
    - Resalta títulos con un estilo especial.
    """
    formatted_content = ""
    lines = content.split("\n")  # Dividir el contenido en líneas

    in_list = False  # Para controlar si estamos dentro de una lista

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Ignorar líneas vacías

        # Detectar títulos (líneas que terminan con ":")
        if line.endswith(":"):
            formatted_content += f'<h3 class="text-xl font-bold mb-2">{line}</h3>'
            continue

        # Detectar listas (líneas que comienzan con "-")
        if line.startswith("-"):
            if not in_list:
                formatted_content += '<ul class="list-disc list-inside mb-4">'
                in_list = True
            formatted_content += f'<li class="text-gray-700">{line[1:].strip()}</li>'
            continue
        else:
            if in_list:
                formatted_content += '</ul>'
                in_list = False

        # Detectar enlaces (líneas que contienen "http://" o "https://")
        if "http://" in line or "https://" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("http://") or part.startswith("https://"):
                    formatted_content += f'<a href="{part}" class="text-blue-500 hover:underline" target="_blank">{part}</a> '
                else:
                    formatted_content += f'{part} '
            formatted_content += '<br>'
            continue

        # Formatear como párrafo
        formatted_content += f'<p class="text-black mb-2">{line}</p>'

    # Cerrar la lista si aún está abierta
    if in_list:
        formatted_content += '</ul>'

    return formatted_content