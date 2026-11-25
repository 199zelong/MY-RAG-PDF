# 前面的代码（提取 PDF 和切块）原封不动复制在这里
import pdfplumber

# 1. 打开 PDF 文件
pdf_path = "test.pdf" # 确保这个文件和你的代码在同一个文件夹里

# 2. 创建一个空字符串，用来装所有的文字
all_text = ""

# 3. 用 with 语句打开 PDF（这相当于 C 语言里的 fopen，用完会自动关闭防泄露）
with pdfplumber.open(pdf_path) as pdf:
    # 遍历 PDF 的每一页
    for page in pdf.pages:
        # 提取当前页的文字
        text = page.extract_text()
        if text: # 如果这页有字
            all_text += text # 拼接到大字符串里

# 4. 打印看看抠出来了多少字
print(f"一共提取了 {len(all_text)} 个字。")
print("前 500 个字的内容是：\n")
print(all_text[:500]) # 切片，只打印前500个字看看效果
def split_text(text, chunk_size=200, overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        # 结束位置 = 开始位置 + 块大小
        end = start + chunk_size
        # 切片取出这一块
        chunk = text[start:end]
        chunks.append(chunk)
        # 下一次开始的位置，要减去重叠部分（防止断句）
        start = start + chunk_size - overlap
    return chunks

# 调用函数，把 all_text 切碎
chunks = split_text(all_text)

# 打印看看切成了多少块
print(f"\n一共切成了 {len(chunks)} 块。")
print("第一块的内容是：\n", chunks[0])
print("第二块的内容是：\n", chunks[1])
# 现在你的 chunks 列表里已经装满了切好的文本块

# ====== 下面是今天的新内容 ======

import chromadb

# 1. 创建一个本地数据库客户端，数据会存在当前目录的 chroma_db 文件夹里
client = chromadb.PersistentClient(path="./chroma_db")

# 2. 创建一个“集合”（相当于数据库里的一张表），名字叫 "my_docs"
collection = client.get_or_create_collection(name="my_docs")

# 3. 把我们的文本块存进去！
# 注意：Chroma 会默认调用它内置的模型帮你把文字转成向量，不用你手动算！
collection.add(
    documents=chunks,               # 要存入的文本内容
    ids=[str(i) for i in range(len(chunks))]  # 给每个块编个号，不能重复，这里用 '0', '1', '2'...
)

print(f"成功存入数据库！当前数据库里有 {collection.count()} 条记录。")
# 假装用户提了一个问题
query_text = "这四问的核心求解器是什么？" # 你可以根据你PDF的内容随便改个问题

print(f"\n用户提问：{query_text}")
print("正在数据库中搜索最相关的片段...\n")

# 让数据库去搜索最相关的 2 个块
results = collection.query(
    query_texts=[query_text], # 要查的问题
    n_results=2               # 只要最相似的 2 个结果
)

# 打印搜索结果（又是拆字典的时候了！）
print("--- 搜索结果 ---")
# 观察一下 results 的结构，它是字典，里面的 'documents' 是个嵌套列表
for i in range(len(results['documents'][0])):
    print(f"\n【最相关的第 {i+1} 块内容】:\n{results['documents'][0][i]}")