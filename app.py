
import streamlit as st
from google import genai
import os

# Configuración de la página
st.set_page_config(page_title="Generador de Rimas", page_icon="✍️")
st.title("✍️ Generador de Rimas Asonantes")
st.markdown("Escribe una frase de al menos 4 palabras y la IA generará una segunda frase de longitud similar, con rima asonante y con sentido.")

# Intentar obtener la API Key de varias fuentes seguras
google_api_key = ""

# 1. Intentar obtener desde Google Colab Userdata (si se ejecuta en el notebook)
try:
    from google.colab import userdata
    google_api_key = userdata.get("GOOGLE_API_KEY")
except Exception:
    pass

# 2. Si no está en Colab, intentar obtener de variables de entorno o st.secrets
if not google_api_key:
    google_api_key = os.environ.get("GOOGLE_API_KEY", "")

# 3. Si sigue sin configurarse, permitir introducirla manualmente en la barra lateral
if not google_api_key:
    with st.sidebar:
        st.subheader("Configuración")
        google_api_key = st.text_input("Introduce tu Google API Key:", type="password")
        st.markdown("[¿Cómo obtener una API Key?](https://aistudio.google.com/)")

# Entrada de la frase por parte del usuario
frase_usuario = st.text_input("Introduce tu frase inicial (mínimo 4 palabras):", "")

if st.button("Generar Rima"):
    if not google_api_key:
        st.error("Por favor, introduce tu Google API Key para continuar.")
    elif not frase_usuario:
        st.warning("Por favor, escribe una frase primero.")
    else:
        # Validar la longitud de la frase
        palabras = frase_usuario.split()
        if len(palabras) < 4:
            st.error(f"Tu frase tiene solo {len(palabras)} palabras. Debe tener al menos 4 palabras.")
        else:
            with st.spinner("Generando rima perfecta..."):
                try:
                    # Inicializar el cliente de Gemini utilizando la nueva librería google-genai
                    client = genai.Client(api_key=google_api_key)
                    
                    prompt = (
                        f"El usuario ha escrito la siguiente frase: '{frase_usuario}'.\n"
                        f"Por favor, genera una segunda frase que:\n"
                        f"1. Tenga una longitud similar (aproximadamente {len(palabras)} palabras).\n"
                        f"2. Tenga rima asonante con la frase del usuario.\n"
                        f"3. Tenga sentido y coherencia lógica con la primera.\n"
                        f"Devuelve únicamente la frase generada, sin explicaciones ni comillas."
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    
                    frase_generada = response.text.strip()
                    
                    # Mostrar el resultado de manera atractiva
                    st.success("¡Rima generada con éxito!")
                    st.markdown("### Resultado:")
                    st.info(f"**Frase original:** {frase_usuario}")
                    st.success(f"**Frase rimada:** {frase_generada}")
                    
                except Exception as e:
                    st.error(f"Ocurrió un error al conectar con Gemini: {e}")
