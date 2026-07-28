import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv

from langchain.agents import Tool
from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-3.6-flash", temperature=0
)

# --- 1. HERRAMIENTAS DE DATOS (CSV/EXCEL) ---
@tool
def informacion_df(pregunta: str, df: pd.DataFrame) -> str:
    """Úsala para dar un informe general de una tabla de datos (columnas, tipos, dimensiones, nulos)."""
    plantilla = PromptTemplate(
        template="""Analiza esta metadata del dataset:
        Dimensiones: {shape} | Columnas: {columns} | Nulos: {nulos} | Duplicados: {duplicados}
        Redacta un informe estructurado respondiendo: {pregunta}""",
        input_variables=["pregunta", "shape", "columns", "nulos", "duplicados"]
    )
    return (plantilla | llm | StrOutputParser()).invoke({
        "pregunta": pregunta, "shape": df.shape, "columns": df.dtypes.to_string(),
        "nulos": df.isnull().sum().to_string(), "duplicados": df.duplicated().sum()
    })

@tool
def resumen_estadistico(pregunta: str, df: pd.DataFrame) -> str:
    """Úsala para resúmenes estadísticos (promedios, mínimos, máximos) de los datos tabulares."""
    plantilla = PromptTemplate(
        template="""Interpreta estas estadísticas y responde la pregunta: '{pregunta}'.
        Estadísticas: {resumen}""",
        input_variables=["pregunta", "resumen"]
    )
    return (plantilla | llm | StrOutputParser()).invoke({"pregunta": pregunta, "resumen": df.describe(include="number").to_string()})

@tool
def generar_grafico(pregunta: str, df: pd.DataFrame) -> str:
    """Úsala para generar gráficos en pantalla usando matplotlib/seaborn."""
    plantilla = PromptTemplate(
        template="""Genera SOLO CÓDIGO PYTHON limpio (sin markdown) para graficar esto: '{pregunta}'.
        Columnas: {columnas} | Muestra: {muestra}. 
        Usa plt y sns. Finaliza con plt.show().""",
        input_variables=["pregunta", "columnas", "muestra"]
    )
    script_bruto = (plantilla | llm | StrOutputParser()).invoke({
        "pregunta": pregunta, 
        "columnas": "\n".join([f"{c} ({d})" for c, d in df.dtypes.items()]), 
        "muestra": df.head(3).to_dict(orient="records")
    })
    
    script_limpio = script_bruto.replace("```python", "").replace("```", "").strip()
    exec(script_limpio, {"df": df, "plt": plt, "sns": sns}, {})
    fig = plt.gcf()
    st.pyplot(fig)
    plt.close(fig)
    return "Gráfico generado exitosamente."

# --- 2. HERRAMIENTA RAG (BASE DE CONOCIMIENTO MIGRATORIA) ---
def crear_herramienta_migracion(retriever):
    def buscar_documentos_migratorios(pregunta: str) -> str:
        docs = retriever.invoke(pregunta)
        contexto = "\n\n".join([d.page_content for d in docs])

        plantilla = PromptTemplate(
            template="""Eres un experto en migración a Canadá para mexicanos.
            Responde usando ESTRICTAMENTE esta información oficial:
            {contexto}
            Pregunta: {pregunta}
            Si no está en el texto, indícalo amablemente.""",
            input_variables=["contexto", "pregunta"],
        )
        return (plantilla | llm | StrOutputParser()).invoke({"contexto": contexto, "pregunta": pregunta})

    return Tool(
        name="Consultar Documentos de Migracion",
        func=buscar_documentos_migratorios,
        description="ÚSALA SIEMPRE para responder dudas sobre Express Entry, visas, permisos, requisitos, idiomas, o leyes migratorias.",
        return_direct=False,
    )

# --- 3. EXPORTADOR DE HERRAMIENTAS ---
def crear_herramientas(df=None, retriever=None):
    herramientas = []
    
    if retriever:
        herramientas.append(crear_herramienta_migracion(retriever))
        
    if df is not None and not df.empty:
        herramientas.extend([
            Tool(name="Informaciones DF", func=lambda p: informacion_df.invoke({"pregunta": p, "df": df}), description="Informe de estructura de datos.", return_direct=True),
            Tool(name="Resumen Estadistico", func=lambda p: resumen_estadistico.invoke({"pregunta": p, "df": df}), description="Estadísticas de datos numéricos.", return_direct=True),
            Tool(name="Generar Grafico", func=lambda p: generar_grafico.invoke({"pregunta": p, "df": df}), description="Generar gráficas visuales.", return_direct=True),
            Tool(name="Herramienta Codigos Python", func=PythonAstREPLTool(locals={"df": df}), description="Cálculos puntuales en Python sobre el DF.", return_direct=False),
        ])
        
    return herramientas