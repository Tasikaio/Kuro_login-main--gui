# 使用指南

## 快速开始

### 1. 环境准备

```bash
# 创建conda虚拟环境（推荐）
conda create -n kuro_login python=3.11 -y
conda activate kuro_login

# 选择安装方式：
# 完整版（支持图标点选 + 滑块验证码）
pip install -r requirements.txt

# 或轻量版（仅支持滑块验证码）
pip install -r requirements_slice.txt
```

### 2. 验证码类型判断

运行任一脚本后，根据出现的验证码类型选择对应的解决方案：

- **图标点选验证码**：显示多个图标，需要点击特定图标
- **滑块验证码**：显示一个需要拖动的滑块

### 3. 运行脚本

#### 方案A：滑块验证码（推荐首次尝试）
```bash
cd slice
python tools.py
```

#### 方案B：图标点选验证码
```bash
python sms_send.py
```

#### 方案C：手动输入验证码
```bash
python login.py
```

## 常见问题

### Q: 如何知道当前是哪种验证码？
A: 运行脚本后，根据验证码界面判断：
- 如果看到多个小图标需要点击 → 使用 `sms_send.py`
- 如果看到滑块需要拖动 → 使用 `slice/tools.py`

### Q: 验证码识别失败怎么办？
A: 
1. 多尝试几次（验证码识别有一定失败率）
2. 切换到手动模式：使用 `login.py`
3. 检查网络连接是否正常

### Q: 首次运行很慢？
A: 图标点选验证码功能首次运行需要下载AI模型文件，请耐心等待。

### Q: 依赖安装失败？
A: 
1. 确保使用conda虚拟环境
2. 尝试使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
3. 如果只需要滑块验证码功能，使用轻量版：`pip install -r requirements_slice.txt`

## 输出示例

成功运行后，您将获得类似以下的输出：

```json
{
    "token": "your_token_here",
    "userId": "your_user_id",
    "roleId": "your_role_id", 
    "roleName": "your_role_name",
    "serverId": "your_server_id"
}
```

将这些信息保存下来，用于后续的自动签到等功能。
