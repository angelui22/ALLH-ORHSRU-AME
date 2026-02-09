import streamlit as st
import requests
import json

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="AME-ORH Táctico", layout="wide")
CLAVE_INSTITUCIONAL = "ORH2026"

# --- DOCTRINA ---
SYSTEM_PROMPT = "Actúa como Asesor AME de la ORH. Usa protocolos MARTE, START y PAS. Cierra con: No solo es querer salvar, sino saber salvar. ALLH-ORH:2026."

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("SISTEMA AME-ORH")
    pwd = st.text_input("Clave Táctica", type="password")
    if st.button("ACCEDER"):
        if pwd == CLAVE_INSTITUCIONAL:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- MOTOR DE IA (VERSIÓN LIGERA) ---
def llamar_ia(texto_usuario):
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    # URL estable sin v1beta para evitar el 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nREPORTE: {texto_usuario}"}]}]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {r.status_code}: {r.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- INTERFAZ DE CHAT (RESTAURADA) ---
st.title("🚑 ASESOR TÁCTICO AME-ORH")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad SAR activa. Transmita SITREP."}]

# Mostrar historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Barra de entrada (Chat Input)
if prompt := st.chat_input("Escriba su reporte aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Consultando doctrina..."):
        respuesta = llamar_ia(prompt)
        
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
