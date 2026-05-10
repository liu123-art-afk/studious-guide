import streamlit as st
import base64
import os
from openai import OpenAI # 改用 OpenAI 格式调用云端 API

# --- 1. 配置云端 API (灵积/通义千问) ---
# 这里的 DASHSCOPE_API_KEY 稍后在 Streamlit 网页后台设置
client = OpenAI(
    api_key=st.secrets["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# --- 2. 侧边栏：白色背景与视频 ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #ffffff !important; color: #31333F; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    # 注意：云端路径要用相对路径
    video_path = os.path.join("assets", "Screenrecording_20260510_181319.mp4")
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <video width="100%" autoplay loop muted playsinline style="border-radius:15px;">
                <source src="data:video/mp4;base64,{b64}" type="video/mp4">
            </video>
        """, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>我是小爱</h2>", unsafe_allow_html=True)

# --- 3. 聊天逻辑 ---
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
            model="qwen-plus", # 云端模型名称
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True
        )
        full_res = st.write_stream(response)
    st.session_state.messages.append({"role": "assistant", "content": full_res})
