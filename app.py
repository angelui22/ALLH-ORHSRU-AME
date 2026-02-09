import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import os

# --- PROTOCOLO DE CONEXIÓN GLOBAL ---
def inicializar_ia():
    if "GOOGLE_API_KEY" in st.secrets:
        # Forzamos la configuración para usar la versión estable y transporte REST
        # Esto ayuda a saltar bloqueos regionales de v1beta
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

# --- DOCTRINA INSTITUCIONAL ORH (MANTENIDA) ---
SYSTEM_PROMPT = """
ACTÚA COMO: Asesor Táctico AME de la Organización Rescate Humboldt.
PROTOCOLOS: PHTLS (X-ABCDE), TCCC (MARTE), START (Triage).
CIERRE: "No solo es querer salvar, sino saber salvar" ALLH-ORH:2026.
"""

st.set_page_config(page_title="AME-ORH Operaciones", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("SISTEMA AME-ORH")
    if st.text_input("Clave Táctica", type="password") == "ORH2026":
        if st.button("ACCEDER"): 
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- EJECUCIÓN ---
model = inicializar_ia()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad SAR activa. Reporte SITREP."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Transmita..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        # Usamos un bloque de control de errores más agresivo
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nREPORTE: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Bloqueo de Región/Enlace: {e}")
        st.warning("⚠️ Su ubicación actual (VZLA) podría estar restringida. Intente usar un VPN en su navegador o cambie la región de su cuenta Google a una soportada globalmente.")

st.caption("© 2026 ORH")
