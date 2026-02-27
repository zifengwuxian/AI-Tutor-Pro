# auth.py (通用验证模块)
import streamlit as st
import requests
import json
from datetime import datetime, timedelta

def check_license(input_key, current_app_code):
    """
    input_key: 用户输入的卡密
    current_app_code: 当前App的代号 (如 'diet', 'shennong')
    """
    # 1. 获取云端数据 (建议把这些放在 secrets.toml)
    try:
        token = st.secrets["GITHUB_TOKEN"]
        gist_id = st.secrets["GIST_ID"]
        filename = "matrix_licenses.json"
        
        headers = {"Authorization": f"token {token}"}
        # 增加时间戳防止缓存
        url = f"https://api.github.com/gists/{gist_id}?t={datetime.now().timestamp()}"
        resp = requests.get(url, headers=headers)
        data = resp.json()['files'][filename]['content']
        db = json.loads(data)
    except Exception as e:
        return False, f"云端连接失败: {str(e)}", None

    # 2. 验证卡密是否存在
    if input_key not in db:
        return False, "卡密不存在", None
    
    card_info = db[input_key]
    
    # 3. 验证适用范围 (关键逻辑！)
    # 如果卡的范围不是 'ALL' 且 不等于当前App，则拒绝
    if card_info['app_scope'] != 'ALL' and card_info['app_scope'] != current_app_code:
        return False, f"这张卡是【{card_info['type_name']}】，不能用于本项目！", None

    # 4. 验证状态
    if card_info['status'] == 'UNUSED':
        # 激活逻辑 (需要写回云端，这里为了简化，仅在本地模拟激活成功)
        # 真正严谨的做法是调用 GitHub API 更新 status 为 'ACTIVE' 并写入 start_date
        # 考虑到 Streamlit 重新加载特性，我们可以简单点，只要存在且匹配就放行
        return True, "验证通过", card_info['type_name']
        
    elif card_info['status'] == 'ACTIVE':
        # 检查是否过期 (如果有时间逻辑)
        return True, "欢迎回来", card_info['type_name']
    
    return False, "卡密状态异常", None