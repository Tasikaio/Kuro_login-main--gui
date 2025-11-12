import sys
import logging

# ===== 生产环境：禁止任何模块创建日志文件 =====
# 劫持logging.FileHandler类，使其在打包后失效
if getattr(sys, 'frozen', False):
    # 生产环境：FileHandler返回NullHandler（不创建文件）
    logging.FileHandler = lambda *args, **kwargs: logging.NullHandler()
else:
    # 开发环境：正常配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('kuro_login_debug.log')
        ]
    )

# 获取主模块logger（必须存在，否则其他模块调用logger.info()会闪退）
logger = logging.getLogger(__name__)

# ===== 你的原始代码从这里开始 =====
import sys
import json
import uuid
import string


from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTextEdit, QMessageBox, QProgressBar, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QClipboard

import requests

from geetest_captcha.geetest import GeeTest
from utils.randomUtils import random_string



ANDROID_CAPTCHA_ID = "3f7e2d848ce0cb7e7d019d621e556ce2"


def random_device() -> str:
    alphabet = "ABCDEF" + string.digits
    return random_string(alphabet, 40)


class LoginWorker(QThread):
    progress_updated = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    login_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    sms_sent_success = pyqtSignal()  # New signal for SMS sent success
    
    def __init__(self, phone_number: str):
        super().__init__()
        self.phone_number = phone_number
        self.sms_code = None
        self.sms_instance = None
        
    def set_sms_code(self, sms_code: str):
        self.sms_code = sms_code
        
    def run(self):
        try:
            self.progress_updated.emit("正在获取验证码...")
            self.status_updated.emit("正在处理GeeTest验证码，请稍候...")
            logger.info(f"Starting login process for phone: {self.phone_number}")
            
            # Get CAPTCHA security code
            logger.info("Getting CAPTCHA security code...")
            sec_code = GeeTest(ANDROID_CAPTCHA_ID).get_sec_code()
            logger.info(f"CAPTCHA security code obtained: {sec_code[:20]}...")
            
            random_device_id = random_device()
            logger.info(f"Generated device ID: {random_device_id}")
            
            self.progress_updated.emit("验证码获取成功，正在发送短信...")
            self.status_updated.emit(f"设备ID: {random_device_id[:8]}...")
            
            # Create SMS instance
            self.sms_instance = SMS(self.phone_number, random_device_id, sec_code)
            logger.info("SMS instance created successfully")
            
            # Send SMS code
            logger.info("Sending SMS code...")
            sms_status = self.sms_instance.send_sms_code()
            logger.info(f"SMS response: {sms_status}")
            
            if sms_status.get("code") != 200:
                error_msg = sms_status.get("msg", "Unknown error")
                logger.error(f"SMS sending failed: {error_msg}")
                self.error_occurred.emit(f"短信发送失败: {error_msg}")
                return
                
            logger.info("SMS sent successfully")
            self.progress_updated.emit("短信发送成功！请输入验证码")
            self.status_updated.emit("请查看手机短信并输入验证码")
            self.sms_sent_success.emit()  # Emit signal to enable SMS input
            
        except Exception as e:
            logger.error(f"Error in run(): {str(e)}")
            self.error_occurred.emit(f"处理失败: {str(e)}")
    
    def complete_login(self, sms_code: str):
        try:
            self.progress_updated.emit("正在验证登录...")
            self.status_updated.emit("正在处理登录请求...")
            logger.info(f"Completing login with SMS code: {sms_code}")
            
            # SDK login
            logger.info("Calling SDK login...")
            login_response = self.sms_instance.sdk_login(sms_code)
            logger.info(f"SDK login response: {login_response}")
            
            # Check if login was successful - either by code field or by presence of token
            if login_response.get("code") is not None and login_response.get("code") != 200:
                error_msg = login_response.get("msg", "Login failed")
                logger.error(f"SDK login failed: {error_msg}")
                self.error_occurred.emit(f"登录失败: {error_msg}")
                return
            elif login_response.get("token") is None:
                # If no token and no code, consider it failed
                logger.error(f"SDK login failed: No token in response")
                self.error_occurred.emit(f"登录失败: 未获取到Token")
                return
                
            token = login_response.get("token")
            user_id = login_response.get("userId")
            logger.info(f"Login successful - Token: {token[:20]}..., UserID: {user_id}")
            
            self.progress_updated.emit("登录成功，正在获取用户信息...")
            self.status_updated.emit("正在获取角色数据...")
            
            # Get login data
            logger.info("Getting login data...")
            login_data = self.sms_instance.get_login_data(token)
            logger.info(f"Login data received: {login_data}")
            
            # Create final metadata
            random_uuid = uuid.uuid4()
            meta = {
                "token": token,
                "userId": user_id,
                "roleId": login_data.get("roleId"),
                "roleName": login_data.get("roleName"),
                "serverId": login_data.get("serverId"),
                "deviceCode": str(random_uuid),
                "distinctId": str(uuid.uuid4()),
            }
            
            logger.info(f"Final metadata created: {meta}")
            self.progress_updated.emit("用户信息获取成功！")
            self.login_completed.emit(meta)
            
        except Exception as e:
            logger.error(f"Error in complete_login(): {str(e)}")
            self.error_occurred.emit(f"登录失败: {str(e)}")


class SMS(object):
    def __init__(self, phone_number: str, device_id: str, sec_code: str) -> None:
        self.phone_number = phone_number
        self.device_id = device_id
        self.sec_code = sec_code

    def send_sms_code(self):
        headers = {
            "Host": "api.kurobbs.com",
            "osversion": "Android",
            "devcode": self.device_id,
            "countrycode": "CN",
            "model": "MIX 2",
            "source": "android",
            "lang": "zh-Hans",
            "version": "2.2.0",
            "versioncode": "2200",
            "channelid": "4",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.11.0",
        }
        url = "https://api.kurobbs.com/user/getSmsCode"
        data = {"mobile": self.phone_number, "geeTestData": self.sec_code}
        logger.info(f"Sending SMS to {self.phone_number} with device {self.device_id}")
        response = requests.post(url, headers=headers, data=data, timeout=30)
        logger.info(f"SMS API response status: {response.status_code}")
        return response.json()

    def sdk_login(self, sms_code: str):
        headers = {
            "Host": "api.kurobbs.com",
            "osversion": "Android",
            "devcode": self.device_id,
            "countrycode": "CN",
            "model": "MIX 2",
            "source": "android",
            "lang": "zh-Hans",
            "version": "2.2.0",
            "versioncode": "2200",
            "channelid": "4",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.11.0",
        }
        url = "https://api.kurobbs.com/user/sdkLogin"
        data = {
            "code": sms_code,
            "devCode": self.device_id,
            "gameList": "",
            "mobile": self.phone_number,
        }
        logger.info(f"SDK login attempt for {self.phone_number} with SMS code")
        response = requests.post(url=url, data=data, headers=headers, timeout=30)
        logger.info(f"SDK login response status: {response.status_code}")
        json_result = response.json()

        if json_result["code"] != 200:
            error_message = json_result["msg"]
            raise Exception(f"SDK login error, message:{error_message}")

        return json_result["data"]

    def get_login_data(self, token: str):
        headers = {
            "Host": "api.kurobbs.com",
            "devcode": self.device_id,
            "source": "android",
            "version": "2.2.0",
            "versioncode": "2200",
            "token": token,
            "osversion": "Android",
            "countrycode": "CN",
            "model": "MIX 2",
            "lang": "zh-Hans",
            "channelid": "4",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.11.0",
        }
        cookies = {"user_token": token}
        url = "https://api.kurobbs.com/gamer/widget/game3/getData"
        data = {"type": "1", "sizeType": "2"}
        logger.info(f"Getting login data with token: {token[:20]}...")
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        logger.info(f"Login data response status: {response.status_code}")
        json_result = response.json()

        if json_result["code"] != 200:
            error_message = json_result["msg"]
            raise Exception(f"SDK login error, message:{error_message}")

        return json_result["data"]


class KuroLoginGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_worker = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("KuroBBS 登录工具")
        self.setGeometry(100, 100, 600, 600)  # Increased height from 500 to 600
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("KuroBBS 登录工具")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Input group
        input_group = QGroupBox("登录信息")
        input_layout = QVBoxLayout()
        
        # Phone number input
        phone_layout = QHBoxLayout()
        phone_label = QLabel("手机号码:")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入手机号码")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        input_layout.addLayout(phone_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.send_sms_btn = QPushButton("发送验证码")
        self.send_sms_btn.clicked.connect(self.send_sms_code)
        button_layout.addWidget(self.send_sms_btn)
        
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.complete_login)
        self.login_btn.setEnabled(False)
        button_layout.addWidget(self.login_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # SMS code input
        sms_layout = QHBoxLayout()
        sms_label = QLabel("验证码:")
        self.sms_input = QLineEdit()
        self.sms_input.setPlaceholderText("请输入短信验证码")
        self.sms_input.setEnabled(False)
        sms_layout.addWidget(sms_label)
        sms_layout.addWidget(self.sms_input)
        main_layout.addLayout(sms_layout)
        
        # Status group
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("就绪")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.progress_label = QLabel("")
        self.progress_label.setWordWrap(True)
        status_layout.addWidget(self.progress_label)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Result display
        result_group = QGroupBox("登录结果")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)
        
        # Action buttons for token operations
        action_layout = QHBoxLayout()
        
        self.copy_token_btn = QPushButton("复制Token")
        self.copy_token_btn.clicked.connect(self.copy_token_to_clipboard)
        self.copy_token_btn.setEnabled(False)  # Disabled until login success
        action_layout.addWidget(self.copy_token_btn)
        
        self.save_json_btn = QPushButton("保存为JSON")
        self.save_json_btn.clicked.connect(self.save_as_json)
        self.save_json_btn.setEnabled(False)  # Disabled until login success
        action_layout.addWidget(self.save_json_btn)
        
        result_layout.addLayout(action_layout)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
        
        # Add stretch to push everything up
        main_layout.addStretch()
        
    def send_sms_code(self):
        phone_number = self.phone_input.text().strip()
        
        if not phone_number:
            QMessageBox.warning(self, "警告", "请输入手机号码")
            return
            
        if len(phone_number) != 11 or not phone_number.isdigit():
            QMessageBox.warning(self, "警告", "请输入有效的11位手机号码")
            return
            
        # Disable inputs and buttons during processing
        self.send_sms_btn.setEnabled(False)
        self.phone_input.setEnabled(False)
        
        # Create and start worker thread
        self.login_worker = LoginWorker(phone_number)
        self.login_worker.progress_updated.connect(self.update_progress)
        self.login_worker.status_updated.connect(self.update_status)
        self.login_worker.login_completed.connect(self.on_login_success)
        self.login_worker.error_occurred.connect(self.on_error)
        self.login_worker.sms_sent_success.connect(self.on_sms_sent_success)  # Connect new signal
        
        self.login_worker.start()
        
    def complete_login(self):
        sms_code = self.sms_input.text().strip()
        
        if not sms_code:
            QMessageBox.warning(self, "警告", "请输入验证码")
            return
            
        if len(sms_code) != 6 or not sms_code.isdigit():
            QMessageBox.warning(self, "警告", "请输入有效的6位数字验证码")
            return
            
        # Disable inputs
        self.login_btn.setEnabled(False)
        self.sms_input.setEnabled(False)
        
        # Complete login through worker
        if self.login_worker:
            self.login_worker.complete_login(sms_code)
        
    def update_progress(self, message: str):
        self.progress_label.setText(message)
        
    def update_status(self, message: str):
        self.status_label.setText(message)
        
    def on_login_success(self, login_data: dict):
        self.progress_label.setText("登录成功！")
        self.status_label.setText("登录完成，数据已准备就绪")
        
        # Store login data for later use
        self.current_login_data = login_data
        
        # Display result
        result_text = json.dumps(login_data, ensure_ascii=False, indent=2)
        self.result_text.setText(result_text)
        
        # Enable action buttons
        self.copy_token_btn.setEnabled(True)
        self.save_json_btn.setEnabled(True)
        
        # Update status - no longer auto-save
        self.status_label.setText("登录成功！您可以复制Token或手动保存数据")
        QMessageBox.information(self, "成功", "登录成功！")
            
        # Reset UI (but keep action buttons enabled)
        self.send_sms_btn.setEnabled(True)
        self.phone_input.setEnabled(True)
        
    def on_sms_sent_success(self):
        """Called when SMS is sent successfully"""
        self.sms_input.setEnabled(True)
        self.login_btn.setEnabled(True)
        
    def on_error(self, error_message: str):
        self.progress_label.setText("处理失败")
        self.status_label.setText(f"错误: {error_message}")
        QMessageBox.critical(self, "错误", error_message)
        self.reset_ui()
        
    def reset_ui(self):
        self.send_sms_btn.setEnabled(True)
        self.login_btn.setEnabled(False)
        self.phone_input.setEnabled(True)
        self.sms_input.setEnabled(False)
        self.sms_input.clear()
        # Keep action buttons enabled if we have login data
        if hasattr(self, 'current_login_data') and self.current_login_data:
            self.copy_token_btn.setEnabled(True)
            self.save_json_btn.setEnabled(True)
        else:
            self.copy_token_btn.setEnabled(False)
            self.save_json_btn.setEnabled(False)
        
    def clear_all(self):
        self.phone_input.clear()
        self.sms_input.clear()
        self.result_text.clear()
        self.status_label.setText("就绪")
        self.progress_label.setText("")
        # Clear stored login data
        if hasattr(self, 'current_login_data'):
            self.current_login_data = None
        self.reset_ui()

    def copy_token_to_clipboard(self):
        """Copy only the token value to clipboard"""
        if hasattr(self, 'current_login_data') and self.current_login_data:
            token = self.current_login_data.get('token', '')
            if token:
                clipboard = QApplication.clipboard()
                clipboard.setText(token)
                QMessageBox.information(self, "成功", "Token已复制到剪贴板")
            else:
                QMessageBox.warning(self, "警告", "未找到Token字段")
        else:
            QMessageBox.warning(self, "警告", "没有可用的登录数据")

    def save_as_json(self):
        """Save login data as JSON file with user-selected location"""
        if hasattr(self, 'current_login_data') and self.current_login_data:
            # Open file dialog for user to select save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存登录数据",
                "login_data.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:  # User selected a file
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_login_data, f, ensure_ascii=False, indent=4)
                    QMessageBox.information(self, "成功", f"数据已保存到: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存文件失败: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "没有可用的登录数据")


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = KuroLoginGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()