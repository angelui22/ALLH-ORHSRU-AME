import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE ACCESO ---
CLAVE_INSTITUCIONAL = "ORH2026"

# --- DOCTRINA TÁCTICA ÍNTEGRA (INSTRUCCIONES PASADAS) ---
SYSTEM_PROMPT = """
ACTÚA COMO: Asesor Táctico AME de la Organización Rescate Humboldt (ORH).
ESTÁNDARES OBLIGATORIOS:
1. PHTLS: Evaluación X-ABCDE.
2. TCCC: Algoritmo MARTE (Hemorragias, Vía Aérea, Respiración, Circulación, Hipotermia).
3. SAR: Protocolos OACI (Anexo 12) e IAMSAR (OMI).
4. TRIAGE: Método START.

FASE 1: Seguridad de Escena (Conducta PAS: Proteger, Avisar, Socorrer).
FASE 2: Evaluación Clínica.
FASE 3: Plan de Evacuación.

CIERRE OBLIGATORIO: "No solo es querer salvar, sino saber salvar" Organización Rescate Humboldt. (ALLH-ORH:2026)
"""

# --- INICIALIZACIÓN DE INTERFAZ ---
st.set_page_config(page_title="AME-ORH Sistema Táctico", layout="wide", page_icon="🚑")

# --- CONTROL DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.image("https://static.wixstatic.com/media/d8b631_96e163498ad440adb30973da129107ba~mv2.png", width=120)
    st.title("SISTEMA DE ASISTENCIA AME-ORH")
    pwd = st.text_input("Ingrese Clave Táctica Institucional", type="password")
    if st.button("DESBLOQUEAR"):
        if pwd == CLAVE_INSTITUCIONAL:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Acceso Denegado")
    st.stop()

# --- CONFIGURACIÓN DEL MOTOR IA ---
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Forzamos el uso del modelo estable
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de motor: {e}")
else:
    st.error("Falta GOOGLE_API_KEY en Secrets.")
    st.stop()

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.title("CONTROL SAR-AME")
    id_u = st.text_input("ID Unidad", "SAR-01")
    if st.button("Cerrar Misión"):
        st.session_state.auth = False
        st.rerun()

# --- CHAT OPERATIVO ---
if "messages" not in st.session_state:
    bienvenida = f"""
    ### 🚑 UNIDAD {id_u} EN LÍNEA
    Especialista, sistema bajo doctrina **ALLH-ORH:2026** activo.
    
    Por favor, inicie con el reporte de **Seguridad de la Escena (PAS)**.
    """
    st.session_state.messages = [{"role": "assistant", "content": bienvenida}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Transmita SITREP..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        # Generación con doctrina inyectada
        contexto = f"{SYSTEM_PROMPT}\n\nSITUACIÓN ACTUAL:\n{prompt}"
        response = model.generate_content(contexto)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Falla de enlace: {e}")

st.markdown("---")
st.caption("© 2026 ORH - No solo es querer salvar, sino saber salvar.")
