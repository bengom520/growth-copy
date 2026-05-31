import streamlit as st
import requests
import json

# -------------------------- 页面配置 --------------------------
st.set_page_config(
    page_title="成长副本 - 30-60-90学习路径设计器",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 密钥配置（自动适配本地和部署环境） --------------------------
try:
    # 部署环境：从Streamlit Secrets读取
    DOUBAO_API_KEY = st.secrets["DOUBAO_API_KEY"]
except:
    # 本地测试环境：直接在这里填写你的API密钥（部署前记得删掉！）
    DOUBAO_API_KEY = ""

# 固定配置（不需要改）
DOUBAO_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/responses"
MODEL_ID = "doubao-seed-1-8-251228"

# -------------------------- AI生成学习路径的核心函数 --------------------------
def generate_learning_path(position, skill_level, goal, daily_time):
    prompt = f"""
    你是一个专为AI Native游戏公司打造的新人成长导师。请根据以下新人信息，生成一份详细的、个性化的30-60-90天学习路径。

    新人信息：
    - 岗位：{position}
    - AI技能基础：{skill_level}
    - 学习目标：{goal}
    - 每日可用学习时间：{daily_time}

    AI Native组织核心能力模型：
    1. Prompt工程：掌握高质量提示词编写方法，能够精准引导AI输出
    2. AI工具使用：熟练使用ChatGPT、豆包、GitHub Copilot、Midjourney、Notion AI等工具
    3. 人机协同写作：能够与AI协作完成需求文档、代码注释、产品方案等内容
    4. AI辅助设计：使用AI工具进行UI设计、原型制作、游戏美术素材生成
    5. 数据洞察：使用AI进行数据分析、可视化和业务洞察
    6. AI伦理：了解AI使用的边界和规范，避免版权和合规风险

    分阶段目标体系：
    - 30天（AI工具入门阶段）：掌握日常工作必备的AI工具和技能，能够使用AI提升基础工作效率
    - 60天（人机协同实践阶段）：能够在实际工作中运用AI提升效率，完成简单的人机协同任务
    - 90天（AI思维建立阶段）：建立AI思维，能够主动探索AI在业务中的创新应用

    输出要求：
    1. 使用Markdown格式，结构清晰，标题层级分明
    2. 每个任务必须包含：任务描述、预计时长、验收标准（具体可衡量）
    3. 每个阶段结束后，添加一个"阶段验收标准"
    4. 最后推荐3-5个高质量免费学习资源，包含资源名称和获取方式
    5. 语言简洁专业，避免空泛内容，所有内容必须与AI Native能力相关
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }

    # 火山方舟Responses API正确格式（已验证）
    data = {
        "model": MODEL_ID,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
        "top_p": 0.9
    }

    try:
        response = requests.post(DOUBAO_ENDPOINT, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 生成失败，请检查：\n1. API密钥是否正确\n2. 网络连接是否正常\n3. 豆包API是否有可用额度\n\n错误信息：{str(e)}"
        if 'response' in locals() and response.text:
            error_msg += f"\n响应内容：{response.text}"
        return error_msg

# -------------------------- 主界面 --------------------------
st.title("🎮 成长副本 - AI Native新人30-60-90学习路径设计器")
st.subheader("专为游戏行业AI Native组织打造的个性化新人融入工具")
st.divider()

# 侧边栏用户信息输入
with st.sidebar:
    st.header("📝 新人信息")
    position = st.selectbox(
        "岗位",
        ["研发", "产品", "设计", "运营"],
        help="选择你的岗位，系统会生成对应的专属学习内容"
    )

    skill_level = st.selectbox(
        "AI技能基础",
        ["零基础", "了解基础", "熟练使用"],
        help="零基础：从未使用过AI工具；了解基础：会用ChatGPT聊天；熟练使用：能熟练使用多种AI工具"
    )

    goal = st.text_area(
        "学习目标",
        placeholder="例如：能够用AI辅助完成日常产品工作，提升30%工作效率",
        height=100
    )

    daily_time = st.selectbox(
        "每日可用学习时间",
        ["1小时以内", "1-2小时", "2小时以上"]
    )

    generate_button = st.button(
        "🚀 生成专属学习路径",
        type="primary",
        use_container_width=True,
        help="点击后AI将为你生成个性化的30-60-90天学习计划"
    )

    st.divider()
    st.caption("© 2026 成长副本 | 基于Streamlit和豆包API构建")

# 主内容区
if generate_button:
    if not goal.strip():
        st.warning("⚠️ 请填写学习目标")
    else:
        with st.spinner("🤖 AI正在为你生成专属成长副本，请稍候..."):
            learning_path = generate_learning_path(position, skill_level, goal, daily_time)

            if "❌ 生成失败" in learning_path:
                st.error(learning_path)
            else:
                st.success("✅ 学习路径生成完成！")
                st.markdown(learning_path)

                # 下载按钮
                st.download_button(
                    label='📥 下载学习路径为Markdown文件',
                    data=learning_path,
                    file_name=f"{position}岗30-60-90学习路径.md",
                    mime="text/markdown",
                    use_container_width=True
                )

# 首次加载时的提示
else:
    st.info('👈 请在左侧填写你的信息，然后点击"生成专属学习路径"按钮')

    # 展示示例
    with st.expander("📌 查看示例学习路径（产品岗）"):
        st.markdown("""
        # 「成长副本」30-60-90天学习路径
        ## 新人画像
        岗位：产品
        AI技能基础：了解基础
        学习目标：能够用AI辅助完成日常产品工作，提升30%工作效率
        每日可用时间：1-2小时
        
        ## 30天：AI工具入门阶段
        ### 阶段目标
        掌握产品岗日常工作必备的AI工具和技能，能够使用AI提升基础工作效率
        
        ### 每周任务
        #### 第1周：AI基础认知与工具入门
        - 任务1：了解AI Native组织的工作方式 | 预计时长：2小时 | 验收标准：能够说出AI Native组织与传统组织的3个核心区别
        - 任务2：注册并熟悉3个常用AI工具 | 预计时长：3小时 | 验收标准：能够熟练使用豆包、Notion AI和ChatGPT进行基础对话
        - 任务3：学习基础prompt编写技巧 | 预计时长：2小时 | 验收标准：能够写出包含"角色+任务+要求"的完整提示词
        
        ...
        """)