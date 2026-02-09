import streamlit as st
import requests
import json
from datetime import datetime

# --- CONFIGURACIÓN ---
CLAVE_INSTITUCIONAL = "ORH2026"
API_KEY = st.secrets.get("AIzaSyAB4iZKQRBpTS5Q8ym9TlELSBdneQn8-oE")

# --- DOCTRINA ORH ---
SYSTEM_PROMPT = """
Actúa como Asesor Táctico AME de la Organización Rescate Humboldt.
Protocolos: PHTLS (X-ABCDE), TCCC (MARTE), START (Triage).
Cierre: "No solo es querer salvar, sino saber salvar" ALLH-ORH:2026.
"""

st.set_page_config(page_title="AME-ORH Sistema", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("SISTEMA DE ASISTENCIA AME-ORH")
    if st.text_input("Clave Táctica", type="password") == CLAVE_INSTITUCIONAL:
        if st.button("DESBLOQUEAR"): 
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- FUNCIÓN DE CONEXIÓN DIRECTA (PUENTE REST) ---
def llamar_ia_directo(prompt_usuario):
    # Usamos la URL de la versión estable v1, no la beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nREPORTE: {prompt_usuario}"}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800
        }
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error de Enlace Crítico ({response.status_code}): {response.text}"

# --- INTERFAZ ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad SAR-01 en línea. Transmita SITREP."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escriba su reporte..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Procesando doctrina..."):
        respuesta = llamar_ia_directo(prompt)
        
    with st.chat_message("assistant"):
        st.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})

