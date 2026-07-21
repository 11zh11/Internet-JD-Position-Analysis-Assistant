from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from file_history_store import get_history
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from operator import itemgetter




class RagService():
    def __init__(self):
       
        # 3. 传入修复后的向量实例，初始化向量库服务
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )
        
        # 4. 构建提示词模板
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的岗位分析助手,"
            "以我提供的岗位描述为基础，参考资料；{context}.分析岗位的职责、要求、技能等。"),
            ("system", "并且我提供用户的对话历史，如下："),
            MessagesPlaceholder("history"),
            ("user", "请回答用户的问题：{input}"),
        ])

        # 5. 初始化通义大语言模型（streaming=True 启用逐 token 流式输出）
        self.chat_model = ChatTongyi(model=config.chat_model_name, streaming=True)

        # 6. 组装完整RAG执行链路
        self.chain = self.__get_chain()

    def __get_chain(self):
        # 获取向量检索器，用于根据问题检索相似岗位文档
        retriever = self.vector_service.get_retriever()

        # 检索结果格式化函数：把Document对象拼接成可读文本上下文
        def format_document(docs: list[Document]):
            if not docs:
                return "无相关资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据:{doc.metadata}\n\n"
            return formatted_str

        # ── 流式兼容的内层链 ──
        # 直接接收 {"input": str, "history": list[BaseMessage]}
        # itemgetter("input") 同时作为用户问题和检索输入，避免 RunnableWithMessageHistory 的嵌套转换
        self._stream_chain = (
            {
                "input": itemgetter("input"),
                "context": itemgetter("input") | retriever | format_document,
                "history": itemgetter("history"),
            }
            | self.prompt_template
            | self.chat_model
            | StrOutputParser()
        )

        # ── 带历史管理的链（invoke 用） ──
        conversation_chain = RunnableWithMessageHistory(
            self._stream_chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain

    def stream_response(self, user_input: str, session_config: dict):
        """流式输出，跳过 RunnableWithMessageHistory 手动管理历史"""
        session_id = session_config["configurable"]["session_id"]
        history_store = get_history(session_id)
        history = list(history_store.messages)

        return self._stream_chain.stream(
            {"input": user_input, "history": history}
        )

        
if __name__ == "__main__":
    
    session_config = {
        "configurable": {
        "session_id": "user_001",
        }
    }
    res = RagService().chain.invoke({"input": "请分析以下岗位描述：岗位描述：前端开发"}, session_config)
    print(res)
