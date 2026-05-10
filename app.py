import streamlit as st
import base64
import os
from openai import OpenAI 
client = OpenAI(
    api_key=st.secrets["ZHIPU_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #ffffff !important; }
    [data-testid="stSidebar"] .stMarkdown p { color: #31333F !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏视频 ---
with st.sidebar:
    video_path = os.path.join("assets", "Screenrecording_20260510_181319.mp4")
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            b64_video = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <video width="100%" autoplay loop muted playsinline style="border-radius: 15px;">
                <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
            </video>
        """, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #31333F;'>我是小爱</h2>", unsafe_allow_html=True)

# --- 4. 聊天逻辑 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("说点什么..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="glm-4", 
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True
        )
        full_res = st.write_stream(response)
    st.session_state.messages.append({"role": "assistant", "content": full_res})
