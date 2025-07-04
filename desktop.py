import threading
import webview
import time
import os
from app import app

def run_flask():
    app.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == '__main__':
    # 启动 Flask 后端
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    # 等待 Flask 启动
    time.sleep(1)
    # 打开更大4:3比例窗口（如1200x900）
    webview.create_window('视频下载', 'http://127.0.0.1:5000', width=1200, height=900, resizable=True)
    webview.start() 