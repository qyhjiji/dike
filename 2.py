import streamlit as st
import requests
import json
from datetime import datetime
import time

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
if "saved_templates" not in st.session_state:
    st.session_state.saved_templates = []
if "show_advanced" not in st.session_state:
    st.session_state.show_advanced = False

# ====================== 核心API函数 ======================
def generate_bilibili_content(api_key, theme, style, length, category, 
                             use_trending, include_examples, custom_prompt):
    """调用Kimi API生成B站话题文案，增加了更多参数控制"""

    # 根据长度选择token数
    length_map = {
        "短（150字内）": 400,
        "中（300字）": 700,
        "长（500字）": 1200,
        "超长（800字）": 2000
    }

    # 构建系统提示
    system_prompt = """你是一名B站热门话题创作专家，精通各种风格和品类的内容创作。请按照以下要求生成文案：
1. 生成5个吸引人的标题，每个标题包含B站特色符号或emoji，不超过25字
2. 撰写正文，分段清晰，段落不宜过长，使用B站用户熟悉的表达
3. 正文中适当添加emoji或特殊符号增强表现力
4. 在结尾添加5个相关话题标签，格式如：#话题标签#
5. 直接输出文案内容，不要有任何解释或说明
"""
    
    # 如果需要热门话题参考
    trending_addon = ""
    if use_trending:
        trending_addon = """
额外要求：参考B站当前热门话题特点，融入热门元素，使用当前流行的弹幕用语和梗，
让内容更具时效性和传播性。
"""

    # 如果需要示例参考
    example_addon = ""
    if include_examples:
        example_addon = """
参考示例风格：
- 标题："【原神】新版本隐藏任务大揭秘！错过等一年！😱"
- 正文："家人们谁懂啊！这个隐藏任务也太好哭了吧😭 前方高能预警，还没做的赶紧码住！
首先传送到璃月港...（详细步骤）...最后别忘了一键三连哦~"
"""

    # 构建用户提示
    user_prompt = f"""请创作一篇关于【{theme}】的B站话题文案。

具体要求：
1. 文案风格：{style}
2. 文案长度：{length}
3. 内容品类：{category}
4. 使用B站流行语：如"前方高能"、"awsl"、"yyds"、"一键三连"等
5. 语气符合B站社区氛围，亲切有活力
{trending_addon}
{example_addon}
"""
    
    # 添加自定义提示
    if custom_prompt:
        user_prompt += f"\n额外自定义要求：{custom_prompt}"

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
        elif response.status_code == 401:
            return "❌ API Key无效或已过期，请重新输入"
        elif response.status_code == 429:
            return "❌ 请求过于频繁，请稍后再试"
        else:
            return f"API调用失败: {response.status_code}\n{response.text}"

    except requests.exceptions.Timeout:
        return "❌ 请求超时，请检查网络或稍后重试"
    except Exception as e:
        return f"生成失败: {str(e)}"


# ====================== 辅助函数 ======================
def save_as_template(theme, style, length, category, use_trending, include_examples):
    """保存当前配置为模板"""
    template_name = f"{theme}_{style}"
    st.session_state.saved_templates.append({
        "name": template_name,
        "theme": theme,
        "style": style,
        "length": length,
        "category": category,
        "use_trending": use_trending,
        "include_examples": include_examples
    })
    st.success(f"✅ 已保存模板: {template_name}")


def apply_template(template):
    """应用保存的模板"""
    return (template["theme"], template["style"], template["length"], 
            template["category"], template["use_trending"], template["include_examples"])


# ====================== 侧边栏 ======================
with st.sidebar:
    st.title("⚙️ 配置中心")

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

    # 模板管理
    st.subheader("📋 模板管理")
    if st.session_state.saved_templates:
        selected_template = st.selectbox(
            "选择模板",
            [t["name"] for t in st.session_state.saved_templates],
            index=None,
            placeholder="选择已保存的模板"
        )
        
        if selected_template:
            template = next(t for t in st.session_state.saved_templates if t["name"] == selected_template)
            if st.button("应用模板", use_container_width=True):
                st.session_state.theme, st.session_state.style, st.session_state.length, \
                st.session_state.category, st.session_state.use_trending, st.session_state.include_examples = apply_template(template)
                st.success(f"已应用模板: {selected_template}")
                time.sleep(0.5)
                st.rerun()
                
        if st.button("清除所有模板", use_container_width=True, type="secondary"):
            st.session_state.saved_templates = []
            st.success("所有模板已清除")
    else:
        st.info("暂无保存的模板，配置参数后可保存")

    st.divider()

    # 清空历史
    if st.button("🗑️ 清空历史记录", use_container_width=True, type="secondary"):
        st.session_state.chat_history = []
        st.success("历史记录已清空")
        st.rerun()

    st.divider()

    # 使用说明
    st.markdown("### 💡 使用说明")
    st.markdown("""
    1. 输入Kimi API Key
    2. 设置创作参数（可保存为模板）
    3. 输入主题和自定义要求
    4. 点击生成按钮
    5. 查看历史记录并管理
    """)

    st.divider()
    st.caption("© 2025 B站热门话题AI创作助手")

# ====================== 主界面 ======================
st.title("📺 B站热门话题AI创作助手")
st.markdown("### 一键生成高互动的B站热门话题文案，助力内容创作")

st.divider()

# 检查API Key
if not st.session_state.api_key:
    st.warning("⚠️ 请先在左侧输入Kimi API Key")
    st.info("API Key获取地址: https://platform.moonshot.cn/console/api-keys")
    st.stop()

# 创作参数
st.subheader("🎯 设置创作参数")

# 基础参数
col1, col2, col3, col4 = st.columns(4)

with col1:
    theme = st.text_input(
        "创作主题",
        placeholder="例如：新番推荐、游戏攻略、科技评测、生活vlog",
        help="输入你想要创作的核心主题",
        key="theme"
    )

with col2:
    style = st.selectbox(
        "文案风格",
        ["吐槽", "科普", "测评", "剧情解析", "搞笑", "治愈", "教程", "盘点", "激情", "悬念"],
        help="选择文案的风格调性",
        key="style"
    )

with col3:
    length = st.selectbox(
        "文案长度",
        ["短（150字内）", "中（300字）", "长（500字）", "超长（800字）"],
        help="控制文案的详细程度",
        key="length"
    )

with col4:
    category = st.selectbox(
        "内容品类",
        ["动画", "游戏", "科技", "生活", "音乐", "舞蹈", "知识", "影视", "美食", "时尚", "其他"],
        help="选择内容所属品类",
        key="category"
    )

# 高级选项
st.checkbox("展开高级选项", key="show_advanced")

if st.session_state.show_advanced:
    with st.expander("高级设置", expanded=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            use_trending = st.checkbox(
                "融入热门元素", 
                help="让内容参考当前B站热门话题特点",
                key="use_trending"
            )
            
            include_examples = st.checkbox(
                "参考示例风格", 
                help="根据经典B站文案结构生成",
                key="include_examples"
            )
        
        with col_b:
            custom_prompt = st.text_area(
                "自定义要求",
                placeholder="输入额外的创作要求或限制",
                height=100
            )
    
    # 模板保存
    if theme:
        if st.button("💾 保存为模板", type="secondary"):
            save_as_template(theme, style, length, category, use_trending, include_examples)

# 生成按钮
st.divider()

col_generate, col_regenerate = st.columns([3, 1])

with col_generate:
    generate_btn = st.button("🚀 生成热门话题", type="primary", use_container_width=True)

with col_regenerate:
    regenerate_btn = st.button("🔄 重新生成", use_container_width=True)

# 处理生成逻辑
if generate_btn or regenerate_btn:
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
                category,
                st.session_state.get("use_trending", False),
                st.session_state.get("include_examples", False),
                custom_prompt if st.session_state.show_advanced else ""
            )

            # 保存到历史记录（重新生成不创建新记录，只更新最后一条）
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if regenerate_btn and st.session_state.chat_history:
                st.session_state.chat_history[-1]["content"] = content
                st.session_state.chat_history[-1]["time"] = timestamp
            else:
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
            col_copy, col_download, col_preview = st.columns([1, 1, 1])

            with col_copy:
                if st.button("📋 复制文案"):
                    # 使用Streamlit的剪贴板功能
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

            with col_preview:
                # 预览效果
                if st.button("👀 预览效果"):
                    with st.expander("B站风格预览", expanded=True):
                        st.markdown(f"""
                        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px;">
                            <h3 style="color:#fb7299;">{theme}</h3>
                            <p style="line-height:1.8;">{content.replace('\n', '<br>')}</p>
                        </div>
                        """, unsafe_allow_html=True)

st.divider()

# ====================== 历史记录 ======================
if st.session_state.chat_history:
    st.subheader("📚 创作历史")
    
    # 历史记录筛选
    filter_style = st.selectbox(
        "按风格筛选",
        ["全部"] + list(set(record["style"] for record in st.session_state.chat_history)),
        index=0
    )
    
    # 倒序显示并应用筛选
    filtered_history = [r for r in st.session_state.chat_history 
                       if filter_style == "全部" or r["style"] == filter_style]
    
    for idx, record in enumerate(reversed(filtered_history)):
        with st.expander(f"{record['time']} - {record['theme']} ({record['style']}风格)", expanded=False):
            st.markdown(f"**主题:** {record['theme']}")
            st.markdown(f"**风格:** {record['style']} | **品类:** {record['category']}")
            st.markdown("---")
            st.markdown(record['content'])

            # 操作按钮
            col1, col2, col3 = st.columns(3)
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
            with col3:
                if st.button(f"🔄 基于此重写", key=f"rewrite_{idx}"):
                    # 填充表单以便重写
                    st.session_state.theme = record["theme"]
                    st.session_state.style = record["style"]
                    st.session_state.category = record["category"]
                    st.rerun()
else:
    st.info("📝 暂无创作历史，开始生成你的第一篇B站话题文案吧！")
