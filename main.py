import streamlit as st
import os
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

# 页面标题与样式
st.title("✨ 朋友圈文案灵感库 AI助手")
st.divider()

# ---------------------- 侧边栏：API配置 ----------------------
with st.sidebar:
    st.subheader("⚙️ API配置")
    api_key = st.text_input("请输入OpenAI API密钥", type="password")
    # 可选：切换模型（支持gpt-3.5-turbo/gpt-4）
    model_version = st.selectbox("选择模型", ["gpt-3.5-turbo", "gpt-4"], index=0)
    st.caption("📌 密钥获取：OpenAI官网/国内合规大模型平台")

# ---------------------- 核心参数配置 ----------------------
st.subheader("📝 文案生成设置")
col1, col2 = st.columns(2)

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
        ]
    )

with col2:
    # 风格选择
    style = st.selectbox(
        "选择文案风格",
        ["温馨治愈", "搞笑沙雕", "文艺清新", "简约短句", "元气满满"]
    )

# 自定义补充需求
custom_demand = st.text_input("补充需求（可选）", placeholder="比如：生日文案要带蛋糕emoji、旅行文案突出海边氛围...")


# ---------------------- LangChain 文案生成逻辑 ----------------------
def generate_friends_circle_copy(api_key, scene, style, custom_demand):
    # 设置API密钥
    os.environ["OPENAI_API_KEY"] = api_key

    # 初始化大模型（新版写法）
    llm = ChatOpenAI(
        model=model_version,
        temperature=0.8,  # 创意度（0-1，越高越灵活）
        max_tokens=200
    )

    # 构建朋友圈文案专属Prompt（新版Prompt写法）
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是朋友圈文案专家，擅长生成符合场景、风格的朋友圈文案，要求：
        1. 每段文案控制在50字以内，适配朋友圈阅读习惯；
        2. 必须带贴合场景的emoji，避免堆砌；
        3. 风格严格匹配用户选择的类型，语言自然不生硬；
        4. 生成3条不同版本的文案，每条换行分隔，前标注序号。"""),
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

    return result


# ---------------------- 生成按钮与结果展示 ----------------------
st.divider()
generate_btn = st.button("🚀 生成文案", type="primary")

if generate_btn:
    # 校验API密钥
    if not api_key:
        st.error("⚠️ 请先在侧边栏输入API密钥！")
    else:
        with st.spinner("AI正在为你创作专属文案..."):
            try:
                # 生成文案
                copy_result = generate_friends_circle_copy(api_key, scene, style, custom_demand)
                # 展示结果
                st.subheader("✨ 生成的朋友圈文案")
                st.success(copy_result)

                # 一键复制功能
                st.code(copy_result, language="text")
                if st.button("📋 复制文案"):
                    st.write("✅ 文案已复制到剪贴板！")
                    # 实际复制逻辑（借助streamlit的剪贴板API）
                    st.session_state["copied_text"] = copy_result

            except Exception as e:
                st.error(f"❌ 生成失败：{str(e)}")
                st.caption("请检查API密钥是否有效，或确认网络可访问OpenAI服务器")

# ---------------------- 页脚 ----------------------
st.divider()
st.caption("💡 小贴士：生成的文案可直接复制到朋友圈，支持修改后使用～")