import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SISTEMA AME-ORH 2026", page_icon="🚑", layout="wide")

# --- DOCTRINA TÁCTICA ---
CLAVE_INSTITUCIONAL = "ORH2026"
SYSTEM_PROMPT = """Actúa como Asesor Experto AME-ORH. 
Tus respuestas deben ser técnicas, precisas y basadas en protocolos PAS y MARTE.
Al final de cada respuesta, incluye siempre la frase: 'No solo es querer salvar, sino saber salvar. ALLH-ORH:2026.'"""

# --- FUNCIÓN DE REGISTRO EN GOOGLE SHEETS ---
def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        # Definir el alcance
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # Obtener credenciales desde st.secrets
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja (Asegúrate de que el nombre sea exacto)
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        
        # Insertar fila
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([timestamp, unidad, reporte, respuesta_ia[:500]])
        return True
    except Exception as e:
        # El error se muestra en el sidebar para no interrumpir el chat
        st.sidebar.error(f"Error de Registro: {e}")
        return False

# --- FUNCIÓN DE INTELIGENCIA ARTIFICIAL (GROQ) ---
def llamar_ia(texto_usuario):
    # Obtener y limpiar la clave de cualquier espacio o comilla extra
    api_key = st.secrets.get("GROQ_API_KEY", "").strip().strip('"').strip("'")
    
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
        "temperature": 0.6
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "Error 401: La clave GROQ_API_KEY en Secrets es inválida o tiene espacios adicionales."
        else:
            return f"Error IA ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Fallo de conexión con el servidor IA: {e}"

# --- INTERFAZ Y SEGURIDAD ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("### 🛡️ ACCESO RESTRINGIDO - SISTEMA AME-ORH")
    password = st.text_input("Ingrese Clave de Unidad:", type="password")
    if st.button("DESBLOQUEAR"):
        if password == CLAVE_INSTITUCIONAL:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acceso denegado. Credenciales incorrectas.")
    st.stop()

# --- PANEL DE CONTROL ---
st.title("🚑 ASESORÍA TÁCTICA AME-ORH")

with st.sidebar:
    st.header("UNIDAD OPERATIVA")
    nombre_unidad = st.text_input("ID de Unidad:", value="OPERADOR-01")
    st.divider()
    if st.button("Finalizar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrada de SITREP
if prompt := st.chat_input("Describa la emergencia o reporte táctico..."):
    # Guardar y mostrar mensaje de usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Procesar con IA
    with st.spinner("IA analizando doctrina MARTE..."):
        respuesta = llamar_ia(prompt)
        # Intentar registro en Google Sheets
        registrar_en_excel(nombre_unidad, prompt, respuesta)

    # Mostrar respuesta de IA
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
