import streamlit as st
import replicate
import os
import time
from streamlit.components.v1 import html

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Chatbot",
    page_icon="💬 ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Load Custom CSS --------------------
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -------------------- Sidebar: Title, API Key & New Chat --------------------
with st.sidebar:
    st.markdown("""
    <div style="animation: float 3s ease-in-out infinite;">
        <h1 style="color: white; text-align: center;">🚀 Chatbot</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input(
            'Enter Replicate API Token:',
            type='password',
            help="Get your API key from https://replicate.com/account"
        )
        if replicate_api:
            if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
                st.error('❌ Invalid API Key!')
                st.stop()
            else:
                st.success('🔑 Authentication Successful')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    if st.button("💬 New Chat", help="Start fresh conversation", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your advanced AI assistant. How can I help you today?",
            "timestamp": time.time()
        }]
        st.rerun()

# -------------------- Model Config --------------------
MODEL_CONFIG = {
    'Llama2-7B': {
        'version': 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea',
        'badge': '⚡ Fast Inference',
        'color': '#10b981'
    },
    'Llama2-13B': {
        'version': 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5',
        'badge': '🎯 High Accuracy', 
        'color': '#3b82f6'
    },
    'Mistral-7B': {
        'version': 'mistralai/mistral-7b-instruct-v0.1:83b6a56e7c828e667f21fd596c338fd4f0039b46bcfa18d973e8e70e455fda70',
        'badge': '🌟 Latest Model',
        'color': '#f59e0b'
    },
    'Falcon-40B': {
        'version': 'tiiuae/falcon-40b-instruct:1e7b3b7c7453128b8b6a430eb788a8efa4a3c70d39887a9a3cf41c8c1ff37d00',
        'badge': '🚀 Powerful',
        'color': '#8b5cf6'
    }
}

# -------------------- Sidebar: Model Settings --------------------
with st.sidebar:
    st.subheader('⚙️ Model Settings')
    
    selected_model = st.radio(
        'Select Model:',
        list(MODEL_CONFIG.keys()),
        format_func=lambda x: f"{x} {MODEL_CONFIG[x]['badge']}",
        help="Choose between speed and accuracy"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            'Temperature 🌡️',
            0.01, 1.0, 0.7,
            help="Control randomness (lower = more deterministic)"
        )
    with col2:
        top_p = st.slider(
            'Top-p 🎯',
            0.01, 1.0, 0.9,
            help="Control diversity via nucleus sampling"
        )
    
    max_length = st.slider(
        'Max Length 📏',
        50, 500, 250,
        help="Maximum response length in tokens"
    )
    st.markdown("""
    <div class="footer">
        <small>Create by MinHiuLe 👨🏻‍💻</small>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Chat History --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your advanced AI assistant. How can I help you today?",
        "timestamp": time.time()
    }]

# -------------------- Chat Display --------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        st.caption(f"🕒 {time.strftime('%H:%M:%S', time.localtime(msg['timestamp']))}")

# -------------------- Response Generation --------------------
@st.cache_data(show_spinner=False)
def generate_response(prompt: str) -> str:
    prompt_template = f"""
    [INST]<<SYS>>
    You are a helpful, respectful, and honest assistant. 
    Provide concise, well-structured answers with markdown formatting when appropriate.
    <</SYS>>
    {prompt}[/INST]
    """
    
    response = replicate.run(
        MODEL_CONFIG[selected_model]['version'],
        input={
            "prompt": prompt_template,
            "temperature": temperature,
            "top_p": top_p,
            "max_length": max_length,
            "repetition_penalty": 1.2
        }
    )
    
    return ''.join(response)

# -------------------- Input Handling --------------------
if prompt := st.chat_input("Ask me anything...", disabled=not replicate_api):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": time.time()
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕒 {time.strftime('%H:%M:%S')}")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ''
        
        with st.spinner(""):
            try:
                response = generate_response(prompt)
                
                for chunk in response.split():
                    full_response += chunk + " "
                    response_placeholder.markdown(f"""
                    <div style="color: white;">
                        {full_response}▌
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.03)
                
                response_placeholder.markdown(f"""
                <div style="color: white;">
                    {full_response}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
                full_response = "⚠️ Sorry, I encountered an error. Please try again."
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "timestamp": time.time()
    })

# -------------------- Performance Enhancements --------------------
@st.cache_resource
def preload_assets():
    pass

preload_assets()