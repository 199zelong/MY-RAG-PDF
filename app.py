import streamlit as st
import pdfplumber
import chromadb
import requests

# ====== 网页基础设置 ======
st.set_page_config(page_title="泽龙的智能问答助手", page_icon="📚")
st.title("📚 泽龙的专属 PDF 知识库助手")

# 你的 API Key (记得换成你自己的)
API_KEY = st.secrets["API_KEY"]
url = "https://api.deepseek.com/chat/completions"
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

# 初始化网页的“记忆”
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====== 侧边栏：知识库管理 ======
with st.sidebar:
    st.header("知识库管理")
    uploaded_file = st.file_uploader("请上传一个 PDF 文件", type=["pdf"])

    # 核心判断：如果上传了新文件
    if uploaded_file is not None:
        # 如果背包里没存过文件名，或者当前文件名和背包里存的不一样（说明换文件了）
        if "file_name" not in st.session_state or st.session_state.file_name != uploaded_file.name:

            # 1. 换文件时，自动清空之前的聊天记录
            st.session_state.messages = []

            with st.spinner("发现新文件，正在重新解析并建立知识库..."):
                # 2. 提取文字
                all_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            all_text += text

                # 3. 切块
                chunks = []
                chunk_size = 200
                overlap = 20
                start = 0
                while start < len(all_text):
                    chunks.append(all_text[start:start + chunk_size])
                    start += chunk_size - overlap

                # 4. 存入临时内存数据库
                client = chromadb.Client()

                # ==========================================
                # 🚨 修复 Bug 的核心代码在这里！
                # 每次建新库前，先尝试把旧的 "my_docs" 删掉，防止新旧数据混合
                try:
                    client.delete_collection("my_docs")
                except Exception:
                    pass  # 如果本来就没有旧库，报错也不管
                # ==========================================

                collection = client.create_collection("my_docs")
                collection.add(
                    documents=chunks,
                    ids=[str(i) for i in range(len(chunks))]
                )

                # 5. 把新数据和文件名存入背包
                st.session_state.collection = collection
                st.session_state.file_name = uploaded_file.name

            st.success(f"已成功加载：{uploaded_file.name}")

    st.divider()
    # 一键清空对话按钮
    if st.button("🧹 清空对话记录", use_container_width=True):
        st.session_state.messages = []
        st.rerun()  # 强制刷新网页

# ====== 主界面：展示历史聊天记录 ======
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 如果在历史记录中找到了参考原文，也把它展示出来
        if "context" in msg and msg["context"]:
            with st.expander("查看 AI 参考的原文"):
                st.write(msg["context"])

# ====== 主界面：底部输入框 ======
user_query = st.chat_input("向这份 PDF 提问吧...")

if user_query:
    if "collection" not in st.session_state:
        st.warning("⚠️ 请先在左侧上传 PDF 文件！")
    else:
        # 1. 显示用户问题并存入记忆
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # 2. 去数据库检索
        with st.spinner("正在查阅资料并思考..."):
            results = st.session_state.collection.query(query_texts=[user_query], n_results=2)
            context = "\n".join(results['documents'][0])

            # 3. 组装 Prompt
            prompt = f"""
            你是一个专业的文档分析助手。请严格根据下面提供的【参考资料】来回答用户的问题。
            如果资料里没有答案，请直接说“根据资料无法回答”，绝对不要自己瞎编。

            【参考资料】：
            {context}

            【用户问题】：
            {user_query}
            """

            # 4. 发送请求
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }

            response = requests.post(url, headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]

        # 5. 显示 AI 回答并存入记忆
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "context": context
        })

        with st.chat_message("assistant"):
            st.markdown(reply)
            with st.expander("查看 AI 参考的原文"):
                st.write(context)