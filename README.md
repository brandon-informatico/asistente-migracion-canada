<!-- # 🇨🇦 Asistente de Inteligencia Artificial para Migración a Canadá

¡Bienvenido! Este proyecto es un **agente conversacional inteligente** desarrollado para orientar a ciudadanos mexicanos sobre las distintas vías de migración, visados, permisos de estudio/trabajo y requisitos oficiales para establecerse en Canadá.

El sistema combina **Arquitectura RAG (Retrieval-Augmented Generation)** con un **Agente ReAct** capaz de razonar, consultar documentos oficiales precargados y analizar archivos de datos tabulares (costos de vida, puntajes CRS, etc.).

---

## 🚀 Características Principales

* **Consultor Migratorio RAG:** Respuestas precisas sobre Express Entry (FSWP, CEC), Tratado CUSMA/T-MEC, Permisos de Estudio (PGWP) y Programas Provinciales (PNP).
* **Soporte Multi-Formato:** Procesa e indexa archivos en formato **PDF, Word (.docx), TXT, Markdown (.md), CSV y Excel (.xlsx)**.
* **Agente Híbrido ReAct:** Capacidad de razonamiento para decidir si debe buscar en documentos normativos o ejecutar código Python para analizar tablas de datos.
* **Motor de IA:** Alimentado con el modelo **Google Gemini 3.6 Flash** e indexado vectorial con **FAISS**.
* **Interfaz Interactiva:** Desarrollada con **Streamlit** para una experiencia gráfica conversacional fluida.

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología / Librería |
| :--- | :--- |
| **Lenguaje** | Python 3.10+ |
| **Frameworks de IA** | LangChain, LangChain Community, LangChain Experimental |
| **LLM & Embeddings** | Google Gemini (`gemini-3.6-flash`), Google GenAI Embeddings (`gemini-embedding-001`) |
| **Base de Datos Vectorial** | FAISS (Facebook AI Similarity Search) |
| **Interfaz Web** | Streamlit |
| **Análisis y Gráficos** | Pandas, Matplotlib, Seaborn |

---

## ⚙️ Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de contar con:

1. **Python 3.10 o superior** instalado en tu sistema.
2. Una **Google Gemini API Key** (puedes obtenerla gratuitamente en [Google AI Studio](https://aistudio.google.com/)).

---

## 📦 Instrucciones de Instalación y Ejecución Local

Sigue estos sencillos pasos para poner a funcionar el asistente en tu computadora:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/brandon-informatico/asistente-migracion-canada.git](https://github.com/brandon-informatico/asistente-migracion-canada.git)
cd asistente-migracion-canada


2. Crear y activar un entorno virtual
En Windows (PowerShell):

PowerShell


python -m venv .venv
.\.venv\Scripts\Activate
En Mac/Linux:

Bash


python3 -m venv .venv
source .venv/bin/activate
3. Instalar las dependencias
Bash


pip install -r requirements.txt
4. Configurar la API Key
Crea un archivo llamado .env en la raíz del proyecto (o ingrésala directamente en la barra lateral de la app) con la siguiente variable:

Fragmento de código


GOOGLE_API_KEY="tu_api_key_de_gemini_aqui"
5. Iniciar la aplicación en Streamlit
Bash


streamlit run app.py
Se abrirá automáticamente tu navegador en http://localhost:8501.

🧠 Estructura del Código
Plaintext


asistente-migracion-canada/
│
├── app.py               # Aplicación principal de Streamlit, interfaz y flujo ReAct
├── herramientas.py      # Definición de herramientas (RAG con FAISS + Análisis Pandas)
├── requirements.txt     # Dependencias y librerías del proyecto
├── .gitignore           # Archivos ignorados por Git (.env, .venv, temporales)
└── data_docs/           # Base de conocimiento interna en Markdown/PDF
💬 Ejemplos de Preguntas y Respuestas
Ejemplo 1: Consulta sobre visados profesionales (T-MEC)
Pregunta: "Soy ingeniero mexicano, ¿puedo trabajar en Canadá bajo el tratado T-MEC sin un examen de mercado laboral (LMIA)?"

Respuesta del Agente: "¡Sí! Bajo el acuerdo CUSMA/T-MEC, los ciudadanos mexicanos con profesiones elegibles (como ingeniería) que cuenten con una oferta de empleo formal en Canadá están exentos de requerir una evaluación LMIA, facilitando enormemente el trámite del permiso de trabajo temporal."

Ejemplo 2: Consulta de requisitos de idioma
Pregunta: "¿Qué examen de inglés necesito para Express Entry y cuál es el puntaje de fondos exigido?"

Respuesta del Agente: "Para inglés debes presentar el examen IELTS General o CELPIP. En cuanto a fondos de sustentabilidad, para una persona solitaria se requiere demostrar aproximadamente entre $14,000 y $15,000 CAD líquidos, a menos que apliques por Canadian Experience Class (CEC) o cuentes con una oferta laboral válida." -->

#Prueba de pregunta.
<img width="1919" height="560" alt="image" src="https://github.com/user-attachments/assets/a5984cd5-9e14-4e9b-9bd7-a97e0b5214dc" />

#Prueba con respuesta y sugerencia.
<img width="1875" height="787" alt="image" src="https://github.com/user-attachments/assets/7c4b1975-c88d-4b92-a7d7-5aab696a8004" />

#Prueba con csv.
<img width="1919" height="937" alt="image" src="https://github.com/user-attachments/assets/33805f28-b2f3-40b5-a2ca-34031b606aed" />
