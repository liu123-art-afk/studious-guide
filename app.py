import streamlit as st
import ollama
import PyPDF2
import pandas as pd
import base64
import os

# --- 1. 网页基础配置 ---
st.set_page_config(page_title="小爱 AI", layout="wide")

# 自定义样式：让侧边栏看起来更高级
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1e1e1e; color: white; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 视频处理函数 (使用你的新路径) ---
def get_video_html(video_path):
    # 检查文件是否存在
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        # 返回带样式的视频 HTML 标签
        return f"""
            <div style="text-align: center;">
                <video width="100%" autoplay loop muted playsinline style="border-radius: 15px; border: 2px solid #4F8BF9;">
                    <source src="data:video/mp4;base64,{b64}" type="video/mp4">
                </video>
            </div>"""
    else:
        return f"<p style='color:red;'>找不到视频文件：{video_path}</p>"

# --- 3. 侧边栏：显示小爱形象 ---
with st.sidebar:
    # 这里使用了你提供的最新路径
    my_video_path = r"D:\AI\assets\Screenrecording_20260510_181319.mp4"
    
    video_tag = get_video_html(my_video_path)
    st.markdown(video_tag, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>我是小爱，你想我了吗？</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # 文档上传区
    uploaded_file = st.file_uploader("投喂文档给小爱 (PDF/Excel)", type=["pdf", "xlsx", "xls"])
    doc_context = ""
    if uploaded_file:
        with st.spinner("正在阅读中..."):
            if uploaded_file.type == "application/pdf":
                reader = PyPDF2.PdfReader(uploaded_file)
                doc_context = "".join([p.extract_text() for p in reader.pages])
            st.success("文档已存入我的大脑！")

# --- 4. 聊天界面逻辑 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "你是万能管家小爱，说话亲切且富有智慧。"}]

# 显示历史消息
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("向小爱提问..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        
        # 整合文档信息和用户问题
        input_content = f"【参考文档】：\n{doc_context}\n\n【用户提问】：{prompt}" if doc_context else prompt
        
        try:
            # 向本地 Ollama 模型发起请求
            res = ollama.chat(model='qwen2.5:7b', 
                             messages=[st.session_state.messages[0], {"role": "user", "content": input_content}], 
                             stream=True)
            for chunk in res:
                full_res += chunk['message']['content']
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
        except Exception as e:
            st.error(f"模型连接失败，请确保 Ollama 已开启。")
    
    st.session_state.messages.append({"role": "assistant", "content": full_res})
