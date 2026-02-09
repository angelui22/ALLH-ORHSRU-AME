import streamlit as st
import requests
import json

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="AME-ORH Táctico", layout="wide", page_icon="🚑")

# --- DOCTRINA INSTITUCIONAL ---
SYSTEM_PROMPT = """
ACTÚA COMO: Asesor AME de la Organización Rescate Humboldt.
PROTOCOLOS: PAS, MARTE (X-ABCDE), START.
CIERRE: "No solo es querer salvar, sino saber salvar" ALLH-ORH:2026.
"""

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("SISTEMA AME-ORH")
    pwd = st.text_input("Clave Táctica", type="password")
    if st.button("ACCEDER"):
        if pwd == "ORH2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- MOTOR DE IA CON RESPALDO (ANTI-404) ---
def llamar_ia(texto_usuario):
    api_key = st.secrets.get("GOOGLE_API_KEY", "AIzaSyAB4iZKQRBpTS5Q8ym9TlELSBdneQn8-oE").strip()
    
    # Intentaremos con dos variantes de nombre de modelo que son las más estables actualmente
    modelos_a_probar = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]
    
    for modelo in modelos_a_probar:
        # Probamos primero con la versión estable v1
        url = f"https://generativelanguage.googleapis.com/v1/models/{modelo}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nREPORTE: {texto_usuario}"}]}]}
        
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                return r.json()['candidates'][0]['content']['parts'][0]['text']
            # Si da 404, el bucle intentará con el siguiente modelo en la lista
        except:
            continue
            
    return "Error Crítico: El servicio de Google no reconoce los modelos disponibles en su región. Verifique su API Key en Google AI Studio."

# --- INTERFAZ DE USUARIO ---
st.title("🚑 ASESOR TÁCTICO AME-ORH")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad SAR activa. Transmita SITREP bajo doctrina MARTE."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Escriba su reporte aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Sincronizando con base de datos táctica..."):
        respuesta = llamar_ia(prompt)
        
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
