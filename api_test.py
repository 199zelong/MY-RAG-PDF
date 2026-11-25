import requests
import json

# 1. 准备你的 API Key（把下面引号里的内容换成你自己的）
API_KEY = "sk-3399bd020849420895ce0dc8c9a97a95"

# 2. 准备你昨天写的聊天记录（数据格式你已经学过了）
messages = [
    {"role": "user", "content": "我叫泽龙，今年大三，在找实习"},
    {"role": "assistant", "content": "你好泽龙！大三找实习非常合适，祝你顺利。"}, # 这是你伪造的上一轮AI的回答
    {"role": "user", "content": "请问我叫什么？我今年大几？在干什么？"} # 这是你现在问的
]

# 3. 构造请求头（相当于你的通行证）
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"  # 这里用到了昨天教的 f-string
}

# 4. 构造请求体（你要发给大模型的具体参数）
# 注意：DeepSeek 的模型名字叫 "deepseek-chat"
data = {
    "model": "deepseek-chat",
    "messages": messages
}

# 5. 发送 POST 请求（去敲大模型的门）
print("正在呼叫大模型，请稍候...")
# 这里填的是 DeepSeek 的 API 地址。如果你用智谱，地址和 model 名字不一样。
url = "https://api.deepseek.com/chat/completions"
response = requests.post(url, headers=headers, json=data)

# 6. 接收大模型的回复（返回的是 JSON 格式，也就是字典）
# 这里的 response.json() 会把服务器返回的死字符串，自动变成 Python 的字典
result = response.json()
print("服务器返回的原始数据：")
print(result)

# 7. 提取大模型说的话（重点！结合你昨天学的字典和列表知识）
# 你自己尝试写出提取回复的代码！
# 提示：大模型回复的内容藏在 result["choices"][0]["message"]["content"] 里
reply = result["choices"][0]["message"]["content"]
print("AI 的回答：", reply)
print("这次对话总共消耗了token:",result["usage"]["total_tokens"])