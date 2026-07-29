# Internet-JD-Position-Analysis-Assistant
互联网岗位分析助手，环境配置后直接运行app_qa.py
技术栈：Python ， Claude code ， Embedding ， ChromaDB ， PromptTemplate ， LangChain
项目简介：
独立设计并实现了一个基于RAG 架构的岗位智能问答系统
搭建了文档分块→ 向量嵌入→相似检索→ LLM 生成的完整 RAG 管道
集成阿里 Dash Scope 与通义千问 Qwen3-Max 模型 ，实现流式对话问答
实现了 MD5 去重、多会话隔离、本地持久化等工程化特性技术亮点技术亮点：
1.完整RAG管道自建 ：从文档分块 → 向量嵌入 → 向量检索引擎 → Prompt 模板构建 → LLM调用 ，全程自主搭建 ，未使用第三方 "一键式 "RAG 服务
2.工程化细节： MD5去重防止重复入库、 Dash Scope API兼容性处理、会话隔离的JSON文件存储
3.流式响应兼容 ：针对 LangChain RunnableWith MessageHistory 流式支持不佳的问题手动管理历史消息实现 streaming
4.UI 体验优化： CSS 自定义实现聊天输入框浮动固定底部、消息区域自适应填充等细节
