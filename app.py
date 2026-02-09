import streamlit as st
import requests

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="AME-ORH Táctico", layout="wide", page_icon="🚑")

# --- DOCTRINA INSTITUCIONAL ---
SYSTEM_PROMPT = """
ACTÚA COMO: Asesor Táctico AME de la Organización Rescate Humboldt.
ESTÁNDARES: PHTLS (X-ABCDE), TCCC (MARTE), START (Triage).
CIERRE OBLIGATORIO: "No solo es querer salvar, sino saber salvar" ALLH-ORH:2026.
"""

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("SISTEMA AME-ORH (MOTOR RESILIENTE)")
    pwd = st.text_input("Clave Táctica", type="password")
    if st.button("ACCEDER"):
        if pwd == "ORH2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- MOTOR DE IA (VIA GROQ - SIN BLOQUEOS REGIONALES) ---
def llamar_ia_groq(texto_usuario):
    api_key = st.secrets.get("GROQ_API_KEY", "").strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texto_usuario}
        ],
        "temperature": 0.7
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f"Error de Servicio: {r.status_code}. Verifique su GROQ_API_KEY."
    except Exception as e:
        return f"Falla de conexión: {str(e)}"

# --- INTERFAZ DE USUARIO ---
st.title("🚑 ASESOR TÁCTICO AME-ORH")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad SAR activa. Motor Groq desplegado. Transmita SITREP."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escriba su reporte aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Procesando bajo doctrina Humboldt..."):
        respuesta = llamar_ia_groq(prompt)
        
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"): st.markdown(respuesta)
