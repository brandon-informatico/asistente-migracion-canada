import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.document_loaders import (
    CSVLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    DirectoryLoader
)
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from herramientas import crear_herramientas

load_dotenv()

st.set_page_config(page_title="Asistente de Migración a Canadá 🇨🇦", page_icon="🍁", layout="centered")
st.title("🇨🇦 Asistente de IA para Migración a Canadá")

st.info("""
¡Bienvenido al Asistente de Migración a Canadá! 🍁
Este sistema ya contiene toda la base de conocimiento oficial sobre Express Entry, Visas de Trabajo (T-MEC), Permisos de Estudio y Programas Provinciales para mexicanos.

**¿Qué puedes hacer?**
1. **Chatear directamente:** Haz cualquier pregunta sobre cómo migrar.
2. **Subir archivos adicionales:** Puedes subir tu CV (PDF/Word) para que el agente lo evalúe, o subir tablas de datos (CSV/Excel) para generar gráficas.
""")

# --- CONFIGURACIÓN DE API KEY ---
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    with st.sidebar:
        google_api_key = st.text_input("Ingresa tu GOOGLE_API_KEY:", type="password")
if not google_api_key:
    st.warning("⚠️ Ingresa tu `GOOGLE_API_KEY` para iniciar el sistema.")
    st.stop()

# --- PRE-CARGA DE CONOCIMIENTO (AUTOMÁTICA) ---
DATA_DIR = "data_docs"

def inicializar_base_conocimiento():
    """Genera la guía predeterminada si no existe y carga FAISS en memoria."""
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta_guia = os.path.join(DATA_DIR, "Guia_Migracion.md")
    
    # Si no existe la guía, la creamos automáticamente
    if not os.path.exists(ruta_guia):
        contenido_base = """# 🇨🇦 Guía Completa de Migración a Canadá para Mexicanos
        ## 1. Vías Principales de Migración
        * **Express Entry:** Sistema federal basado en puntos (CRS). Incluye el Federal Skilled Worker Program (FSWP) y el Canadian Experience Class (CEC).
        * **Tratado CUSMA / T-MEC:** Permite a profesionistas mexicanos trabajar en Canadá sin necesidad de LMIA si tienen una oferta de empleo.
        * **Estudios (PGWP):** Estudiar en una DLI canadiense permite obtener un Post-Graduation Work Permit para trabajar legalmente y acumular experiencia.
        * **Nominación Provincial (PNP):** Las provincias eligen candidatos y les otorgan 600 puntos extra en Express Entry.
        
        ## 2. Requisitos Generales
        * **ECA:** Evaluación de Credenciales Educativas (validar título mexicano, ej. WES).
        * **Idioma:** Inglés (IELTS General o CELPIP) o Francés (TEF/TCF Canadá). Se mide en niveles CLB.
        * **Fondos (Proof of Funds):** Demostrar aprox. $14,000 - $15,000 CAD por persona sola (excepto CEC).
        * **Experiencia:** Cartas de referencia laboral y nóminas que respalden la experiencia.
        """
        with open(ruta_guia, "w", encoding="utf-8") as f:
            f.write(contenido_base)

    # Cargar documentos y crear VectorStore solo si no está en sesión
    if "vectorstore" not in st.session_state:
        with st.spinner("Cargando conocimientos oficiales de migración..."):
            loader = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            splits = text_splitter.split_documents(docs)
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=google_api_key)
            st.session_state["vectorstore"] = FAISS.from_documents(splits, embeddings)

inicializar_base_conocimiento()

# --- GESTIÓN DE ARCHIVOS DEL USUARIO (OPCIONAL) ---
st.markdown("### 📂 Sube archivos adicionales (Tu CV, o tablas CSV/Excel)")
archivo_cargado = st.file_uploader("Selecciona un archivo (PDF, DOCX, TXT, CSV, XLSX)", 
                                   type=["csv", "xlsx", "xls", "pdf", "docx", "txt", "md"], 
                                   label_visibility="collapsed")

df = None
df_head = "No se ha cargado ninguna tabla de datos (CSV/Excel)."

if archivo_cargado:
    nombre_archivo = archivo_cargado.name
    ext = os.path.splitext(nombre_archivo)[1].lower()
    ruta_temp = f"temp_{nombre_archivo}"
    
    with open(ruta_temp, "wb") as f:
        f.write(archivo_cargado.getbuffer())

    try:
        # Archivos Tabulares (Datos)
        if ext in [".csv", ".xlsx", ".xls"]:
            df = pd.read_csv(ruta_temp) if ext == ".csv" else pd.read_excel(ruta_temp)
            st.markdown("### 📊 Vista previa de los datos")
            st.dataframe(df.head())
            df_head = df.head().to_markdown()
            st.success("¡Tabla de datos cargada y lista para análisis!")

        # Archivos de Texto (CV, más guías)
        elif ext in [".pdf", ".docx", ".txt", ".md"]:
            with st.spinner("Agregando tu documento a la base de conocimiento..."):
                if ext == ".pdf":
                    docs = PyPDFLoader(ruta_temp).load()
                elif ext == ".docx":
                    docs = UnstructuredWordDocumentLoader(ruta_temp).load()
                else:
                    docs = TextLoader(ruta_temp, encoding="utf-8").load()
                
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                splits = text_splitter.split_documents(docs)
                
                # Agregamos los nuevos fragmentos al vectorstore existente
                st.session_state["vectorstore"].add_documents(splits)
                st.success("✅ ¡Documento personal integrado! Ya puedes hacerle preguntas.")
    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
    finally:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)

# --- CONFIGURACIÓN DEL AGENTE Y LLM ---
llm = ChatGoogleGenerativeAI(api_key=google_api_key, model="gemini-3.6-flash", temperature=0)
retriever = st.session_state["vectorstore"].as_retriever(search_kwargs={"k": 3})
tools = crear_herramientas(df, retriever)

prompt_react_es = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
    partial_variables={"df_head": df_head},
    template="""
Eres un experto consultor sobre inmigración a Canadá para mexicanos. 
El sistema ya cuenta con normativas migratorias oficiales.

Si el usuario subió una tabla (CSV/Excel), aquí están sus primeras filas:
{df_head}

Tienes acceso a las siguientes herramientas:
{tools}

Usa el formato exacto de razonamiento:
Question: la pregunta del usuario
Thought: Reflexiona sobre qué herramienta usar.
Action: la acción a ejecutar, DEBE ser una de las [{tool_names}]
Action Input: la entrada para la herramienta elegida
Observation: el resultado de la herramienta
... (repite Thought/Action/Action Input/Observation si es necesario)
Thought: Ya tengo la respuesta completa.
Final Answer: Responde de forma clara, detallada, amable y en español.

Question: {input}
Thought: {agent_scratchpad}
"""
)

agente = create_react_agent(llm=llm, tools=tools, prompt=prompt_react_es)
orquestador = AgentExecutor(agent=agente, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=5)

# --- ACCIONES RÁPIDAS (SOLO PARA CSV/EXCEL) ---
if df is not None:
    st.markdown("---")
    st.markdown("### ⚡ Análisis Automático de Datos")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Reporte General"):
            with st.spinner("Analizando tabla..."):
                st.markdown(orquestador.invoke({"input": "Genera un reporte de información general del dataframe"})["output"])
    with col2:
        if st.button("📈 Estadísticas"):
            with st.spinner("Calculando estadísticas..."):
                st.markdown(orquestador.invoke({"input": "Genera un reporte estadístico"})["output"])
                
    pregunta_grafico = st.text_input("Generar gráfico (ej. 'Genera un gráfico de los costos'):")
    if st.button("🎨 Dibujar Gráfico") and pregunta_grafico:
        with st.spinner("Procesando gráfico..."):
            orquestador.invoke({"input": pregunta_grafico})

# --- INTERFAZ DE CHAT ---
st.markdown("---")
st.markdown("### 💬 Chat Migratorio")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, message in st.session_state["chat_history"]:
    st.chat_message(role).write(message)

pregunta_usuario = st.chat_input("Ej: ¿Cuántos fondos necesito para Express Entry?")
if pregunta_usuario:
    st.chat_message("user").write(pregunta_usuario)
    st.session_state["chat_history"].append(("user", pregunta_usuario))
    
    with st.spinner("Consultando normativas canadienses..."):
        try:
            respuesta = orquestador.invoke({"input": pregunta_usuario})["output"]
        except Exception as e:
            respuesta = "Lo siento, hubo un problema al procesar tu solicitud."
            
        st.chat_message("assistant").write(respuesta)
        st.session_state["chat_history"].append(("assistant", respuesta))