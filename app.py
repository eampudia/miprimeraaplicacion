import streamlit as st
from google import genai
import os
import re

# Configuración de la página
st.set_page_config(page_title="Generador de Rimas", page_icon="✍_")
st.title("✍_ Generador de Rimas Consonantes")

# Intentar obtener la API Key de varias fuentes seguras en segundo plano
google_api_key = ""

try:
    from google.colab import userdata
    google_api_key = userdata.get("GOOGLE_API_KEY")
except Exception:
    pass

if not google_api_key:
    google_api_key = os.environ.get("GOOGLE_API_KEY", "")

# Entrada de la frase por parte del usuario
frase_usuario = st.text_input("Introduce tu frase inicial (mínimo 4 palabras):", "")

if st.button("Generar Rima"):
    if not google_api_key:
        st.error("Por favor, configura tu GOOGLE_API_KEY en los secretos de Google Colab.")
    elif not frase_usuario:
        st.warning("Por favor, escribe una frase primero.")
    else:
        palabras = frase_usuario.split()
        if len(palabras) < 4:
            st.error(f"Tu frase tiene solo {len(palabras)} palabras. Debe tener al menos 4 palabras.")
        else:
            with st.spinner("Generando..."):
                try:
                    client = genai.Client(api_key=google_api_key)

                    # 1. Descargar todos los modelos disponibles desde la API
                    modelos_disponibles = []
                    for m in client.models.list():
                        if 'gemini' in m.name.lower():
                            modelos_disponibles.append(m.name)

                    if not modelos_disponibles:
                        st.error("No se encontraron modelos de Gemini disponibles en esta cuenta.")
                        st.stop()

                    # 2. Filtrar únicamente por la coincidencia estricta de 'flash' y 'lite'
                    modelos_filtrados = [
                        m for m in modelos_disponibles 
                        if 'flash' in m.lower() and 'lite' in m.lower()
                    ]

                    if not modelos_filtrados:
                        st.error("No se encontraron modelos que coincidan con 'flash' y 'lite' en tu cuenta.")
                        st.stop()

                    # 3. Función dinámica para extraer la versión numérica del string
                    def extraer_numero_version(nombre):
                        coincidencias = re.findall(r'\d+\.\d+|\d+', nombre)
                        if  coincidencias:
                            return float(coincidencias[0])
                        return float('inf')

                    # 4. Ordenar dinámicamente de menor a mayor versión
                    modelos_ordenados = sorted(modelos_filtrados, key=extraer_numero_version)

                    # 5. Intentar generar rima iterando de manera silenciosa
                    prompt = (
                        f"El usuario ha escrito la siguiente frase: '{frase_usuario}'.\n"
                        f"Por favor, genera una segunda frase que:\n"
                        f"1. Tenga una longitud similar (aproximadamente {len(palabras)} palabras).\n"
                        f"2. Tenga rima CONSONANTE en la última palabra con respecto a la última palabra de la frase del usuario (las vocales y consonantes a partir de la última vocal acentuada deben coincidir exactamente).\n"
                        f"3. Tenga sentido y coherencia lógica con la primera.\n"
                        f"Devuelve únicamente la frase generada de respuesta, sin explicaciones, sin comentarios ni comillas.\n"
                    )

                    respuesta_generada = None
                    
                    for modelo in modelos_ordenados:
                        try:
                            # Probamos el modelo de manera silenciosa
                            response = client.models.generate_content(
                                model=modelo,
                                contents=prompt,
                            )
                            respuesta_generada = response.text.strip()
                            if respuesta_generada:
                                break
                        except Exception:
                            # Ignorar silenciosamente errores 404 u otros para probar la siguiente opción
                            continue

                    if respuesta_generada:
                        # Limpiar comillas extras si las hubiera
                        respuesta_generada = respuesta_generada.replace('"', '').replace("'", "")
                        st.markdown(f"###  {frase_usuario}")
                        st.markdown(f"###  {respuesta_generada}")
                    else:
                        st.error("No se pudo generar la rima con ningún modelo disponible.")

                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")
