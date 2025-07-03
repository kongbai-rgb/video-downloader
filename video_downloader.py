import sys
import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
import subprocess
import openpyxl
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yt_dlp
import requests
import tempfile
import shutil


class DownloadThread(QThread):
    """下载线程类"""
    progress = pyqtSignal(dict)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url, save_path, resolution, format_type, proxy=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.resolution = resolution
        self.format_type = format_type
        self.proxy = proxy
        self.is_cancelled = False
        self.temp_dir = tempfile.mkdtemp()
        
    def run(self):
        try:
            self.download_with_ytdlp()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # 清理临时目录
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def download_with_ytdlp(self):
        """使用yt-dlp下载视频"""
        # 基础配置
        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.yt_progress_hook],
            'quiet': True,
            'no_warnings': True,
            # 使用浏览器cookies
            'cookiesfrombrowser': ('chrome',),
            # 临时文件目录
            'paths': {'temp': self.temp_dir},
            # 网络选项
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
        }
        
        # 设置代理
        if self.proxy:
            ydl_opts['proxy'] = self.proxy
        
        # 设置格式
        if self.format_type == 'MP3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        else:
            # 处理分辨率
            resolution_num = self.resolution[:-1]  # 去掉 'p'
            if resolution_num == '4K':
                resolution_num = '2160'
            
            # 设置格式选择器
            format_selector = f'bestvideo[height<={resolution_num}]+bestaudio/best[height<={resolution_num}]/best'
            ydl_opts['format'] = format_selector
            
            # 格式转换
            if self.format_type != 'MP4':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': self.format_type.lower(),
                }]
        
        # 处理播放列表
        if 'playlist' in self.url or 'list=' in self.url:
            ydl_opts['outtmpl'] = os.path.join(self.save_path, '%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s')
        
        # 重试机制
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # 提取信息
                    info = ydl.extract_info(self.url, download=False)
                    
                    # 检查是否是播放列表
                    if info.get('_type') == 'playlist':
                        total_videos = len(info.get('entries', []))
                        self.progress.emit({
                            'status': f'发现播放列表，共{total_videos}个视频',
                            'percent': 0,
                            'speed': '',
                            'eta': ''
                        })
                    
                    # 开始下载
                    ydl.download([self.url])
                    
                    title = info.get('title', 'video')
                    self.finished.emit({'file': self.save_path, 'title': title})
                    return
                    
            except yt_dlp.utils.DownloadError as e:
                last_error = str(e)
                if "Private video" in last_error:
                    self.error.emit("这是私密视频，需要登录才能下载。请在Chrome浏览器中登录后重试。")
                    return
                elif "429" in last_error or "Too Many Requests" in last_error:
                    wait_time = 30 * (attempt + 1)
                    self.progress.emit({
                        'status': f'请求过多，等待{wait_time}秒后重试...',
                        'percent': 0,
                        'speed': '',
                        'eta': ''
                    })
                    time.sleep(wait_time)
                elif attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
        
        # 所有重试都失败
        error_msg = f"下载失败: {last_error}\n\n"
        error_msg += "解决方案：\n"
        error_msg += "1. 确保已安装最新版本的yt-dlp\n"
        error_msg += "2. 检查网络连接和代理设置\n"
        error_msg += "3. 在Chrome浏览器中登录对应网站"
        
        self.error.emit(error_msg)
    
    def yt_progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("下载已取消")
        
        if d['status'] == 'downloading':
            # 提取进度信息
            percent = 0
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                if d['total_bytes'] > 0:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif '_percent_str' in d:
                percent_str = d.get('_percent_str', '0%').replace('%', '').strip()
                try:
                    percent = float(percent_str)
                except:
                    percent = 0
            
            # 速度信息
            speed = d.get('_speed_str', 'N/A')
            
            # 剩余时间
            eta = d.get('_eta_str', 'N/A')
            
            # 文件大小信息
            size_info = ''
            if 'total_bytes' in d:
                total_mb = d['total_bytes'] / 1024 / 1024
                downloaded_mb = d.get('downloaded_bytes', 0) / 1024 / 1024
                size_info = f"{downloaded_mb:.1f}/{total_mb:.1f} MB"
            
            self.progress.emit({
                'percent': percent,
                'speed': speed,
                'eta': eta,
                'size': size_info,
                'status': d.get('status', 'downloading')
            })
        elif d['status'] == 'finished':
            self.progress.emit({
                'percent': 100,
                'speed': '完成',
                'eta': '',
                'size': '',
                'status': 'finished'
            })
    
    def cancel(self):
        self.is_cancelled = True


class VideoDownloader(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.download_history = []
        self.current_downloads = {}
        self.init_ui()
        self.load_settings()
        self.check_ffmpeg()
        
    def init_ui(self):
        self.setWindowTitle('视频下载器 v2.0')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                padding: 8px;
                font-size: 14px;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #ddd;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel('🎬 视频下载器')
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # URL输入区域
        url_group = QGroupBox("链接输入")
        url_layout = QVBoxLayout()
        
        # URL输入框
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入视频链接...")
        self.url_input.returnPressed.connect(self.start_download)
        url_input_layout.addWidget(self.url_input)
        
        # 粘贴按钮
        paste_btn = QPushButton("📋 粘贴")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        paste_btn.setMaximumWidth(80)
        url_input_layout.addWidget(paste_btn)
        
        url_layout.addLayout(url_input_layout)
        
        # 批量导入按钮
        batch_btn = QPushButton("📊 从Excel导入")
        batch_btn.clicked.connect(self.import_from_excel)
        url_layout.addWidget(batch_btn)
        
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # 下载设置
        settings_group = QGroupBox("下载设置")
        settings_layout = QGridLayout()
        
        # 分辨率选择
        settings_layout.addWidget(QLabel("分辨率:"), 0, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(['720p', '1080p', '4K'])
        self.resolution_combo.setCurrentText('1080p')
        settings_layout.addWidget(self.resolution_combo, 0, 1)
        
        # 格式选择
        settings_layout.addWidget(QLabel("格式:"), 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP4', 'MP3'])
        settings_layout.addWidget(self.format_combo, 0, 3)
        
        # 保存路径
        settings_layout.addWidget(QLabel("保存路径:"), 1, 0)
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home() / "Videos"))
        settings_layout.addWidget(self.path_input, 1, 1, 1, 2)
        
        path_btn = QPushButton("📁")
        path_btn.clicked.connect(self.select_save_path)
        path_btn.setMaximumWidth(50)
        settings_layout.addWidget(path_btn, 1, 3)
        
        # 代理设置
        settings_layout.addWidget(QLabel("代理:"), 2, 0)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:1080 (可选)")
        settings_layout.addWidget(self.proxy_input, 2, 1, 1, 3)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # 下载按钮
        download_btn = QPushButton("⬇️ 开始下载")
        download_btn.clicked.connect(self.start_download)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                font-size: 16px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        main_layout.addWidget(download_btn)
        
        # 进度显示
        progress_group = QGroupBox("下载进度")
        progress_layout = QVBoxLayout()
        
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(6)
        self.progress_table.setHorizontalHeaderLabels(['文件名', '进度', '速度', '大小', '剩余时间', '操作'])
        self.progress_table.horizontalHeader().setStretchLastSection(True)
        progress_layout.addWidget(self.progress_table)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # 历史记录
        history_group = QGroupBox("历史记录")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        self.history_list.itemDoubleClicked.connect(self.use_history_url)
        history_layout.addWidget(self.history_list)
        
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        # 状态栏
        self.statusBar().showMessage('就绪')
        
        # 创建菜单栏
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        update_action = QAction('更新yt-dlp', self)
        update_action.triggered.connect(self.update_ytdlp)
        tools_menu.addAction(update_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)
    
    def select_save_path(self):
        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if folder:
            self.path_input.setText(folder)
    
    def import_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Excel文件", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
                urls = []
                
                for row in ws.iter_rows(values_only=True):
                    for cell in row:
                        if cell and isinstance(cell, str) and ('http' in str(cell) or 'www.' in str(cell)):
                            urls.append(str(cell))
                
                if urls:
                    msg = f"找到 {len(urls)} 个链接，是否全部下载？"
                    reply = QMessageBox.question(self, '确认批量下载', msg)
                    if reply == QMessageBox.Yes:
                        for url in urls:
                            self.url_input.setText(url)
                            self.start_download()
                            time.sleep(0.5)
                else:
                    QMessageBox.information(self, '提示', '未找到有效链接')
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'读取Excel失败: {str(e)}')
    
    @pyqtSlot(str)
    def show_video_info(self, info_text):
        QMessageBox.information(self, '视频信息', info_text)
    
    @pyqtSlot(str)
    def show_error(self, error_msg):
        QMessageBox.critical(self, '错误', error_msg)
    
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, '警告', '请输入链接')
            return
        
        # 添加到历史记录
        if url not in self.download_history:
            self.download_history.append(url)
            self.history_list.addItem(url)
            self.save_history()
        
        # 创建下载线程
        save_path = self.path_input.text()
        resolution = self.resolution_combo.currentText()
        format_type = self.format_combo.currentText()
        proxy = self.proxy_input.text().strip() if self.proxy_input.text().strip() else None
        
        thread = DownloadThread(url, save_path, resolution, format_type, proxy)
        thread.progress.connect(lambda data, u=url: self.update_progress(u, data))
        thread.finished.connect(lambda data, u=url: self.download_finished(u, data))
        thread.error.connect(lambda msg, u=url: self.download_error(u, msg))
        
        # 添加到进度表
        row = self.progress_table.rowCount()
        self.progress_table.insertRow(row)
        
        # 文件名
        filename_item = QTableWidgetItem(url[:50] + '...' if len(url) > 50 else url)
        self.progress_table.setItem(row, 0, filename_item)
        
        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setTextVisible(True)
        self.progress_table.setCellWidget(row, 1, progress_bar)
        
        # 其他列
        for col in range(2, 5):
            self.progress_table.setItem(row, col, QTableWidgetItem(''))
        
        # 操作按钮
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(lambda: self.cancel_download(url))
        self.progress_table.setCellWidget(row, 5, cancel_btn)
        
        self.current_downloads[url] = {
            'thread': thread,
            'row': row,
            'progress_bar': progress_bar
        }
        
        thread.start()
        self.statusBar().showMessage(f'开始下载: {url}')
    
    def update_progress(self, url, data):
        if url in self.current_downloads:
            info = self.current_downloads[url]
            progress_bar = info['progress_bar']
            row = info['row']
            
            # 更新进度条
            percent = int(data.get('percent', 0))
            progress_bar.setValue(percent)
            
            # 更新其他信息
            self.progress_table.item(row, 2).setText(data.get('speed', ''))
            self.progress_table.item(row, 3).setText(data.get('size', ''))
            self.progress_table.item(row, 4).setText(data.get('eta', ''))
    
    def download_finished(self, url, data):
        if url in self.current_downloads:
            info = self.current_downloads[url]
            row = info['row']
            
            # 更新状态
            self.progress_table.item(row, 2).setText('完成')
            self.progress_table.item(row, 4).setText(data.get('title', ''))
            
            # 更新按钮
            open_btn = QPushButton('打开文件夹')
            open_btn.clicked.connect(lambda: self.open_download_folder())
            self.progress_table.setCellWidget(row, 5, open_btn)
            
            del self.current_downloads[url]
            
            self.statusBar().showMessage(f'下载完成: {data.get("title", url)}')
            QMessageBox.information(self, '下载完成', f'文件已保存: {data.get("title", "video")}')
    
    def download_error(self, url, msg):
        if url in self.current_downloads:
            info = self.current_downloads[url]
            row = info['row']
            
            self.progress_table.item(row, 2).setText('失败')
            self.progress_table.item(row, 4).setText(msg[:30])
            
            del self.current_downloads[url]
        
        self.statusBar().showMessage(f'下载失败')
        QMessageBox.critical(self, '下载失败', msg)
    
    def cancel_download(self, url):
        if url in self.current_downloads:
            self.current_downloads[url]['thread'].cancel()
            self.current_downloads[url]['thread'].quit()
            
            row = self.current_downloads[url]['row']
            self.progress_table.item(row, 2).setText('已取消')
            
            del self.current_downloads[url]
            self.statusBar().showMessage('下载已取消')
    
    def open_download_folder(self):
        folder = self.path_input.text()
        if os.path.exists(folder):
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])
    
    def use_history_url(self, item):
        self.url_input.setText(item.text())
    
    def update_ytdlp(self):
        """更新yt-dlp"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                QMessageBox.information(self, '成功', 'yt-dlp更新成功！')
            else:
                QMessageBox.critical(self, '错误', f'更新失败: {result.stderr}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'更新错误: {str(e)}')
    
    def show_about(self):
        about_text = """视频下载器 v2.0

基于 yt-dlp 的视频下载工具

支持网站：
• YouTube
• Instagram  
• Twitter
• TikTok
• 以及1000+其他网站

© 2024 Video Downloader"""
        
        QMessageBox.about(self, '关于', about_text)
    
    def check_ffmpeg(self):
        """检查FFmpeg"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
        except:
            self.statusBar().showMessage('警告: FFmpeg未安装，部分功能可能受限')
    
    def save_history(self):
        """保存历史记录"""
        try:
            with open('download_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.download_history[-20:], f)  # 只保存最近20条
        except:
            pass
    
    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists('download_history.json'):
                with open('download_history.json', 'r', encoding='utf-8') as f:
                    self.download_history = json.load(f)
                    for url in self.download_history:
                        self.history_list.addItem(url)
        except:
            pass
    
    def load_settings(self):
        """加载设置"""
        settings_file = 'settings.json'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.path_input.setText(settings.get('save_path', str(Path.home() / "Videos")))
                    self.proxy_input.setText(settings.get('proxy', ''))
                    self.resolution_combo.setCurrentText(settings.get('resolution', '1080p'))
                    self.format_combo.setCurrentText(settings.get('format', 'MP4'))
            except:
                pass
        
        # 加载历史记录
        self.load_history()
    
    def save_settings(self):
        """保存设置"""
        settings = {
            'save_path': self.path_input.text(),
            'proxy': self.proxy_input.text(),
            'resolution': self.resolution_combo.currentText(),
            'format': self.format_combo.currentText()
        }
        
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f)
        except:
            pass
    
    def closeEvent(self, event):
        """关闭事件"""
        # 保存设置
        self.save_settings()
        self.save_history()
        
        # 取消所有下载
        if self.current_downloads:
            reply = QMessageBox.question(self, '确认退出', 
                                       f'还有{len(self.current_downloads)}个下载任务正在进行，确定要退出吗？')
            if reply == QMessageBox.Yes:
                for url in list(self.current_downloads.keys()):
                    self.cancel_download(url)
            else:
                event.ignore()
                return
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 创建主窗口
    downloader = VideoDownloader()
    downloader.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()