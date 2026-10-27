
import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage
from main import conectar_vectorstore, responder_preguntas


# ============================================================
# 1. CONFIGURACIÓN DE LA INTERFAZ
# ============================================================

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CONEXIÓN CON EL MOTOR RAG
# ============================================================

@st.cache_resource
def cargar_vectorstore():
    """Conecta con Neon y reutiliza el vectorstore entre ejecuciones."""

    return conectar_vectorstore()


# ============================================================
# 3. MEMORIA Y ESTADO DE LA CONVERSACIÓN
# ============================================================

def inicializar_chat():
    """Prepara los mensajes y el historial de la conversación."""

    # session_state mantiene los datos aunque Streamlit recargue el script.
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if "historial" not in st.session_state:
        st.session_state.historial = []


def nueva_conversacion():
    """Borra el chat visible y la memoria conversacional."""

    # Limpiamos ambas listas para evitar referencias a conversaciones anteriores.
    st.session_state.mensajes = []
    st.session_state.historial = []


inicializar_chat()


# ============================================================
# 4. BARRA LATERAL
# ============================================================

with st.sidebar:

    st.title("📚 DocuMind AI")
    st.caption("NovaTech Solutions")

    st.divider()

    # on_click ejecuta la función al pulsar el botón.
    st.button(
        "➕ Nueva conversación",
        use_container_width=True,
        on_click=nueva_conversacion
    )

    st.subheader("📂 Documentación disponible")

    st.markdown("""
    - 📄 Política de RR. HH.
    - 💻 Equipos informáticos
    - 🔐 Seguridad informática
    - 📋 Normativa interna
    """)

    st.divider()

    st.subheader("⚙️ Tecnologías")

    st.caption("Llama 3.1 · Ollama")
    st.caption("LangChain · PostgreSQL · pgvector")
    st.caption("Streamlit")


# ============================================================
# 5. CABECERA Y MENSAJE DE BIENVENIDA
# ============================================================

st.title("💬 Asistente documental")
st.caption(
    "Consulta la documentación interna de NovaTech Solutions "
    "mediante inteligencia artificial."
)

st.divider()

# Mostramos la bienvenida únicamente si todavía no hay mensajes.
if not st.session_state.mensajes:

    st.info(
        "👋 ¡Bienvenido a DocuMind AI! "
        "Puedes preguntarme sobre vacaciones, equipos informáticos, "
        "seguridad y normativa interna."
    )

    st.markdown("**💡 Algunas preguntas que puedes hacer:**")

    # Las columnas organizan los ejemplos horizontalmente.
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("• ¿Cuántos días de vacaciones tenemos?")
        st.markdown("• ¿Cómo solicito material informático?")

    with col2:
        st.markdown("• ¿Qué normas de seguridad debo seguir?")
        st.markdown("• ¿Cómo se reservan las salas de reuniones?")


# ============================================================
# 6. MOSTRAR EL HISTORIAL DEL CHAT
# ============================================================

for mensaje in st.session_state.mensajes:

    # chat_message crea una burbuja según el rol del mensaje.
    with st.chat_message(mensaje["rol"]):

        st.markdown(mensaje["contenido"])

        # get() comprueba si existen fuentes sin provocar errores.
        if mensaje.get("fuentes"):

            with st.expander("📄 Fuentes citadas"):

                for fuente in mensaje["fuentes"]:
                    st.write(f"• {fuente}")


# ============================================================
# 7. PROCESAR NUEVAS PREGUNTAS
# ============================================================

# chat_input crea el campo de texto fijo en la parte inferior.
pregunta = st.chat_input("Pregunta sobre los documentos...")

if pregunta:

    # Guardamos el mensaje del usuario para conservarlo en pantalla.
    st.session_state.mensajes.append({
        "rol": "user",
        "contenido": pregunta
    })

    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):

        # spinner indica que el asistente está procesando la consulta.
        with st.spinner("Consultando documentos..."):

            vectorstore = cargar_vectorstore()

            respuesta, fuentes = responder_preguntas(
                vectorstore,
                pregunta,
                st.session_state.historial
            )

        st.markdown(respuesta)

        if fuentes:

            with st.expander("📄 Fuentes citadas"):

                for fuente in fuentes:
                    st.write(f"• {fuente}")

    # Guardamos la respuesta y sus fuentes en el historial visual.
    st.session_state.mensajes.append({
        "rol": "assistant",
        "contenido": respuesta,
        "fuentes": fuentes
    })

    # Añadimos el intercambio a la memoria utilizada por LangChain.
    st.session_state.historial.append(HumanMessage(content=pregunta))
    st.session_state.historial.append(AIMessage(content=respuesta))