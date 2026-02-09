import streamlit as st
import requests
import json
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
CLAVE_INSTITUCIONAL = "ORH2026"

# --- DOCTRINA INSTITUCIONAL ÍNTEGRA ---
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

# --- MOTOR DE COMUNICACIÓN DIRECTA (REST v1) ---
def llamar_ia_directo(prompt_usuario):
    # Verificación de existencia de llave
    if "GOOGLE_API_KEY" not in st.secrets:
        return "Error: GOOGLE_API_KEY no configurada en Secrets."
    
    # Limpieza de la llave (Elimina espacios accidentales)
    api_key_limpia = st.secrets["GOOGLE_API_KEY"].strip()
    
    # URL Forzada a v1 Estable
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key_limpia}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nREPORTE DE CAMPO: {prompt_usuario}"}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error de Enlace Crítico ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Falla en la transmisión: {str(e)}"

# --- PANEL LATERAL ---
with st.sidebar:
    st.title("CONTROL SAR-AME")
    id_u = st.text_input("ID Unidad", "SAR-01")
    st.divider()
    if st.button("Cerrar Misión"):
        st.session_state.auth = False
        st.rerun()

# --- CHAT OPERATIVO ---
if "messages" not in st.session_state:
    bienvenida = f"### 🚑 UNIDAD {id_u} EN LÍNEA\nEspecialista, sistema bajo doctrina **ALLH-ORH:2026** activo.\n\nIndique estado de la escena (PAS) para iniciar."
    st.session_state.messages = [{"role": "assistant", "content": bienvenida}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Transmita SITREP..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Sincronizando con base de datos táctica..."):
        respuesta = llamar_ia_directo(prompt)
        
    with st.chat_message("assistant"):
        st.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.caption("© 2026 ORH - División AME - No solo es querer salvar, sino saber salvar.")
