import streamlit as st

# Título de la aplicación
st.title("Convertidor a Mayúsculas")

# Caja de texto para la entrada del usuario
texto_usuario = st.text_input("Escribe algo aquí:", "")

# Botón para realizar la transformación
if st.button("Convertir"):
    if texto_usuario:
        # Transformar a mayúsculas
        resultado = texto_usuario.upper()
        st.success(f"Texto en mayúsculas: {resultado}")
    else:
        st.warning("Por favor, escribe algo primero.")
