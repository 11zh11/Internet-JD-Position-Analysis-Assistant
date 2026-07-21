"""
app_qa.py — 互联网岗位分析助手
基于 Streamlit 整合知识库上传 + RAG 智能问答的一站式前端
"""

import time
import uuid

import streamlit as st
from knowledge_base import KnowledgeBaseService
from rag import RagService

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="互联网岗位分析助手",
    page_icon="💼",
    layout="wide",
)

# ============================================================
# 自定义 CSS：聊天区域撑满视口，输入框固定在底部
# ============================================================
st.markdown(
    """
<style>
/* 主内容区撑满视口 */
.main .block-container {
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 4rem);
    padding-bottom: 80px;  /* 给底部浮动输入框留空间 */
}

/* 聊天区自动填充剩余高度 */
section[data-testid="stMain"] .block-container > *:last-child {
    margin-bottom: 0;
}

/* 浮动输入框容器固定在页面底部 */
[data-testid="stChatFloatingInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: linear-gradient(0deg, var(--background-color) 80%, transparent 100%) !important;
    padding: 0.5rem 1rem 1rem 1rem !important;
    z-index: 999 !important;
}

/* 输入框宽度适配侧边栏 */
[data-testid="stChatFloatingInputContainer"] > div {
    max-width: 48rem;
    margin: 0 auto;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 初始化 session_state（只执行一次）
# ============================================================
if "kb_service" not in st.session_state:
    st.session_state["kb_service"] = KnowledgeBaseService()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"session_{uuid.uuid4().hex[:12]}"

if "rag_service" not in st.session_state:
    with st.spinner("正在初始化 RAG 服务，请稍候…"):
        st.session_state["rag_service"] = RagService()

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


def get_session_config():
    """返回当前会话的 LangChain 配置"""
    return {"configurable": {"session_id": st.session_state["session_id"]}}


# ============================================================
# 侧边栏：导航 + 会话管理
# ============================================================
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/briefcase.png",
        width=64,
    )
    st.title("💼 岗位分析助手")

    st.divider()

    # ---- 页面导航 ----
    page = st.radio(
        "📌 导航",
        ["📁 知识库上传", "💬 智能问答"],
        label_visibility="collapsed",
    )

    st.divider()

    # 会话信息
    st.caption(f"📌 会话 ID")
    st.code(st.session_state["session_id"], language=None)

    # 新建会话
    if st.button("🔄 新建会话", use_container_width=True):
        st.session_state["session_id"] = f"session_{uuid.uuid4().hex[:12]}"
        st.session_state["chat_messages"] = []
        st.rerun()

    # 清空当前会话聊天记录
    if st.button("🗑️ 清空聊天记录", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.rerun()

    st.divider()

    # 使用说明
    with st.expander("📖 使用说明"):
        st.markdown("""
        **知识库上传**
        1. 切换到「📁 知识库上传」页
        2. 上传岗位描述 .txt 文件
        3. 系统自动向量化并入库

        **智能问答**
        1. 切换到「💬 智能问答」页
        2. 输入岗位相关问题
        3. AI 基于知识库内容回答
        """)

    st.divider()
    st.caption("Powered by Tongyi Qwen · Chroma · LangChain")


# ============================================================
# 页面 1：知识库上传
# ============================================================
if page == "📁 知识库上传":
    st.header("📁 知识库上传")
    st.caption("上传岗位描述 TXT 文件，系统将自动分块并存入向量知识库")

    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        uploaded_file = st.file_uploader(
            "请上传 TXT 文件",
            type=["txt"],
            accept_multiple_files=False,
            help="支持单个 .txt 文件，内容将被自动分块并向量化存储",
        )

        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_size = uploaded_file.size / 1024  # KB

            st.divider()
            st.subheader("📄 文件信息")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("文件名", file_name)
            with col2:
                st.metric("文件大小", f"{file_size:.2f} KB")

            # 文件内容预览
            text_content = uploaded_file.getvalue().decode("utf-8")
            with st.expander("🔍 内容预览（前 500 字）"):
                st.text(text_content[:500] + ("..." if len(text_content) > 500 else ""))

            # 上传按钮
            if st.button("🚀 上传到知识库", type="primary", use_container_width=True):
                with st.spinner("正在处理并载入知识库…"):
                    time.sleep(0.5)
                    result = st.session_state["kb_service"].upload_by_str(
                        text_content, file_name
                    )
                    if "成功" in result:
                        st.success(f"✅ {result}")
                        st.balloons()
                    elif "已存在" in result:
                        st.info(f"ℹ️ {result}")
                    else:
                        st.warning(f"⚠️ {result}")

    with col_right:
        st.subheader("📋 上传须知")
        st.info(
            """
        **支持格式**：`.txt` 纯文本文件

        **处理流程**：
        1. MD5 去重校验
        2. 文本智能分块（1000 字/块，100 字重叠）
        3. DashScope 向量化
        4. 存入 Chroma 向量库

        **去重规则**：相同内容的文件不会重复入库
        """
        )

        with st.expander("⚙️ 当前配置"):
            import config_data as config

            st.caption(f"知识库名称：`{config.collection_name}`")
            st.caption(f"分块大小：{config.chunk_size} 字符")
            st.caption(f"重叠大小：{config.chunk_overlap} 字符")
            st.caption(f"向量模型：`{config.embedding_model_name}`")
            st.caption(f"对话模型：`{config.chat_model_name}`")
            st.caption(f"检索条数：Top-{config.similarity_threshold}")

# ============================================================
# 页面 2：智能问答
# ============================================================
else:
    st.header("💬 智能问答")
    st.caption("基于已上传的岗位描述文档，向 AI 提问岗位分析相关问题")

    # 渲染历史消息
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框在页面顶层渲染 → 自动浮动到视口底部
    user_input = st.chat_input("请输入你的问题，例如：「互联网开发岗位需要什么技能？」")

    if user_input:
        # 1. 展示用户消息
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. 流式调用 RAG 并展示回答
        with st.chat_message("assistant"):
            try:
                stream = st.session_state["rag_service"].stream_response(
                    user_input,
                    get_session_config(),
                )
                # 手动流式：逐个 token 追加并刷新渲染
                placeholder = st.empty()
                full_response = ""
                for chunk in stream:
                    full_response += chunk  # chunk 已是 str
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.session_state["chat_messages"].append(
                    {"role": "assistant", "content": full_response}
                )
            except Exception as e:
                error_msg = f"❌ 出错了：{str(e)}"
                st.error(error_msg)
                st.session_state["chat_messages"].append(
                    {"role": "assistant", "content": f"⚠️ 系统错误：{e}"}
                )
