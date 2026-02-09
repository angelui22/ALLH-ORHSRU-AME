import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="SISTEMA AME-ORH 2026", layout="wide")

CLAVE_INSTITUCIONAL = "ORH2026"
SYSTEM_PROMPT = """Actúa como Asesor Experto AME-ORH. 
Tus respuestas deben ser técnicas, precisas y basadas en protocolos PAS y MARTE.
Al final de cada respuesta, incluye siempre la frase: 'No solo es querer salvar, sino saber salvar. ALLH-ORH:2026.'"""

def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([timestamp, unidad, reporte, respuesta_ia[:500]])
        return True
    except Exception as e:
        st.sidebar.error(f"Error de Registro: {str(e)}")
        return False

def llamar_ia(texto_usuario):
    # Forzamos limpieza total de la llave
    api_key = st.secrets["GROQ_API_KEY"].strip().replace('"', '').replace("'", "")
    
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
        "temperature": 0.5
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error IA ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- INTERFAZ ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ ACCESO SISTEMA AME-ORH")
    password = st.text_input("Ingrese Clave de Unidad:", type="password")
    if st.button("DESBLOQUEAR"):
        if password == CLAVE_INSTITUCIONAL:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acceso denegado.")
    st.stop()

st.title("🚑 ASESORÍA TÁCTICA AME-ORH")

with st.sidebar:
    st.header("CONFIGURACIÓN")
    unidad_id = st.text_input("ID Unidad:", value="SAR-01")
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Escriba su SITREP aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("IA procesando..."):
        respuesta = llamar_ia(prompt)
        registrar_en_excel(unidad_id, prompt, respuesta)

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
