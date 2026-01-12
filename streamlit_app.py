import streamlit as st
import anthropic
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import re

# ============================================================================
# CONFIGURATION AND SETUP
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="Advanced AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language support
LANGUAGES = {
    "en": {
        "title": "Advanced AI Chatbot",
        "subtitle": "Powered by Claude API",
        "settings": "Settings",
        "chat_history": "Chat History",
        "clear_history": "Clear History",
        "language": "Language",
        "temperature": "Temperature (Creativity)",
        "max_tokens": "Max Tokens",
        "model": "Model Selection",
        "system_prompt": "System Prompt",
        "input_placeholder": "Type your message here...",
        "send": "Send",
        "export": "Export Chat",
        "import": "Import Chat",
        "conversation_name": "Conversation Name",
        "no_history": "No conversation history yet.",
        "thinking": "Thinking...",
        "error": "Error",
        "success": "Success",
        "api_key_missing": "API key not found. Please add ANTHROPIC_API_KEY to your environment variables.",
    },
    "es": {
        "title": "Chatbot de IA Avanzado",
        "subtitle": "Impulsado por Claude API",
        "settings": "Configuración",
        "chat_history": "Historial de Chat",
        "clear_history": "Limpiar Historial",
        "language": "Idioma",
        "temperature": "Temperatura (Creatividad)",
        "max_tokens": "Tokens Máximos",
        "model": "Selección de Modelo",
        "system_prompt": "Mensaje del Sistema",
        "input_placeholder": "Escribe tu mensaje aquí...",
        "send": "Enviar",
        "export": "Exportar Chat",
        "import": "Importar Chat",
        "conversation_name": "Nombre de la Conversación",
        "no_history": "Sin historial de conversación aún.",
        "thinking": "Pensando...",
        "error": "Error",
        "success": "Éxito",
        "api_key_missing": "Clave API no encontrada. Agregue ANTHROPIC_API_KEY a sus variables de entorno.",
    },
    "fr": {
        "title": "Chatbot IA Avancé",
        "subtitle": "Alimenté par Claude API",
        "settings": "Paramètres",
        "chat_history": "Historique du Chat",
        "clear_history": "Effacer l'Historique",
        "language": "Langue",
        "temperature": "Température (Créativité)",
        "max_tokens": "Jetons Maximum",
        "model": "Sélection du Modèle",
        "system_prompt": "Invite Système",
        "input_placeholder": "Tapez votre message ici...",
        "send": "Envoyer",
        "export": "Exporter le Chat",
        "import": "Importer le Chat",
        "conversation_name": "Nom de la Conversation",
        "no_history": "Aucun historique de conversation pour l'instant.",
        "thinking": "Réflexion...",
        "error": "Erreur",
        "success": "Succès",
        "api_key_missing": "Clé API non trouvée. Veuillez ajouter ANTHROPIC_API_KEY à vos variables d'environnement.",
    },
    "ja": {
        "title": "高度なAIチャットボット",
        "subtitle": "Claude APIを搭載",
        "settings": "設定",
        "chat_history": "チャット履歴",
        "clear_history": "履歴をクリア",
        "language": "言語",
        "temperature": "温度（創造性）",
        "max_tokens": "最大トークン",
        "model": "モデルの選択",
        "system_prompt": "システムプロンプト",
        "input_placeholder": "ここにメッセージを入力してください...",
        "send": "送信",
        "export": "チャットをエクスポート",
        "import": "チャットをインポート",
        "conversation_name": "会話名",
        "no_history": "まだ会話履歴がありません。",
        "thinking": "考え中...",
        "error": "エラー",
        "success": "成功",
        "api_key_missing": "APIキーが見つかりません。ANTHROPIC_API_KEYを環境変数に追加してください。",
    }
}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables."""
    if "language" not in st.session_state:
        st.session_state.language = "en"
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2048
    
    if "model" not in st.session_state:
        st.session_state.model = "claude-3-5-sonnet-20241022"
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful, intelligent, and friendly AI assistant. Provide clear, concise, and accurate responses."
    
    if "conversation_name" not in st.session_state:
        st.session_state.conversation_name = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if "client" not in st.session_state:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error(LANGUAGES[st.session_state.language]["api_key_missing"])
            st.stop()
        st.session_state.client = anthropic.Anthropic(api_key=api_key)

initialize_session_state()

# Get translations for current language
t = LANGUAGES[st.session_state.language]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_message(role: str, content: str) -> Dict:
    """Format a message for the conversation history."""
    return {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }

def export_conversation() -> str:
    """Export conversation as JSON."""
    export_data = {
        "conversation_name": st.session_state.conversation_name,
        "language": st.session_state.language,
        "model": st.session_state.model,
        "temperature": st.session_state.temperature,
        "max_tokens": st.session_state.max_tokens,
        "system_prompt": st.session_state.system_prompt,
        "exported_at": datetime.now().isoformat(),
        "messages": st.session_state.conversation_history
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def import_conversation(json_data: str) -> bool:
    """Import conversation from JSON."""
    try:
        data = json.loads(json_data)
        st.session_state.conversation_history = data.get("messages", [])
        st.session_state.conversation_name = data.get("conversation_name", st.session_state.conversation_name)
        st.session_state.language = data.get("language", "en")
        st.session_state.model = data.get("model", "claude-3-5-sonnet-20241022")
        st.session_state.temperature = data.get("temperature", 0.7)
        st.session_state.max_tokens = data.get("max_tokens", 2048)
        st.session_state.system_prompt = data.get("system_prompt", "")
        return True
    except json.JSONDecodeError:
        return False

def count_tokens_estimate(text: str) -> int:
    """Estimate token count (rough approximation)."""
    # Rough estimate: ~4 characters per token
    return len(text) // 4

def get_api_response(user_message: str) -> Optional[str]:
    """Get response from Claude API."""
    try:
        # Prepare messages for API
        messages = []
        for msg in st.session_state.conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call Claude API
        response = st.session_state.client.messages.create(
            model=st.session_state.model,
            max_tokens=st.session_state.max_tokens,
            system=st.session_state.system_prompt,
            messages=messages
        )
        
        return response.content[0].text
    
    except anthropic.APIError as e:
        st.error(f"{t['error']}: {str(e)}")
        return None

def clear_conversation_history():
    """Clear the conversation history."""
    st.session_state.conversation_history = []
    st.session_state.conversation_name = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ " + t["settings"])
    
    # Language selection
    st.session_state.language = st.selectbox(
        t["language"],
        options=list(LANGUAGES.keys()),
        format_func=lambda x: {"en": "English", "es": "Español", "fr": "Français", "ja": "日本語"}.get(x, x),
        key="language_select"
    )
    
    # Model selection
    st.session_state.model = st.selectbox(
        t["model"],
        options=[
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20250219",
        ],
        key="model_select"
    )
    
    # Temperature slider
    st.session_state.temperature = st.slider(
        t["temperature"],
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        key="temperature_slider"
    )
    
    # Max tokens slider
    st.session_state.max_tokens = st.slider(
        t["max_tokens"],
        min_value=256,
        max_value=4096,
        value=st.session_state.max_tokens,
        step=256,
        key="max_tokens_slider"
    )
    
    # System prompt
    st.session_state.system_prompt = st.text_area(
        t["system_prompt"],
        value=st.session_state.system_prompt,
        height=100,
        key="system_prompt_area"
    )
    
    st.divider()
    
    # Conversation management
    st.markdown("### 💬 " + t["chat_history"])
    
    # Conversation name
    st.session_state.conversation_name = st.text_input(
        t["conversation_name"],
        value=st.session_state.conversation_name,
        key="conv_name_input"
    )
    
    # Export/Import buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 " + t["export"], use_container_width=True):
            export_json = export_conversation()
            st.download_button(
                label="💾 JSON",
                data=export_json,
                file_name=f"{st.session_state.conversation_name}.json",
                mime="application/json",
                key="export_button"
            )
    
    with col2:
        uploaded_file = st.file_uploader(
            t["import"],
            type="json",
            key="import_upload"
        )
        if uploaded_file:
            try:
                json_data = uploaded_file.read().decode("utf-8")
                if import_conversation(json_data):
                    st.success(t["success"])
                    st.rerun()
                else:
                    st.error(t["error"])
            except Exception as e:
                st.error(f"{t['error']}: {str(e)}")
    
    # Clear history button
    if st.button("🗑️ " + t["clear_history"], use_container_width=True, type="secondary"):
        clear_conversation_history()
        st.rerun()
    
    st.divider()
    
    # Stats
    st.markdown("### 📊 Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.conversation_history))
    with col2:
        token_estimate = sum(
            count_tokens_estimate(msg["content"])
            for msg in st.session_state.conversation_history
        )
        st.metric("Est. Tokens", token_estimate)

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

# Header
st.title("🤖 " + t["title"])
st.markdown(f"*{t['subtitle']}*")

# Model info
col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"📋 **Model:** {st.session_state.model}")
with col2:
    st.info(f"🌡️ **Temperature:** {st.session_state.temperature}")
with col3:
    st.info(f"🎯 **Language:** {st.session_state.language.upper()}")

st.divider()

# Chat display area
chat_container = st.container()

with chat_container:
    if st.session_state.conversation_history:
        for message in st.session_state.conversation_history:
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp", "")
            
            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp_str = dt.strftime("%H:%M:%S")
                except:
                    timestamp_str = ""
            else:
                timestamp_str = ""
            
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(content)
                    if timestamp_str:
                        st.caption(f"⏰ {timestamp_str}")
            
            elif role == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)
                    if timestamp_str:
                        st.caption(f"⏰ {timestamp_str}")
    else:
        st.info(t["no_history"])

st.divider()

# Input area
st.markdown("### 💬 " + t["chat_history"])

# Create columns for input and send button
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        t["input_placeholder"],
        placeholder=t["input_placeholder"],
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("➤", key="send_button", help=t["send"], use_container_width=True)

# Process user input
if send_button and user_input:
    # Add user message to history
    st.session_state.conversation_history.append(
        format_message("user", user_input)
    )
    
    # Get response
    with st.spinner(t["thinking"]):
        response = get_api_response(user_input)
    
    if response:
        # Add assistant message to history
        st.session_state.conversation_history.append(
            format_message("assistant", response)
        )
        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.85em; margin-top: 2rem;'>
    <p>🚀 Advanced AI Chatbot powered by Claude API | 
    <a href='https://www.anthropic.com' target='_blank'>Anthropic</a> | 
    <a href='https://streamlit.io' target='_blank'>Streamlit</a></p>
    <p>© 2026 | Built with ❤️</p>
    </div>
    """,
    unsafe_allow_html=True
)
