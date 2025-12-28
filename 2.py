import streamlit as st
from openai import OpenAI  # 兼容Kimi/通义千问等大模型API

# 页面配置
st.set_page_config(page_title="B站话题文案生成助手", page_icon="📺", layout="wide")

# ---------------------- 侧边栏：API密钥输入 ----------------------
with st.sidebar:
    st.subheader("API配置")
    api_key = st.text_input(
        "请输入API密钥",
        type="password",  # 隐藏输入
        placeholder="例如：sk-xxxxxx"
    )
    # 显示/隐藏密钥开关
    show_key = st.checkbox("显示API密钥")
    if show_key:
        st.text(api_key)

# ---------------------- 主内容区：B站话题文案生成 ----------------------
st.title("B站话题文案生成助手")
st.write("自动生成符合B站风格的话题文案，支持自定义字数~")

# 1. 话题基本信息输入
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        topic_theme = st.text_input("话题主题", placeholder="例如：Python爬虫实战教程")
        topic_category = st.selectbox("话题分类", ["科技", "学习", "生活", "游戏", "娱乐"])
    with col2:
        word_count = st.slider("文案目标字数", min_value=100, max_value=500, value=200, step=50)
        tone_style = st.selectbox("文案风格", ["轻松活泼", "专业严谨", "幽默搞笑", "干货满满"])

# 2. 生成按钮与结果展示
if st.button("生成B站话题文案", type="primary"):
    # 校验输入
    if not api_key:
        st.error("请先在侧边栏输入API密钥！")
    elif not topic_theme:
        st.error("请输入话题主题！")
    else:
        try:
            with st.spinner("AI正在生成文案..."):
                # 初始化大模型客户端（以Kimi为例，兼容OpenAI接口）
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.moonshot.cn/v1"  # Kimi的API地址
                )

                # 提示词模板：指定B站话题格式+字数+风格
                prompt = f"""
                请生成一篇B站话题文案，要求：
                1. 话题主题：{topic_theme}
                2. 分类：{topic_category}
                3. 字数：{word_count}字左右
                4. 风格：{tone_style}
                5. 格式：包含【话题标题】+【话题简介】+【互动引导】三部分，符合B站用户阅读习惯。
                """

                # 调用大模型
                response = client.chat.completions.create(
                    model="moonshot-v1-8k",  # Kimi模型
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7  # 控制创意度
                )

                # 展示生成结果
                st.subheader("生成的B站话题文案：")
                st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"生成失败：{str(e)}")