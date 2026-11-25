import streamlit as st
import pdfplumber
import chromadb
import requests

# ====== 网页基础设置 ======
st.set_page_config(page_title="泽龙的智能问答助手", page_icon="📚")
st.title("📚 泽龙的专属 PDF 知识库助手")

# ====== 侧边栏：API Key 设置与知识库管理 ======
with st.sidebar:
    st.header("🔑 API Key 设置")
    # 让用户自己输入 Key，type="password" 会让输入的内容变成小黑点
    user_api_key = st.text_input("请输入你的 DeepSeek API Key", type="password")
    st.markdown("[点击这里免费获取 Key](https://platform.deepseek.com/)")
    st.divider()

    # 如果没有输入 Key，直接停止运行！后面的代码全都不执行，绝不扣你的钱。
    if not user_api_key:
        st.info("👈 请先在左侧输入你的 API Key，才能开始提问哦。")
        st.stop()

    # 动态生成请求头（用用户自己的 Key）
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {user_api_key}"
    }

    # ====== 下面是 PDF 上传与解析 ======
    st.header("知识库管理")
    uploaded_file = st.file_uploader("请上传一个 PDF 文件", type=["pdf"])

    if uploaded_file is not None:
        # 如果换了新文件
        if "file_name" not in st.session_state or st.session_state.file_name != uploaded_file.name:
            st.session_state.messages = []  # 清空聊天记录

            with st.spinner("发现新文件，正在重新解析并建立知识库..."):
                all_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            all_text += text

                chunks = []
                chunk_size = 200
                overlap = 20
                start = 0
                while start < len(all_text):
                    chunks.append(all_text[start:start + chunk_size])
                    start += chunk_size - overlap

                client = chromadb.Client()
                # 删旧库防串台
                try:
                    client.delete_collection("my_docs")
                except Exception:
                    pass

                collection = client.create_collection("my_docs")
                collection.add(
                    documents=chunks,
                    ids=[str(i) for i in range(len(chunks))]
                )

                st.session_state.collection = collection
                st.session_state.file_name = uploaded_file.name

            st.success(f"已成功加载：{uploaded_file.name}")

    st.divider()
    # 一键清空对话按钮
    if st.button("🧹 清空对话记录", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # ====== 初始化网页的“记忆” ======
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====== 主界面：展示历史聊天记录 ======
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "context" in msg and msg["context"]:
            with st.expander("查看 AI 参考的原文"):
                st.write(msg["context"])

# ====== 主界面：底部输入框 ======
user_query = st.chat_input("向这份 PDF 提问吧...")

if user_query:
    if "collection" not in st.session_state:
        st.warning("⚠️ 请先在左侧上传 PDF 文件！")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("正在查阅资料并思考..."):
            results = st.session_state.collection.query(query_texts=[user_query], n_results=2)
            context = "\n".join(results['documents'][0])

            prompt = f"""
            你是一个专业的文档分析助手。请严格根据下面提供的【参考资料】来回答用户的问题。
            如果资料里没有答案，请直接说“根据资料无法回答”，绝对不要自己瞎编。

            【参考资料】：
            {context}

            【用户问题】：
            {user_query}
            """

            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }

            # 异常处理：防止余额不足或报错时直接崩溃
            response = requests.post(url, headers=headers, json=data)
            result = response.json()

            if "error" in result:
                st.error(f"API 报错：{result['error'].get('message', '未知错误')}")
                st.stop()

            reply = result["choices"][0]["message"]["content"]

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "context": context
        })

        with st.chat_message("assistant"):
            st.markdown(reply)
            with st.expander("查看 AI 参考的原文"):
                st.write(context)