import streamlit as st
from google import genai
import os
import re

# Configuración de la página
st.set_page_config(page_title="Generador de Rimas", page_icon="✍_")
st.title("✍_ Generador de Rimas Asonantes")
st.markdown("Escribe una frase de al menos 4 palabras y la IA seleccionará dinámicamente el modelo más barato y adecuado para generar una segunda frase de longitud similar.")

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
        st.error("Por favor, configura tu GOOGLE_API_KEY en los secretos de Google Colab (icono de la llave en el menú lateral de Colab) para continuar.")
    elif not frase_usuario:
        st.warning("Por favor, escribe una frase primero.")
    else:
        palabras = frase_usuario.split()
        if len(palabras) < 4:
            st.error(f"Tu frase tiene solo {len(palabras)} palabras. Debe tener al menos 4 palabras.")
        else:
            with st.spinner("Descargando y evaluando modelos de Gemini de forma 100% dinámica..."):
                try:
                    client = genai.Client(api_key=google_api_key)

                    # 1. Descargar todos los modelos disponibles desde la API
                    modelos_disponibles = []
                    for m in client.models.list():
                        if 'gemini' in m.name.lower():
                            modelos_disponibles.append(m.name)

                    if not modelos_disponibles:
                        raise Exception("No se encontraron modelos de Gemini disponibles en esta cuenta.")

                    # 2. Filtrar únicamente por la coincidencia estricta de 'flash' y 'lite'
                    modelos_filtrados = [
                        m for m in modelos_disponibles 
                        if 'flash' in m.lower() and 'lite' in m.lower()
                    ]

                    if not modelos_filtrados:
                        raise Exception("No se encontraron modelos que coincidan simultáneamente con 'flash' y 'lite' en tu cuenta.")

                    # 3. Función dinámica para extraer el primer número decimal o entero (versión) del string
                    def extraer_numero_version(nombre):
                        coincidencias = re.findall(r'\d+\.\d+|\d+', nombre)
                        if modificaciones := coincidencias:
                            return float(modificaciones[0])
                        return float('inf')

                    # 4. Ordenar dinámicamente de menor a mayor versión
                    modelos_ordenados = sorted(modelos_filtrados, key=extraer_numero_version)
                    
                    st.info(f"Modelos 'flash-lite' detectados y ordenados: `{modelos_ordenados}`")

                    # 5. Intentar generar rima iterando sobre los modelos de menor versión a mayor para esquivar los obsoletos (404)
                    prompt = (
                        f"El usuario ha escrito la siguiente frase: '{frase_usuario}'.\n"
                        f"Por favor, genera una segunda frase que:\n"
                        f"1. Tenga una longitud similar (aproximadamente {len(palabras)} palabras).\n"
                        f"2. Tenga rima asonante con la frase del usuario.\n"
                        f"3. Tenga sentido y coherencia lógica con la primera.\n"
                        f"Devuelve únicamente la frase generada, sin explicaciones ni comillas.\n"
                    )

                    respuesta_generada = None
                    modelo_exitoso = None
                    
                    for modelo in modelos_ordenados:
                        try:
                            # Probamos el modelo secuencialmente
                            response = client.models.generate_content(
                                model=modelo,
                                contents=prompt,
                            )
                            respuesta_generada = response.text.strip()
                            modelo_exitoso = modelo
                            break  # Si tiene éxito, salimos del bucle
                        except Exception as inner_error:
                            # Ocultar error 404 e intentar con el siguiente modelo de menor versión
                            st.warning(f"El modelo `{modelo}` no pudo ser utilizado (motivo: {inner_error}). Probando la siguiente opción de menor versión...")
                            continue

                    if respuesta_generada and modelo_exitoso:
                        st.success(f"¡Rima generada con éxito usando el modelo activo más económico: `{modelo_exitoso}`!")
                        st.markdown("### Resultado:")
                        st.info(f"**Frase original:** {frase_usuario}")
                        st.success(f"**Frase rimada:** {respuesta_generada}")
                    else:
                        st.error("No se pudo generar la rima con ninguno de los modelos 'flash-lite' disponibles en tu cuenta.")

                except Exception as e:
                    st.error(f"Ocurrió un error en la inicialización: {e}")
