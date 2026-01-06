import streamlit as st
import os
import random
import string
# 新版LangChain导入方式（适配v0.1+）
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ---------------------- 页面基础配置 ----------------------
st.set_page_config(
    page_title="朋友圈文案灵感库",
    page_icon="✨",
    layout="centered"
)

# 自定义样式优化
st.markdown("""
<style>
/* 按钮样式优化 */
.stButton > button {
    border-radius: 8px;
    height: 40px;
    font-weight: 500;
}
/* 主按钮样式 */
.stButton > button[data-testid="baseButton-primary"] {
    background-color: #8b5cf6;
    color: white;
}
/* 输入框/选择框样式 */
.stSelectbox > div > div, .stTextInput > div > div {
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}
/* 结果展示样式 */
.stSuccess {
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #d1d5db;
}
/* 代码块样式 */
.stCodeBlock {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "copied_text" not in st.session_state:
    st.session_state.copied_text = ""
if "btn_counter" not in st.session_state:
    st.session_state.btn_counter = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# 页面标题与样式
st.title("✨ 朋友圈文案灵感库 AI助手")
st.divider()

# ---------------------- 侧边栏：Kimi API配置 ----------------------
with st.sidebar:
    st.subheader("⚙️ Kimi API配置")
    api_key = st.text_input(
        "请输入Kimi API密钥",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        help="从月之暗面平台获取：https://platform.moonshot.cn/console/api-keys"
    )

    # Kimi模型选择（适配moonshot系列）
    model_version = st.selectbox(
        "选择Kimi模型",
        ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        index=0,
        help="8k/32k/128k代表上下文长度，越长支持更复杂的生成"
    )

    st.divider()
    st.subheader("📌 使用说明")
    st.markdown("""
    1. 输入从月之暗面获取的API密钥
    2. 选择文案场景和风格
    3. 可填写补充需求（如emoji、重点等）
    4. 点击生成按钮获取文案

    💡 密钥获取：
    - 访问 https://platform.moonshot.cn 注册登录
    - 进入「API密钥管理」生成你的API Key
    """)
    st.caption("© 2025 朋友圈文案AI助手 | 基于Kimi AI")

# ---------------------- 核心参数配置 ----------------------
st.subheader("📝 文案生成设置")
col1, col2 = st.columns(2, gap="medium")

with col1:
    # 场景分类
    scene = st.selectbox(
        "选择文案场景",
        [
            "节日文案（春节/中秋/圣诞/情人节等）",
            "日常分享-美食",
            "日常分享-旅行",
            "日常分享-心情（开心/emo/治愈）",
            "日常分享-职场（加班/摸鱼/成就感）",
            "纪念日（生日/恋爱/入职）",
            "社交互动（朋友圈回复/求点赞）"
        ],
        help="选择贴合你要分享的场景类型"
    )

with col2:
    # 风格选择
    style = st.selectbox(
        "选择文案风格",
        ["温馨治愈", "搞笑沙雕", "文艺清新", "简约短句", "元气满满"],
        help="选择文案的整体语气和风格"
    )

# 自定义补充需求
custom_demand = st.text_input(
    "补充需求（可选）",
    placeholder="比如：生日文案要带蛋糕emoji、旅行文案突出海边氛围...",
    help="填写特殊要求，让文案更贴合你的需求"
)


# ---------------------- 工具函数 ----------------------
def generate_unique_key(prefix):
    """生成唯一按钮key，避免DuplicateWidgetID错误"""
    st.session_state.btn_counter += 1
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{st.session_state.btn_counter}_{rand_str}"


def copy_to_clipboard(text):
    """实现真正的剪贴板复制功能"""
    # 处理特殊字符，避免JavaScript报错
    safe_text = text.replace("`", "\\`").replace("\n", "\\n").replace("'", "\\'")
    # 使用JavaScript实现剪贴板复制
    js_code = f"""
    <script>
    navigator.clipboard.writeText(`{safe_text}`)
    .then(() => {{
        alert('✅ 文案已成功复制到剪贴板！');
    }})
    .catch((err) => {{
        alert('❌ 复制失败，请手动复制：' + err);
    }});
    </script>
    """
    st.write(js_code, unsafe_allow_html=True)


# ---------------------- Kimi API 文案生成逻辑 ----------------------
def generate_friends_circle_copy(api_key, scene, style, custom_demand, model_version):
    """适配Kimi API的朋友圈文案生成函数"""
    try:
        # 初始化Kimi大模型（关键适配：API Base + 模型名称）
        llm = ChatOpenAI(
            model=model_version,  # Kimi模型名称
            openai_api_key=api_key,  # Kimi API Key
            openai_api_base="https://api.moonshot.cn/v1",  # Kimi API地址
            temperature=0.8,  # 创意度（0-1，越高越灵活）
            max_tokens=500,  # 生成最大Token数
            timeout=60,  # 超时时间
            max_retries=2  # 重试次数
        )

        # 构建朋友圈文案专属Prompt（优化版）
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是朋友圈文案专家，擅长生成符合场景、风格的朋友圈文案，要求：
1. 每段文案控制在50字以内，适配朋友圈阅读习惯；
2. 必须带贴合场景的emoji，避免堆砌，每个文案1-2个即可；
3. 风格严格匹配用户选择的类型，语言自然不生硬，符合朋友圈语境；
4. 生成3条不同版本的文案，每条换行分隔，前标注序号（1. 2. 3.）；
5. 避免使用过于网络流行的词汇，保持自然亲切的语气。"""),
            ("user", "场景：{scene}\n风格：{style}\n补充需求：{custom_demand}")
        ])

        # 链式调用（新版Chain写法）
        chain = prompt | llm | StrOutputParser()

        # 执行生成
        result = chain.invoke({
            "scene": scene,
            "style": style,
            "custom_demand": custom_demand if custom_demand else "无特殊要求"
        })

        return result, None

    except Exception as e:
        error_msg = f"""
        ❌ 生成失败：{str(e)}
        📌 排查建议：
        1. 检查API Key是否正确（以sk-开头）
        2. 确认API Key有足够的调用额度
        3. 检查网络是否能访问 https://api.moonshot.cn
        4. 确认模型名称选择正确（moonshot-v1-8k/32k/128k）
        """
        return None, error_msg


# ---------------------- 生成按钮与结果展示 ----------------------
st.divider()
generate_btn = st.button("🚀 生成文案", type="primary", use_container_width=True)

if generate_btn:
    # 校验API密钥
    if not api_key:
        st.error("⚠️ 请先在侧边栏输入Kimi API密钥！")
    else:
        with st.spinner("🤖 Kimi AI正在为你创作专属文案..."):
            # 生成文案
            copy_result, error = generate_friends_circle_copy(
                api_key, scene, style, custom_demand, model_version
            )

            if copy_result:
                # 保存结果到会话状态
                st.session_state.last_result = copy_result

                # 展示结果
                st.subheader("✨ 生成的朋友圈文案")
                st.success(copy_result)

                # 一键复制功能
                st.divider()
                col_copy, col_empty = st.columns([1, 5])
                with col_copy:
                    st.button(
                        "📋 复制全部文案",
                        key=generate_unique_key("copy_btn"),
                        on_click=copy_to_clipboard,
                        args=(copy_result,),
                        use_container_width=True
                    )
            else:
                # 展示错误信息
                st.error(error)

# 展示历史生成结果（如果有）
if st.session_state.last_result and not generate_btn:
    st.subheader("✨ 上次生成的文案")
    st.info(st.session_state.last_result)
    st.divider()
    col_copy, col_empty = st.columns([1, 5])
    with col_copy:
        st.button(
            "📋 复制文案",
            key=generate_unique_key("copy_history_btn"),
            on_click=copy_to_clipboard,
            args=(st.session_state.last_result,),
            use_container_width=True
        )

# ---------------------- 页脚 ----------------------
st.divider()
st.caption("💡 小贴士：生成的文案可直接复制到朋友圈，支持修改后使用～ |  Powered by Kimi AI")
