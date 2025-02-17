import streamlit as st
import replicate
import os
import time
from streamlit.components.v1 import html

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="🚀 Llama 2 UltraChat",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Custom CSS --------------------
def inject_custom_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        
        /* Base styles */
        body, .stChatContainer, .stSidebar {{
            font-family: 'Inter', sans-serif;
            background-color: #f9fafb;
        }}
        
        /* Modern chat container */
        .main .block-container {{
            max-width: 80rem;
            padding: 2rem 1rem;
        }}
        
        /* Messages styling */
        .stChatMessage {{
            margin: 1.5rem 0;
            border-radius: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }}
        
        .stChatMessage:hover {{
            transform: translateY(-2px);
        }}
        
        [data-testid="user"] {{
            background: #ffffff;
            border-left: 4px solid #6366f1;
            margin-left: 10%;
        }}
        
        [data-testid="assistant"] {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-left: 4px solid #10b981;
            margin-right: 10%;
        }}
        
        /* Modern sidebar */
        .stSidebar {{
            background: linear-gradient(195deg, #1e1e2f, #252542);
            box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
        }}
        
        .stSidebar .stMarkdown h1 {{
            color: #fff;
            font-size: 1.8rem;
            margin-bottom: 2rem;
        }}
        
        /* Animated input */
        .stTextInput input {{
            border-radius: 1rem !important;
            padding: 1rem !important;
            transition: all 0.3s ease !important;
            border: 2px solid #e5e7eb !important;
        }}
        
        .stTextInput input:focus {{
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        }}
        
        /* Pulse animation */
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        
        /* Floating animation */
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-5px); }}
            100% {{ transform: translateY(0px); }}
        }}
        
        /* Enhanced buttons */
        .stButton button {{
            background: linear-gradient(45deg, #6366f1, #8b5cf6);
            border-radius: 0.75rem;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
        
        /* Loading spinner */
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .custom-spinner {{
            display: inline-block;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(99, 102, 241, 0.2);
            border-radius: 50%;
            border-top-color: #6366f1;
            animation: spin 1s ease-in-out infinite;
        }}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# -------------------- API Key Handling --------------------
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
    # Thêm model mới ở đây
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
# -------------------- Model Settings --------------------
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
    """Generate response with streaming"""
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
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": time.time()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕒 {time.strftime('%H:%M:%S')}")

    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ''
        
        with st.spinner(""):
            try:
                response = generate_response(prompt)
                
                # Typewriter effect đơn giản
                for chunk in response.split():
                    full_response += chunk + " "
                    response_placeholder.markdown(f"""
                    <div style="color: white;">
                        {full_response}▌
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.03)
                
                # Hiển thị cuối cùng
                response_placeholder.markdown(f"""
                <div style="color: white;">
                    {full_response}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
                full_response = "⚠️ Sorry, I encountered an error. Please try again."

    # Add to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "timestamp": time.time()
    })

# -------------------- Sidebar Controls --------------------
with st.sidebar:
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear History", help="Clear chat history"):
            st.session_state.messages = [{
                "role": "assistant", 
                "content": "Hello! I'm your advanced AI assistant. How can I help you today?",
                "timestamp": time.time()
            }]
            st.rerun()
    
    with col2:
        if st.button("🔄 New Session", help="Start fresh conversation"):
            st.session_state.clear()
            st.rerun()

    st.markdown("""
    <div style="margin-top: 2rem; text-align: center;">
        <small>Create by MinHiuLe 👨🏻‍💻</small>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Performance Enhancements --------------------
@st.cache_resource
def preload_assets():
    # Preload any necessary assets
    pass

preload_assets()