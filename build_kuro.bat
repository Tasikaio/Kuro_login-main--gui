@echo off
echo 开始打包Kuro登录工具...
python -m nuitka --standalone --onefile --windows-disable-console --output-dir=C:\Users\cool1\Desktop\Kuro_login-main\dist_nuitka --output-filename=KuroLogin --include-package=geetest_captcha --include-package=utils --include-module=PyQt5 --include-module=PyQt5.QtCore --include-module=PyQt5.QtGui --include-module=PyQt5.QtWidgets --include-data-dir=geetest_captcha=geetest_captcha --include-data-dir=utils=utils --remove-output --assume-yes-for-downloads --windows-icon-from-ico=favicon.ico --windows-company-name=KuroLogin --windows-product-name=Kuro登录工具 --windows-file-version=1.0.0 --windows-product-version=1.0.0 C:\Users\cool1\Desktop\Kuro_login-main\kuro_login_gui.py
echo 打包完成！
pause