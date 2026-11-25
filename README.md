# 泽龙的专属 PDF 知识库助手

这是一个基于 RAG (检索增强生成) 架构与大语言模型 (DeepSeek) 开发的智能文档问答系统。

## 🚀 在线体验地址
👉 [点击这里立即体验](https://my-rag-pdf-havww566aqnmdvbirl2sum.streamlit.app)

> 💡 体验提示：为了保证数据隐私与安全，本应用采用 BYOK (Bring Your Own Key) 架构，请在左侧输入您自己的 DeepSeek API Key 体验。

## ✨ 核心功能
- **智能解析**：自动提取 PDF 文本并基于滑动窗口进行重叠切块 (Chunk 200, Overlap 20)。
- **语义检索**：使用 ChromaDB 建立本地向量库，精准召回 Top-N 上下文。
- **防幻觉控制**：通过 Prompt Engineering 限制大模型只能基于参考原文回答。
- **回答溯源**：支持展开查看 AI 参考的原文段落，做到有据可查。
- **工程安全**：采用 BYOK 模式，不存储服务端密钥，保证部署安全。
