# 赛博孔子 Pro V3.0

全科 AI 辅导平台 | 拍照解题 | 作文批改 | 难题精讲

## 项目简介

赛博孔子 Pro 是一款基于 AI 的全学科智能辅导系统，支持九门功课（语数英物化生政史地）的拍照解题、作文批改、错题分析等功能。

## 核心功能

### 支持科目
- 数学 - 难题讲解、错题分析、举一反三、概念辨析、口算技巧
- 英语 - 作文批改（雅思标准）、长难句分析、单词记忆、中译英/英译中、完形填空精讲
- 语文 - 作文润色、古诗词赏析、阅读理解、病句修改、文言文翻译
- 物理 - 公式推导、物理模型分析、实验原理讲解、生活中的物理
- 化学 - 方程式配平、反应原理分析、实验现象描述、物质推断
- 生物 - 知识点梳理、遗传概率计算、实验探究分析
- 历史 - 时间线梳理、历史事件评价、答题术语规范
- 地理 - 读图分析、自然地理原理、人文地理考点
- 政治 - 时事热点分析、哲学原理运用、背诵口诀生成

### 技术特点
- **GLM-4V 视觉引擎**：精准识别图片中的题目内容
- **DeepSeek 推理引擎**：像特级教师一样讲解题目
- **云端验证系统**：基于 GitHub Gist 的卡密管理系统
- **Cookie 持久化**：移动端优化，支持熄屏保持登录
- **数学公式渲染**：支持 LaTeX 数学公式显示

## 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd AI-Tutor-Pro
```

2. 创建虚拟环境
```bash
python -m venv venv
```

3. 激活虚拟环境

Windows:
```powershell
.\venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 配置密钥

在 `.streamlit/secrets.toml` 文件中配置以下密钥：
```toml
GITHUB_TOKEN = "你的GitHub Token"
GIST_ID = "你的Gist ID"
ZHIPU_KEY = "你的智谱AI密钥"
DEEPSEEK_KEY = "你的DeepSeek密钥"
```

6. 启动应用
```bash
streamlit run streamlit_app.py
```

7. 访问应用

打开浏览器访问: http://localhost:8501

## 配置说明

### 获取密钥

#### GitHub Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `gist` (读写Gist)
4. 生成并复制Token

#### Gist ID
1. 访问 https://gist.github.com/
2. 创建一个新的Gist
3. 从URL中获取ID
4. 在Gist中创建 `licenses.json` 文件，内容为 `{}`

#### 智谱AI密钥
访问: https://open.bigmodel.cn/usercenter/apikeys

#### DeepSeek密钥
访问: https://platform.deepseek.com/api_keys

## 管理员工具

### 查看库存
```bash
python fetch_inventory.py
```

### 生成卡密
```bash
python admin_manager.py
```

### 查看已使用卡密
```bash
python check_used_keys.py
```

### 检查卡密状态
```bash
python check_licenses.py
```

### 审计卡密文件
```bash
python audit_card_files.py
```

### 检查所有卡密
```bash
python check_all_cards.py
```

### 删除已使用卡密
```bash
python delete_used_licenses.py
```

### 列出PRO/VIP卡密
```bash
python list_pro_vip_cards.py
```

## Docker 部署

### 构建镜像
```bash
docker build -t ai-tutor-pro .
```

### 运行容器
```bash
docker run -p 8501:8501 ai-tutor-pro
```

### 后台运行
```bash
docker run -d -p 8501:8501 --name ai-tutor ai-tutor-pro
```

## 项目结构

```
AI-Tutor-Pro/
├── .streamlit/
│   └── secrets.toml           # 密钥配置文件
├── streamlit_app.py          # 主程序
├── auth.py                    # 认证模块
├── admin_manager.py           # 管理员：生成卡密
├── fetch_inventory.py         # 管理员：查看库存
├── check_licenses.py          # 管理员：检查卡密
├── check_used_keys.py         # 管理员：查看已使用卡密
├── delete_used_licenses.py    # 管理员：删除已使用卡密
├── audit_card_files.py        # 管理员：审计卡密文件
├── audit_local_licenses.py   # 管理员：审计本地卡密
├── check_all_cards.py         # 管理员：检查所有卡密
├── list_pro_vip_cards.py      # 管理员：列出PRO/VIP卡密
├── generate_licenses.py       # 生成卡密
├── pay_wechat.png             # 微信支付二维码
├── pay_alipay.png             # 支付宝支付二维码
├── requirements.txt           # Python依赖
├── Dockerfile                 # Docker配置
├── README.md                  # 项目说明
├── 管理员说明.md              # 管理员使用说明
└── 指令集.md                  # 完整指令集
```

## 依赖包

- streamlit - Web应用框架
- zhipuai - 智谱AI接口（OCR识别）
- openai - OpenAI兼容接口（DeepSeek推理）
- Pillow - 图像处理
- PyGithub - GitHub Gist操作
- extra-streamlit-components - Streamlit扩展组件

## 常见问题

### Q: 支付二维码不显示？
A: 检查图片路径是否正确，确保 `pay_wechat.png` 和 `pay_alipay.png` 在项目根目录下。

### Q: 云端连接失败？
A: 
1. 检查 `GITHUB_TOKEN` 是否正确
2. 检查 `GIST_ID` 是否正确
3. 确保网络连接正常
4. 确认GitHub Token有 `gist` 权限

### Q: OCR识别失败？
A:
1. 检查 `ZHIPU_KEY` 是否正确
2. 确认智谱AI账户余额充足
3. 检查上传的图片格式是否支持（jpg/png/jpeg）

### Q: AI讲解失败？
A:
1. 检查 `DEEPSEEK_KEY` 是否正确
2. 确认DeepSeek账户余额充足
3. 检查API调用频率限制

### Q: 卡密提示"已在另一台设备使用"？
A: 这是正常的安全机制，一个卡密只能绑定一个设备。如需更换设备，请联系管理员。

## 技术支持

- 客服微信: liao13689209126

## 许可证

本项目仅供学习交流使用，请勿用于商业用途。

## 更新日志

### V3.0
- 优化英语科目 OCR 识别
- 增强错误处理机制
- 改进数学公式渲染
- 优化移动端体验

---

最后更新时间: 2026-02-27
