import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
CLAVE_INSTITUCIONAL = "ORH2026"

# --- FUNCIÓN DE REGISTRO EN GOOGLE SHEETS ---
def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # Cargamos credenciales desde Secrets
        creds_info = dict(st.secrets["gcp_service_account"])
        # Limpieza de saltos de línea en la llave privada
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja (Asegúrate de que el archivo se llame así y esté compartido con el client_email)
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([fecha, unidad, reporte, respuesta_ia[:500]]) # Limitamos a 500 caracteres para el Excel
        return True
    except Exception as e:
        st.sidebar.error(f"Error de Registro: {e}")
        return False

# --- MOTOR DE IA (GROQ) ---
def llamar_ia_groq(texto_usuario):
    api_key = st.secrets.get("GROQ_API_KEY", "").strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = "Actúa como Asesor Táctico AME de la ORH. Usa protocolos MARTE, START y PAS. Cierra con: No solo es querer salvar, sino saber salvar. ALLH-ORH:2026."
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": texto_usuario}
        ],
        "temperature": 0.6
    }
    
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code == 200:
        return r.json()['choices'][0]['message']['content']
    return f"Error de IA: {r.status_code}"

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="AME-ORH Táctico", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("SISTEMA DE ASISTENCIA AME-ORH")
    pwd = st.text_input("Clave Táctica", type="password")
    if st.button("DESBLOQUEAR"):
        if pwd == CLAVE_INSTITUCIONAL:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.title("SAR-AME CONTROL")
    u_id = st.text_input("Unidad", "SAR-01")
    if st.button("Finalizar"):
        st.session_state.auth = False
        st.rerun()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad activa. Transmita SITREP."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escriba su reporte..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Analizando y Registrando..."):
        # 1. Obtenemos respuesta de la IA
        respuesta = llamar_ia_groq(prompt)
        # 2. Registramos en Excel
        registrar_en_excel(u_id, prompt, respuesta)
        
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"): st.markdown(respuesta)
