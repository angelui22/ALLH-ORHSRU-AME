import streamlit as st
import requests
import json
from datetime import datetime

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="AME-ORH Táctico", layout="wide", page_icon="🚑")

# --- DOCTRINA INSTITUCIONAL ÍNTEGRA ---
SYSTEM_PROMPT = """
ACTÚA COMO: Asesor Táctico AME de la Organización Rescate Humboldt (ORH).
ESTÁNDARES OBLIGATORIOS:
1. PHTLS: Evaluación X-ABCDE.
2. TCCC: Algoritmo MARTE (Hemorragias, Vía Aérea, Respiración, Circulación, Hipotermia).
3. SAR: Protocolos OACI (Anexo 12) e IAMSAR (OMI).
4. TRIAGE: Método START.

INSTRUCCIONES DE RESPUESTA:
- Prioriza SIEMPRE la Seguridad de la Escena (PAS).
- Usa un tono técnico, profesional y autoritario pero empático.
- Estructura tus respuestas con viñetas para facilitar la lectura en campo.

CIERRE OBLIGATORIO: "No solo es querer salvar, sino saber salvar" Organización Rescate Humboldt. (ALLH-ORH:2026)
"""

# --- CONTROL DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.image("https://static.wixstatic.com/media/d8b631_96e163498ad440adb30973da129107ba~mv2.png", width=120)
    st.title("SISTEMA DE ASISTENCIA AME-ORH")
    pwd = st.text_input("Ingrese Clave Táctica Institucional", type="password")
    if st.button("DESBLOQUEAR"):
        if pwd == "ORH2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Acceso Denegado")
    st.stop()

# --- MOTOR DE IA (VIA GROQ - RESILIENTE A BLOQUEOS) ---
def llamar_ia_groq(texto_usuario):
    api_key = st.secrets.get("GROQ_API_KEY", "").strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile", # Modelo de alta capacidad
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texto_usuario}
        ],
        "temperature": 0.5, # Mayor precisión técnica
        "max_tokens": 1024
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f"Error de Servicio: {r.status_code}. Detalle: {r.text}"
    except Exception as e:
        return f"Falla de conexión: {str(e)}"

# --- INTERFAZ OPERATIVA ---
with st.sidebar:
    st.image("https://static.wixstatic.com/media/d8b631_96e163498ad440adb30973da129107ba~mv2.png", width=100)
    st.title("CONTROL SAR-AME")
    u_id = st.text_input("Unidad", "SAR-01")
    st.info("Motor: Groq Llama-3 (Resiliente)")
    if st.button("Finalizar Misión"):
        st.session_state.auth = False
        st.rerun()

st.title("🚑 ASESOR TÁCTICO AME-ORH")

if "messages" not in st.session_state:
    bienvenida = f"### 🚑 UNIDAD {u_id} EN LÍNEA\nEspecialista, sistema bajo doctrina **ALLH-ORH:2026** activo.\n\nTransmita reporte de escena o estado del paciente para iniciar protocolos PAS/MARTE."
    st.session_state.messages = [{"role": "assistant", "content": bienvenida}]

# Mostrar historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrada de usuario
if prompt := st.chat_input("Transmita SITREP..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Procesando bajo doctrina Humboldt..."):
        respuesta = llamar_ia_groq(prompt)
        
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)

st.markdown("---")
st.caption(f"© {datetime.now().year} Organización Rescate Humboldt - División AME")
