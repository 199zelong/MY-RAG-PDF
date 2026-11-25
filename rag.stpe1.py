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