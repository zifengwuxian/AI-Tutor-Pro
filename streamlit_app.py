import streamlit as st
import base64
from zhipuai import ZhipuAI
from openai import OpenAI
from PIL import Image
import io
import json
from github import Github, InputFileContent
import uuid
import time
import extra_streamlit_components as stx
from datetime import datetime, timedelta

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="赛博孔子 Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-title {font-size: 2.5rem; color: #1565C0; text-align: center; font-weight: bold;}
    .sub-title {font-size: 1.2rem; color: #555; text-align: center; margin-bottom: 20px;}
    .answer-area {
        background-color: #F8F9FA; 
        padding: 25px; 
        border-radius: 10px; 
        border-left: 5px solid #1565C0; 
        color: #212529;
        font-size: 1.05rem;
        line-height: 1.6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ================= 2. 核心配置区 (云端安全读取) =================

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "") 
GIST_ID = st.secrets.get("GIST_ID", "")

ZHIPU_KEY = st.secrets.get("ZHIPU_KEY", "")
DEEPSEEK_KEY = st.secrets.get("DEEPSEEK_KEY", "")
MY_WECHAT = "Liao_Code_Master"

# ================= 3. 学科-功能 深度映射表 =================
SUBJECT_TASKS = {
    "数学": ["难题讲解 (分步推导)", "错题分析 (找原因)", "举一反三 (出类似题)", "概念辨析", "口算技巧"],
    "英语": ["作文批改 (雅思标准)", "长难句分析 (语法拆解)", "单词记忆 (词根词缀)", "中译英/英译中", "完形填空精讲"],
    "语文": ["作文润色 (升格)", "古诗词赏析 (意象/情感)", "阅读理解 (答题模板)", "病句修改", "文言文翻译"],
    "物理": ["公式推导", "物理模型分析", "实验原理讲解", "生活中的物理"],
    "化学": ["方程式配平", "反应原理分析", "实验现象描述", "物质推断"],
    "生物": ["知识点梳理", "遗传概率计算", "实验探究分析"],
    "历史": ["时间线梳理", "历史事件评价 (正反面)", "答题术语规范"],
    "地理": ["读图分析", "自然地理原理", "人文地理考点"],
    "政治": ["时事热点分析", "哲学原理运用", "背诵口诀生成"]
}

# ================= 4. Cookie 管理器 =================
cookie_manager = stx.CookieManager()

# ================= 5. 云端验证逻辑 =================

def connect_db():
    try:
        g = Github(GITHUB_TOKEN)
        gist = g.get_gist(GIST_ID)
        file = gist.files['licenses.json']
        return json.loads(file.content), gist
    except: return None, None

def activate_license(license_key):
    """激活/登录逻辑"""
    if not license_key: return False, "请输入卡密"
    
    db, gist = connect_db()
    if not db: return False, "云端连接失败，请检查网络"
    
    if license_key not in db: return False, "❌ 卡密无效，请联系老师购买"
    
    record = db[license_key]
    new_device_id = str(uuid.uuid4())
    
    if record['status'] == 'UNUSED':
        db[license_key]['status'] = 'USED'
        db[license_key]['bind_device'] = new_device_id
        db[license_key]['activated_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            gist.edit(files={'licenses.json': InputFileContent(json.dumps(db, indent=2))})
        except: pass 
    
    try:
        expires_at = datetime.now() + timedelta(days=365)
        cookie_manager.set('user_license', license_key, expires_at=expires_at, key="set_lic")
    except:
        cookie_manager.set('user_license', license_key, key="set_lic")
        
    return True, "✅ 登录成功！"

def auto_login_check():
    """自动登录检查 - 带云端验证"""
    # 1. 优先检查内存Session
    if st.session_state.get('is_vip', False):
        return True, st.session_state.get('user_license', 'Unknown')

    # 2. 检查硬盘Cookie并验证云端
    try:
        cookies = cookie_manager.get_all()
        c_license = cookies.get('user_license')
        
        if c_license and isinstance(c_license, str) and len(c_license) > 10 and c_license.startswith('EDU-'):
            # 关键修复：验证卡密是否在云端数据库中
            db, _ = connect_db()
            if db and c_license in db:
                # 卡密有效，同步到Session
                st.session_state['is_vip'] = True
                st.session_state['user_license'] = c_license
                return True, c_license
            else:
                # 卡密无效或云端连接失败，清除本地Cookie
                cookie_manager.delete('user_license')
                st.session_state['is_vip'] = False
                st.session_state['user_license'] = None
    except Exception as e:
        pass
        
    return False, None

# ================= 6. AI 智能模块 (核心引擎) =================

def ocr_general(image_file, subject):
    """视觉引擎 - 回滚纯净版"""
    if not ZHIPU_KEY: return "Error: ZHIPU_KEY 未配置"
    client = ZhipuAI(api_key=ZHIPU_KEY)
    
    buffered = io.BytesIO()
    image_file.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # 💡 修正：移除 LaTeX 强制指令，让 AI 自然识别
    prompt = f"""
    你是一个精准的 OCR 助手。请识别图片中的【{subject}】内容。
    
    【要求】：
    1. 所见即所得：图片里是什么符号，你就输出什么符号（例如 ×, ÷, +, -）。
    2. 保持排版：每道题占一行。
    3. 不要加任何解释，只输出题目内容。
    """
    
    try:
        res = client.chat.completions.create(
            model="glm-4v",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_base64}}]}]
        )
        return res.choices[0].message.content
    except: return "图片识别失败"

def ai_tutor_brain(question_text, subject, task_type):
    """推理引擎 (Prompt Engine)"""
    if not DEEPSEEK_KEY: return "Error: DEEPSEEK_KEY 未配置"
    client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
    
    strategy = "请用通俗易懂的语言讲解，重点突出考点。"
    if "分步" in task_type: strategy = "请务必分步骤讲解，逻辑严密，每一步都要说明依据。"
    elif "举一反三" in task_type: strategy = "讲解完原题后，请务必再出 1 道类似的变式题，并给出答案。"
    elif "作文" in task_type or "润色" in task_type: strategy = "请按【评分-纠错-点评-升格范文】的结构输出，提供高级词汇。"
    elif "背诵" in task_type or "口诀" in task_type: strategy = "请提供好记的顺口溜或思维导图，帮助记忆。"
    
    system_prompt = f"""
    你是一位资深的【{subject}】特级教师。
    当前任务：{task_type}
    教学策略：{strategy}
    
    请使用 Markdown 格式输出，重点内容加粗。
    """
    
    try:
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"题目/内容：\n{question_text}\n\n请老师开始讲解。"}
            ],
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e: return f"AI思考失败: {str(e)}"

def load_image(path):
    import os
    if os.path.exists(path): return Image.open(path)
    return None

# ================= 7. 界面逻辑 =================

is_logged_in, current_user = auto_login_check()

with st.sidebar:
    st.markdown("## 🔐 赛博孔子通行证")
    
    with st.expander("🔧 缓存清理 (调试用)", expanded=False):
        if st.button("🗑️ 强力重置"):
            cookie_manager.delete('user_license')
            st.session_state.clear()
            st.rerun()
    
    if is_logged_in:
        st.success(f"🟢 已自动登录")
        st.caption(f"卡号: {current_user}")
        
        if st.button("🚪 安全退出", type="secondary", use_container_width=True):
            # 先清除Session状态
            st.session_state['is_vip'] = False
            st.session_state['user_license'] = None
            # 再清除Cookie
            try:
                cookie_manager.delete('user_license')
            except:
                pass
            st.warning("正在清除安全凭证...")
            time.sleep(0.5)
            st.rerun()
            
    else:
        license_input = st.text_input("请输入学习卡密", type="password")
        if st.button("🚀 登录 / 激活", type="primary", use_container_width=True):
            with st.spinner("正在连接云端验证..."):
                valid, msg = activate_license(license_input)
                if valid:
                    st.success(msg)
                    st.session_state['is_vip'] = True
                    st.session_state['user_license'] = license_input
                    time.sleep(1) 
                    st.rerun()
                else:
                    st.error(msg)
    
    st.divider()
    with st.expander("💎 购买卡密 (9.9元/次)", expanded=False):
        st.info("扫码支付后，截图加微信领卡密")
        tab1, tab2 = st.tabs(["微信", "支付宝"])
        with tab1:
            img = load_image("pay_wechat.png")
            if img: st.image(img)
        with tab2:
            img = load_image("pay_alipay.png")
            if img: st.image(img)
        st.markdown(f"**客服微信**: `{MY_WECHAT}`")

# 主界面
st.markdown("<div class='main-title'>🎓 赛博孔子 Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>全科 AI 辅导 | 拍照解题 | 作文批改 | 难题精讲</div>", unsafe_allow_html=True)

if is_logged_in:
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            subject = st.selectbox("📚 选择科目", list(SUBJECT_TASKS.keys()))
        with c2:
            task = st.selectbox("📝 选择辅导模式", SUBJECT_TASKS[subject])
            
        uploaded_file = st.file_uploader(f"📸 上传【{subject}】题目/图片", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        st.markdown("---")
        c1, c2 = st.columns([1, 1.5])
        with c1:
            img = Image.open(uploaded_file)
            st.image(img, caption="上传的内容", use_container_width=True)
            
            if st.button("🚀 开始 AI 辅导", type="primary", use_container_width=True):
                progress = st.progress(0)
                status = st.empty()
                
                # Step 1
                status.write("👀 正在识别内容 (GLM-4V)...")
                progress.progress(30)
                ocr_text = ocr_general(img, subject)
                
                # Step 2
                if "失败" not in ocr_text:
                    status.write(f"🧠 {subject}老师正在思考 (DeepSeek)...")
                    progress.progress(70)
                    ai_result = ai_tutor_brain(ocr_text, subject, task)
                    
                    progress.progress(100)
                    status.empty()
                    
                    with c2:
                        with st.expander("查看识别结果 (OCR)", expanded=True):
                            st.text(ocr_text) # 💡 改回 text 显示，因为现在输出的是纯文本
                        
                        st.markdown(f"### 👩‍🏫 {subject}老师讲解")
                        st.markdown(f"<div class='answer-area'>{ai_result}</div>", unsafe_allow_html=True)
                        st.balloons()
                else:
                    st.error("图片识别失败，请确保字迹清晰。")
else:
    st.info("👋 欢迎！请在左侧输入卡密登录。登录一次，365天免输密码！")
    st.markdown("""
    ### ✨ 功能亮点
    - **全科覆盖**：语数英物化生政史地，九门功课全搞定。
    - **模式丰富**：不仅仅是解题，还能**改作文、背口诀、举一反三**。
    - **名师大脑**：接入 DeepSeek 推理模型，像特级教师一样讲课。
    - **移动端优化**：支持手机熄屏保持登录状态，Cookie持久化存储。
    """)