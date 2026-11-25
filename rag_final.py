import pdfplumber
import chromadb
import requests

# ================= 第一部分：准备知识库 =================
# (这段代码是你今天在 rag_step2 里写过的，直接搬过来)

pdf_path = "test.pdf"
all_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text

def split_text(text, chunk_size=200, overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = start + chunk_size - overlap
    return chunks

chunks = split_text(all_text)

# 把文字存入数据库
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="my_docs")

# 为了不重复写入，我们只在第一次运行时写入（或者这行你可以注释掉，因为之前已经存过了）
if collection.count() == 0:
    collection.add(
        documents=chunks,
        ids=[str(i) for i in range(len(chunks))]
    )

# ================= 第二部分：检索与生成（RAG 核心） =================

# 1. 用户提问
question = "本文件在说什么？" # 你可以换成别的问题

# 2. 去数据库里搜出最相关的 1 块内容
results = collection.query(
    query_texts=[question],
    n_results=3
)
# 提取出搜到的文本（因为结果是个嵌套列表，所以是 results['documents'][0][0]）
context = results['documents'][0][0]
print(f"【系统搜到的参考资料】:\n{context}\n")

# 3. 把搜到的背景资料和用户问题，拼成一段大 Prompt
prompt = f"""
你是一个专业的文档分析助手。请严格根据下面提供的【参考资料】来回答用户的问题。
如果资料里没有答案，请直接说“根据资料无法回答”，绝对不要自己瞎编。

【参考资料】：
{context}

【用户问题】：
{question}
"""

# 4. 发送给大模型（这就是你昨天写的 API 代码，一模一样）
API_KEY = "sk-3399bd020849420895ce0dc8c9a97a95" # 记得换成你自己的
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
url = "https://api.deepseek.com/chat/completions"

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": prompt} # 注意：这里传的是咱们拼好的 prompt
    ]
}

print("正在查阅资料并思考中...")
response = requests.post(url, headers=headers, json=data)
result = response.json()

# 5. 打印结果
reply = result["choices"][0]["message"]["content"]
print("\n--- AI 的回答 ---")
print(reply)