import streamlit as st
import requests
import json
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
CLAVE_INSTITUCIONAL = "ORH2026"
API_KEY = st.secrets.get("GOOGLE_API_KEY", "").strip()

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

# --- MOTOR DE COMUNICACIÓN DIRECTA (REST v1 - COMPATIBILIDAD TOTAL) ---
def llamar_ia_directo(prompt_usuario):
    # Probamos con la ruta de modelo más genérica disponible
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nREPORTE DE CAMPO: {prompt_usuario}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Si v1beta falla (404), intentamos v1 automáticamente
        if response.status_code == 404:
            url_v1 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            response = requests.post(url_v1, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error de Enlace Crítico ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Falla en la transmisión: {str(e)}"

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.title("CONTROL SAR-AME")
    id_u = st.text_input("ID Unidad", "SAR-01")
    if st.button("Cerrar Misión"):
        st.session_state.auth = False
        st.rerun()

if "messages" not in st.session_state:
    bienvenida = f"### 🚑 UNIDAD {id_u} EN LÍNEA\nEspecialista, sistema activo. Indique situación (PAS/MARTE)."
