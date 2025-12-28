import streamlit as st
import requests
import json
from datetime import datetime

# ====================== 页面配置 ======================
st.set_page_config(
    page_title="B站热门话题AI创作助手",
    page_icon="📺",
    layout="wide"
)

# ====================== 初始化会话状态 ======================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""


# ====================== 核心API函数 ======================
def generate_bilibili_content(api_key, theme, style, length, category):
    """调用Kimi API生成B站话题文案"""

    # 根据长度选择token数
    length_map = {
        "短（150字内）": 400,
        "中（300字）": 700,
        "长（500字）": 1200
    }

    # 构建系统提示
    system_prompt = """你是一名B站热门话题创作专家，精通各种风格和品类的内容创作。请按照以下要求生成文案：
1. 生成5个吸引人的标题，每个标题包含B站特色符号或emoji，不超过25字
2. 撰写正文，分段清晰，段落不宜过长，使用B站用户熟悉的表达
3. 正文中适当添加emoji或特殊符号增强表现力
4. 在结尾添加5个相关话题标签，格式如：#话题标签#
5. 直接输出文案内容，不要有任何解释或说明
"""

    # 构建用户提示
    user_prompt = f"""请创作一篇关于【{theme}】的B站话题文案。

具体要求：
1. 文案风格：{style}
2. 文案长度：{length}
3. 内容品类：{category}
4. 使用B站流行语：如"前方高能"、"awsl"、"yyds"、"一键三连"等
5. 语气符合B站社区氛围，亲切有活力
"""

    try:
        # 调用Kimi API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": length_map.get(length, 700),
            "stream": False
        }

        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"API调用失败: {response.status_code}\n{response.text}"

    except Exception as e:
        return f"生成失败: {str(e)}"


# ====================== 侧边栏 ======================
with st.sidebar:
    st.title("⚙️ 配置")

    # API Key输入
    api_key = st.text_input(
        "Kimi API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="输入您的Kimi API Key",
        help="请从 https://platform.moonshot.cn 获取API Key"
    )

    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ API Key已保存")

    st.divider()

    # 清空历史
    if st.button("🗑️ 清空历史记录", use_container_width=True):
        st.session_state.chat_history = []
        st.success("历史记录已清空")
        st.rerun()

    st.divider()

    # 使用说明
    st.markdown("### 💡 使用说明")
    st.markdown("""
    1. 输入Kimi API Key
    2. 设置创作参数
    3. 输入主题
    4. 点击生成按钮
    5. 查看历史记录
    """)

# ====================== 主界面 ======================
st.title("📺 B站热门话题AI创作助手")
st.markdown("### 一键生成高互动的B站热门话题文案")

st.divider()

# 检查API Key
if not st.session_state.api_key:
    st.warning("⚠️ 请先在左侧输入Kimi API Key")
    st.info("API Key获取地址: https://platform.moonshot.cn/console/api-keys")
    st.stop()

# 创作参数
st.subheader("🎯 设置创作参数")

col1, col2, col3, col4 = st.columns(4)

with col1:
    theme = st.text_input(
        "创作主题",
        placeholder="例如：新番推荐、游戏攻略、科技评测、生活vlog",
        help="输入你想要创作的核心主题"
    )

with col2:
    style = st.selectbox(
        "文案风格",
        ["吐槽", "科普", "测评", "剧情解析", "搞笑", "治愈", "教程", "盘点"],
        help="选择文案的风格调性"
    )

with col3:
    length = st.selectbox(
        "文案长度",
        ["短（150字内）", "中（300字）", "长（500字）"],
        help="控制文案的详细程度"
    )

with col4:
    category = st.selectbox(
        "内容品类",
        ["动画", "游戏", "科技", "生活", "音乐", "舞蹈", "知识", "影视", "其他"],
        help="选择内容所属品类"
    )

# 生成按钮
st.divider()

if st.button("🚀 生成热门话题", type="primary", use_container_width=True):
    if not theme:
        st.error("❌ 请输入创作主题！")
    else:
        with st.spinner("🤖 AI正在创作中，请稍候..."):
            # 生成内容
            content = generate_bilibili_content(
                st.session_state.api_key,
                theme,
                style,
                length,
                category
            )

            # 保存到历史记录
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_history.append({
                "time": timestamp,
                "theme": theme,
                "style": style,
                "category": category,
                "content": content
            })

            # 显示结果
            st.subheader("✨ 生成结果")
            st.markdown("---")
            st.markdown(content)
            st.markdown("---")

            # 操作按钮
            col_copy, col_download, _ = st.columns([1, 1, 8])

            with col_copy:
                if st.button("📋 复制文案"):
                    st.code(content, language="markdown")
                    st.success("已复制到剪贴板！")

            with col_download:
                # 创建下载文件
                filename = f"B站文案_{theme}_{timestamp.replace(':', '-')}.txt"
                st.download_button(
                    "💾 下载",
                    content,
                    filename,
                    "text/plain"
                )

st.divider()

# ====================== 历史记录 ======================
if st.session_state.chat_history:
    st.subheader("📚 创作历史")

    # 倒序显示
    for idx, record in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"{record['time']} - {record['theme']} ({record['style']}风格)", expanded=False):
            st.markdown(f"**主题:** {record['theme']}")
            st.markdown(f"**风格:** {record['style']} | **品类:** {record['category']}")
            st.markdown("---")
            st.markdown(record['content'])

            # 操作按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 复制", key=f"copy_{idx}"):
                    st.code(record['content'], language="markdown")
                    st.success("已复制！")
            with col2:
                download_filename = f"文案_{record['theme']}_{record['time'].replace(':', '-')}.txt"
                st.download_button(
                    "💾 下载",
                    record['content'],
                    download_filename,
                    key=f"download_{idx}"
                )
else:
    st.info("📝 暂无创作历史，开始生成你的第一篇B站话题文案吧！")

# ====================== 页脚 ======================
st.divider()
st.caption("© 2025 B站热门话题AI创作助手 | Powered by Kimi AI")
