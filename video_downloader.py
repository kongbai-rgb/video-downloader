@pyqtSlot(str)
    def show_video_info(self, info_text):
        QMessageBox.information(self, '视频信息', info_text)
    
    @pyqtSlot(str)
    def show_error(self, error_msg):
        QMessageBox.critical(self, '错误', error_msg)
    
    def download_playlist_info(self):
        """显示播放列表下载选项"""
        dialog = QDialog(self)
        dialog.setWindowTitle('播放列表下载设置')
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # 说明
        info_label = QLabel('输入播放列表链接，可以选择下载范围')
        layout.addWidget(info_label)
        
        # 范围选择
        range_group = QGroupBox('下载范围')
        range_layout = QGridLayout()
        
        self.all_radio = QRadioButton('下载全部')
        self.all_radio.setChecked(True)
        range_layout.addWidget(self.all_radio, 0, 0)
        
        self.range_radio = QRadioButton('指定范围')
        range_layout.addWidget(self.range_radio, 1, 0)
        
        range_layout.addWidget(QLabel('从:'), 1, 1)
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setValue(1)
        range_layout.addWidget(self.start_spin, 1, 2)
        
        range_layout.addWidget(QLabel('到:'), 1, 3)
        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        self.end_spin.setValue(10)
        range_layout.addWidget(self.end_spin, 1, 4)
        
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # 处理播放列表下载
            self.playlist_range = None
            if self.range_radio.isChecked():
                self.playlist_range = (self.start_spin.value(), self.end_spin.value())
            self.start_download()
    
    def clear_completed(self):
        """清除已完成的下载项"""
        rows_to_remove = []
        for row in range(self.progress_table.rowCount()):
            if self.progress_table.item(row, 2) and self.progress_table.item(row, 2).text() == '完成':
                rows_to_remove.append(row)
        
        for row in reversed(rows_to_remove):
            self.progress_table.removeRow(row)
    
    def clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(self, '确认', '确定要清空所有历史记录吗？')
        if reply == QMessageBox.Yes:
            self.download_history.clear()
            self.history_list.clear()
            self.save_history()
    
    def export_history(self):
        """导出历史记录"""
        if not self.download_history:
            QMessageBox.information(self, '提示', '历史记录为空')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存历史记录", "", "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for url in self.download_history:
                        f.write(url + '\n')
                QMessageBox.information(self, '成功', '历史记录已导出')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导出失败: {str(e)}')
    
    def export_settings(self):
        """导出当前设置"""
        settings = {
            'save_path': self.path_input.text(),
            'proxy': self.proxy_input.text(),
            'resolution': self.resolution_combo.currentText(),
            'format': self.format_combo.currentText(),
            'quality': self.quality_combo.currentText(),
            'download_subtitles': self.subtitle_check.isChecked()
        }
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存设置", "settings.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
                QMessageBox.information(self, '成功', '设置已导出')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导出失败: {str(e)}')
    
    def update_ytdlp(self):
        """更新yt-dlp"""
        self.log("开始更新yt-dlp...")
        try:
            # 在新线程中运行更新
            thread = threading.Thread(target=self._update_ytdlp_thread)
            thread.start()
        except Exception as e:
            self.log(f"更新失败: {str(e)}")
    
    def _update_ytdlp_thread(self):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                QMetaObject.invokeMethod(self, "log", Qt.QueuedConnection, 
                                       Q_ARG(str, "yt-dlp更新成功！"))
            else:
                QMetaObject.invokeMethod(self, "log", Qt.QueuedConnection, 
                                       Q_ARG(str, f"更新失败: {result.stderr}"))
        except Exception as e:
            QMetaObject.invokeMethod(self, "log", Qt.QueuedConnection, 
                                   Q_ARG(str, f"更新错误: {str(e)}"))
    
    def test_downloader(self):
        """测试下载器功能"""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.url_input.setText(test_url)
        self.log("使用测试链接进行测试...")
        QMessageBox.information(self, '测试', f'已填入测试链接:\n{test_url}\n\n点击"获取信息"查看视频信息')
    
    def configure_browser_cookies(self):
        """配置浏览器Cookies"""
        dialog = QDialog(self)
        dialog.setWindowTitle('浏览器Cookies配置')
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # 说明
        info_text = """选择要使用的浏览器Cookies：
        
1. Chrome - 推荐，自动检测
2. Firefox - 需要先在Firefox中登录
3. Edge - Windows用户推荐
4. Safari - macOS用户

注意：请先在对应浏览器中登录Instagram/YouTube"""
        
        info_label = QLabel(info_text)
        layout.addWidget(info_label)
        
        # 浏览器选择
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(['chrome', 'firefox', 'edge', 'safari', 'brave', 'chromium'])
        layout.addWidget(self.browser_combo)
        
        # 测试按钮
        test_btn = QPushButton('测试Cookies')
        test_btn.clicked.connect(self.test_browser_cookies)
        layout.addWidget(test_btn)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton('保存')
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            self.selected_browser = self.browser_combo.currentText()
            self.save_settings()
            QMessageBox.information(self, '成功', f'已设置使用{self.selected_browser}浏览器的Cookies')
    
    def test_browser_cookies(self):
        """测试浏览器Cookies"""
        browser = self.browser_combo.currentText()
        try:
            ydl_opts = {
                'cookiesfrombrowser': (browser,),
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 尝试提取cookies
                ydl._setup_opener()
                QMessageBox.information(self, '成功', f'{browser}浏览器Cookies读取成功！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取{browser} Cookies失败:\n{str(e)}')
    
    def show_manual(self):
        """显示使用说明"""
        manual_text = """视频下载器 v2.0 使用说明

基本功能：
1. 支持YouTube和Instagram视频下载
2. 支持播放列表批量下载
3. 支持多种分辨率和格式
4. 自动下载字幕和缩略图

使用步骤：
1. 输入或粘贴视频链接
2. 选择下载设置（分辨率、格式等）
3. 点击"开始下载"

高级功能：
- 批量下载：使用Excel导入多个链接
- 播放列表：自动识别并下载整个列表
- 代理支持：配置HTTP代理绕过限制
- 浏览器Cookies：自动使用浏览器登录状态

常见问题：
Q: 下载失败怎么办？
A: 1. 更新yt-dlp (工具菜单)
   2. 检查代理设置
   3. 在浏览器中登录账号

Q: 如何下载私密视频？
A: 先在Chrome中登录账号，程序会自动使用Cookies

更多帮助请访问：
https://github.com/yt-dlp/yt-dlp"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle('使用说明')
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(manual_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_about(self):
        """显示关于信息"""
        about_text = """视频下载器 Pro v2.0

基于 yt-dlp 的强大视频下载工具

特性：
• 支持 1000+ 网站
• 智能格式选择
• 批量下载支持
• 播放列表下载
• 自动字幕下载
• 代理和Cookies支持

开发基于：
- yt-dlp (视频下载核心)
- PyQt5 (图形界面)
- Python 3.8+

© 2024 Video Downloader Pro"""
        
        QMessageBox.about(self, '关于', about_text)
    
    def check_updates(self):
        """检查更新"""
        self.log("检查更新...")
        self.update_ytdlp()
    
    def check_dependencies(self):
        """检查依赖"""
        try:
            # 检查ffmpeg
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
            if result.returncode == 0:
                self.log("FFmpeg已安装")
            else:
                self.log("警告: FFmpeg未安装，部分功能可能受限")
        except:
            self.log("警告: FFmpeg未找到，请安装FFmpeg以获得完整功能")
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def select_save_path(self):
        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if folder:
            self.path_input.setText(folder)
            self.log(f"保存路径设置为: {folder}")
    
    def import_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Excel文件", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
                urls = []
                
                for row in ws.iter_rows(values_only=True):
                    for cell in row:
                        if cell and isinstance(cell, str):
                            # 检查是否包含支持的网站
                            if any(site in str(cell) for site in ['youtube.com', 'youtu.be', 'instagram.com', 'instagr.am']):
                                urls.append(str(cell))
                
                if urls:
                    self.log(f"从Excel导入了{len(urls)}个链接")
                    
                    # 显示确认对话框
                    msg = f"找到 {len(urls)} 个链接:\n\n"
                    msg += "\n".join(urls[:5])  # 显示前5个
                    if len(urls) > 5:
                        msg += f"\n... 还有 {len(urls)-5} 个"
                    msg += "\n\n是否全部下载？"
                    
                    reply = QMessageBox.question(self, '确认批量下载', msg)
                    if reply == QMessageBox.Yes:
                        for url in urls:
                            self.url_input.setText(url)
                            self.start_download()
                            time.sleep(0.5)  # 避免太快
                else:
                    QMessageBox.information(self, '提示', '未找到有效链接')
                    self.log("Excel中未找到有效链接")
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'读取Excel失败: {str(e)}')
                self.log(f"Excel读取错误: {str(e)}")
    
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, '警告', '请输入链接')
            return
        
        # 验证URL
        supported_sites = ['youtube.com', 'youtu.be', 'instagram.com', 'instagr.am', 
                          'twitter.com', 'x.com', 'tiktok.com', 'facebook.com']
        
        if not any(site in url.lower() for site in supported_sites):
            reply = QMessageBox.question(self, '确认', 
                                       '这个链接可能不被支持，是否继续尝试下载？\n\n'
                                       '支持的网站包括：YouTube, Instagram, Twitter, TikTok等')
            if reply != QMessageBox.Yes:
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
        quality_pref = self.quality_combo.currentText()
        proxy = self.proxy_input.text().strip() if self.proxy_input.text().strip() else None
        
        thread = DownloadThread(url, save_path, resolution, format_type, quality_pref, proxy)
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
        
        # 速度
        self.progress_table.setItem(row, 2, QTableWidgetItem('准备中...'))
        
        # 大小
        self.progress_table.setItem(row, 3, QTableWidgetItem(''))
        
        # 剩余时间
        self.progress_table.setItem(row, 4, QTableWidgetItem(''))
        
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
        self.log(f"开始下载: {url}")
    
    def update_progress(self, url, data):
        if url in self.current_downloads:
            info = self.current_downloads[url]
            progress_bar = info['progress_bar']
            row = info['row']
            
            # 更新进度条
            percent = int(data.get('percent', 0))
            progress_bar.setValue(percent)
            
            # 更新速度
            speed = data.get('speed', '')
            if speed:
                self.progress_table.item(row, 2).setText(speed)
            
            # 更新大小
            size = data.get('size', '')
            if size:
                self.progress_table.item(row, 3).setText(size)
            
            # 更新剩余时间
            eta = data.get('eta', '')
            if eta:
                self.progress_table.item(row, 4).setText(eta)
            
            # 更新状态
            status = data.get('status', '')
            if status and status != 'downloading':
                self.progress_table.item(row, 2).setText(status)
    
    def download_finished(self, url, data):
        if url in self.current_downloads:
            info = self.current_downloads[url]
            row = info['row']
            
            # 更新状态
            self.progress_table.item(row, 2).setText('完成')
            self.progress_table.item(row, 3).setText('')
            self.progress_table.item(row, 4).setText(data.get('title', ''))
            
            # 更新按钮
            open_btn = QPushButton('打开文件夹')
            open_btn.clicked.connect(lambda: self.open_download_folder())
            self.progress_table.setCellWidget(row, 5, open_btn)
            
            del self.current_downloads[url]
            
            title = data.get('title', url)
            self.statusBar().showMessage(f'下载完成: {title}')
            self.log(f"下载完成: {title}")
            
            # 显示通知
            self.show_notification('下载完成', f'已下载: {title}')
    
    def download_error(self, url, msg):
        if url in self.current_downloads:
            info = self.current_downloads[url]
            row = info['row']
            
            self.progress_table.item(row, 2).setText('失败')
            self.progress_table.item(row, 3).setText('')
            self.progress_table.item(row, 4).setText(msg[:30] + '...' if len(msg) > 30 else msg)
            
            # 重试按钮
            retry_btn = QPushButton('重试')
            retry_btn.clicked.connect(lambda: self.retry_download(url))
            self.progress_table.setCellWidget(row, 5, retry_btn)
            
            del self.current_downloads[url]
        
        self.statusBar().showMessage(f'下载失败')
        self.log(f"下载失败 [{url}]: {msg}")
        
        # 显示详细错误信息
        QMessageBox.critical(self, '下载失败', msg)
    
    def cancel_download(self, url):
        if url in self.current_downloads:
            self.current_downloads[url]['thread'].cancel()
            self.current_downloads[url]['thread'].quit()
            self.current_downloads[url]['thread'].wait()
            
            row = self.current_downloads[url]['row']
            self.progress_table.item(row, 2).setText('已取消')
            
            del self.current_downloads[url]
            self.statusBar().showMessage('下载已取消')
            self.log(f"下载已取消: {url}")
    
    def retry_download(self, url):
        """重试下载"""
        self.url_input.setText(url)
        # 先移除失败的行
        for row in range(self.progress_table.rowCount()):
            if self.progress_table.item(row, 0) and url in self.progress_table.item(row, 0).text():
                self.progress_table.removeRow(row)
                break
        # 重新开始下载
        self.start_download()
    
    def open_download_folder(self):
        """打开下载文件夹"""
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
        self.log(f"使用历史记录: {item.text()}")
    
    def show_notification(self, title, message):
        """显示系统通知"""
        try:
            from PyQt5.QtWidgets import QSystemTrayIcon
            if QSystemTrayIcon.isSystemTrayAvailable():
                tray = QSystemTrayIcon(self)
                tray.showMessage(title, message, QSystemTrayIcon.Information, 3000)
        except:
            pass
    
    def save_history(self):
        """保存历史记录"""
        try:
            with open('download_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
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
        """加载保存的设置"""
        settings_file = 'settings.json'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.path_input.setText(settings.get('save_path', str(Path.home() / "Videos")))
                    self.proxy_input.setText(settings.get('proxy', ''))
                    self.resolution_combo.setCurrentText(settings.get('resolution', '1080p'))
                    self.format_combo.setCurrentText(settings.get('format', 'MP4'))
                    self.quality_combo.setCurrentText(settings.get('quality', '高帧率'))
                    self.subtitle_check.setChecked(settings.get('download_subtitles', True))
                    self.selected_browser = settings.get('browser', 'chrome')
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
            'format': self.format_combo.currentText(),
            'quality': self.quality_combo.currentText(),
            'download_subtitles': self.subtitle_check.isChecked(),
            'browser': getattr(self, 'selected_browser', 'chrome')
        }
        
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
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

class DropArea(QLabel):
    """支持拖放的区域"""
    dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setText("将链接拖放到此处\n或在下方输入")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #aaa;
                padding: 40px;
                background-color: #fafafa;
                border-radius: 10px;
                font-size: 16px;
                color: #666;
                min-height: 100px;
            }
            QLabel:hover {
                border-color: #4CAF50;
                background-color: #f0f8f0;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 3px dashed #4CAF50;
                    padding: 40px;
                    background-color: #e8f5e9;
                    border-radius: 10px;
                    font-size: 16px;
                    color: #2e7d32;
                    min-height: 100px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #aaa;
                padding: 40px;
                background-color: #fafafa;
                border-radius: 10px;
                font-size: 16px;
                color: #666;
                min-height: 100px;
            }
        """)
    
    def dropEvent(self, event):
        text = event.mimeData().text()
        self.dropped.emit(text)
        self.dragLeaveEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用现代化的界面风格
    
    # 设置应用图标
    app.setWindowIcon(QIcon())
    
    # 启动画面
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(QColor('#2196F3'))
    painter = QPainter(splash_pix)
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont('Arial', 24, QFont.Bold))
    painter.drawText(splash_pix.rect(), Qt.AlignCenter, '视频下载器\nPro v2.0')
    painter.end()
    
    splash = QSplashScreen(splash_pix)
    splash.show()
    app.processEvents()
    
    # 创建主窗口
    downloader = VideoDownloader()
    
    # 延迟显示主窗口
    QTimer.singleShot(1500, lambda: (splash.close(), downloader.show()))
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()import sys
import os
import re
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
    progress = pyqtSignal(dict)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url, save_path, resolution, format_type, quality_pref, proxy=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.resolution = resolution
        self.format_type = format_type
        self.quality_pref = quality_pref
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
        """统一使用yt-dlp下载YouTube和Instagram"""
        # 基础配置
        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s_%(height)sp.%(ext)s'),
            'progress_hooks': [self.yt_progress_hook],
            'quiet': False,
            'no_warnings': False,
            'verbose': True,
            # 使用浏览器cookies（支持Chrome, Firefox, Edge等）
            'cookiesfrombrowser': ('chrome',),
            # 临时文件目录
            'paths': {'temp': self.temp_dir},
            # 网络选项
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            # 绕过地理限制
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            # 自动处理播放列表
            'playlistend': None,
            'noplaylist': False,
            # 标记已观看（可选）
            'mark_watched': False,
            # 强制使用IPv4
            'source_address': '0.0.0.0',
        }
        
        # 设置代理
        if self.proxy:
            ydl_opts['proxy'] = self.proxy
        
        # Instagram特殊处理
        if 'instagram.com' in self.url or 'instagr.am' in self.url:
            ydl_opts['outtmpl'] = os.path.join(self.save_path, 'instagram_%(id)s_%(title)s.%(ext)s')
            # Instagram需要更多的headers
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        
        # 设置格式
        if self.format_type == 'MP3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
            ydl_opts['outtmpl'] = os.path.join(self.save_path, '%(title)s.%(ext)s')
        else:
            # 处理分辨率
            resolution_num = self.resolution[:-1]  # 去掉 'p'
            if resolution_num == '4K':
                resolution_num = '2160'
            
            # 根据质量偏好设置格式选择器
            if self.quality_pref == '高帧率':
                # 优先选择60fps的视频
                format_selector = f'bestvideo[height<={resolution_num}][fps>=60]+bestaudio/bestvideo[height<={resolution_num}]+bestaudio/best[height<={resolution_num}]/best'
            else:
                # 优先选择高码率
                format_selector = f'bestvideo[height<={resolution_num}][vcodec^=avc]+bestaudio/bestvideo[height<={resolution_num}]+bestaudio/best[height<={resolution_num}]/best'
            
            ydl_opts['format'] = format_selector
            
            # 后处理器设置
            postprocessors = []
            
            # 格式转换
            if self.format_type != 'MP4':
                postprocessors.append({
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': self.format_type.lower(),
                })
            
            # 嵌入缩略图
            postprocessors.append({
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            })
            
            # 添加元数据
            postprocessors.append({
                'key': 'FFmpegMetadata',
                'add_chapters': True,
                'add_metadata': True,
            })
            
            ydl_opts['postprocessors'] = postprocessors
            
            # 下载缩略图
            ydl_opts['writethumbnail'] = True
            
            # 下载字幕
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['en', 'zh-CN', 'zh-TW']
        
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
                    wait_time = min(60 * (attempt + 1), 300)  # 最多等待5分钟
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
        error_msg += "3. 在Chrome浏览器中登录对应网站\n"
        error_msg += "4. 运行更新工具：update_tools.bat"
        
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
            speed = d.get('_speed_str', d.get('speed_str', 'N/A'))
            if speed == 'N/A' and 'speed' in d and d['speed']:
                speed = f"{d['speed']/1024:.1f} KB/s"
            
            # 剩余时间
            eta = d.get('_eta_str', d.get('eta_str', 'N/A'))
            if eta == 'N/A' and 'eta' in d and d['eta']:
                eta = f"{d['eta']}秒"
            
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
    def __init__(self):
        super().__init__()
        self.download_history = []
        self.current_downloads = {}
        self.init_ui()
        self.load_settings()
        self.check_dependencies()
        
    def init_ui(self):
        self.setWindowTitle('视频下载器 v2.0 - 支持YouTube/Instagram')
        self.setGeometry(100, 100, 1000, 800)
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
        
        # 标题和版本信息
        header_layout = QHBoxLayout()
        title_label = QLabel('🎬 视频下载器 Pro')
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)
        
        version_label = QLabel('v2.0 | 支持YouTube/Instagram')
        version_label.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(version_label)
        header_layout.addStretch()
        
        # 更新按钮
        update_btn = QPushButton("🔄 检查更新")
        update_btn.clicked.connect(self.check_updates)
        update_btn.setStyleSheet("background-color: #2196F3;")
        header_layout.addWidget(update_btn)
        
        main_layout.addLayout(header_layout)
        
        # URL输入区域
        url_group = QGroupBox("📎 链接输入")
        url_layout = QVBoxLayout()
        
        # 拖拽区域
        self.drop_area = DropArea()
        self.drop_area.dropped.connect(self.handle_drop)
        url_layout.addWidget(self.drop_area)
        
        # URL输入框
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入或粘贴YouTube/Instagram链接...")
        self.url_input.returnPressed.connect(self.start_download)
        url_input_layout.addWidget(self.url_input)
        
        # 粘贴按钮
        paste_btn = QPushButton("📋 粘贴")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        paste_btn.setMaximumWidth(80)
        url_input_layout.addWidget(paste_btn)
        
        url_layout.addLayout(url_input_layout)
        
        # 批量操作按钮
        batch_layout = QHBoxLayout()
        
        batch_btn = QPushButton("📊 从Excel导入")
        batch_btn.clicked.connect(self.import_from_excel)
        batch_layout.addWidget(batch_btn)
        
        playlist_btn = QPushButton("📁 下载整个播放列表")
        playlist_btn.clicked.connect(self.download_playlist_info)
        batch_layout.addWidget(playlist_btn)
        
        url_layout.addLayout(batch_layout)
        
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # 下载设置
        settings_group = QGroupBox("⚙️ 下载设置")
        settings_layout = QGridLayout()
        
        # 分辨率选择
        settings_layout.addWidget(QLabel("分辨率:"), 0, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(['360p', '480p', '720p', '1080p', '1440p', '4K'])
        self.resolution_combo.setCurrentText('1080p')
        settings_layout.addWidget(self.resolution_combo, 0, 1)
        
        # 格式选择
        settings_layout.addWidget(QLabel("格式:"), 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP4', 'MKV', 'WebM', 'AVI', 'MP3'])
        settings_layout.addWidget(self.format_combo, 0, 3)
        
        # 质量偏好
        settings_layout.addWidget(QLabel("质量偏好:"), 1, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['高帧率', '高码率'])
        settings_layout.addWidget(self.quality_combo, 1, 1)
        
        # 字幕选项
        settings_layout.addWidget(QLabel("字幕:"), 1, 2)
        self.subtitle_check = QCheckBox("下载字幕")
        self.subtitle_check.setChecked(True)
        settings_layout.addWidget(self.subtitle_check, 1, 3)
        
        # 保存路径
        settings_layout.addWidget(QLabel("保存路径:"), 2, 0)
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home() / "Videos"))
        settings_layout.addWidget(self.path_input, 2, 1, 1, 2)
        
        path_btn = QPushButton("📁 选择")
        path_btn.clicked.connect(self.select_save_path)
        path_btn.setMaximumWidth(80)
        settings_layout.addWidget(path_btn, 2, 3)
        
        # 代理设置
        settings_layout.addWidget(QLabel("代理:"), 3, 0)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:9090 (可选)")
        self.proxy_input.setText("http://127.0.0.1:9090")
        settings_layout.addWidget(self.proxy_input, 3, 1, 1, 2)
        
        # 测试代理按钮
        test_proxy_btn = QPushButton("🔍 测试")
        test_proxy_btn.clicked.connect(self.test_proxy)
        test_proxy_btn.setMaximumWidth(80)
        settings_layout.addWidget(test_proxy_btn, 3, 3)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # 下载按钮
        download_layout = QHBoxLayout()
        
        download_btn = QPushButton("⬇️ 开始下载")
        download_btn.clicked.connect(self.start_download)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                font-size: 18px;
                padding: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        download_layout.addWidget(download_btn)
        
        # 获取视频信息按钮
        info_btn = QPushButton("ℹ️ 获取信息")
        info_btn.clicked.connect(self.get_video_info)
        info_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                font-size: 16px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        info_btn.setMaximumWidth(150)
        download_layout.addWidget(info_btn)
        
        main_layout.addLayout(download_layout)
        
        # 进度显示
        progress_group = QGroupBox("📊 下载进度")
        progress_layout = QVBoxLayout()
        
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(6)
        self.progress_table.setHorizontalHeaderLabels(['文件名', '进度', '速度', '大小', '剩余时间', '操作'])
        self.progress_table.horizontalHeader().setStretchLastSection(True)
        self.progress_table.setAlternatingRowColors(True)
        progress_layout.addWidget(self.progress_table)
        
        # 清空完成的下载
        clear_btn = QPushButton("🗑️ 清空已完成")
        clear_btn.clicked.connect(self.clear_completed)
        clear_btn.setMaximumWidth(150)
        progress_layout.addWidget(clear_btn, alignment=Qt.AlignRight)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # 历史记录标签页
        tab_widget = QTabWidget()
        
        # 历史记录
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.use_history_url)
        history_layout.addWidget(self.history_list)
        
        # 历史记录操作按钮
        history_btn_layout = QHBoxLayout()
        clear_history_btn = QPushButton("清空历史")
        clear_history_btn.clicked.connect(self.clear_history)
        history_btn_layout.addWidget(clear_history_btn)
        
        export_history_btn = QPushButton("导出历史")
        export_history_btn.clicked.connect(self.export_history)
        history_btn_layout.addWidget(export_history_btn)
        
        history_layout.addLayout(history_btn_layout)
        history_widget.setLayout(history_layout)
        
        tab_widget.addTab(history_widget, "📜 历史记录")
        
        # 日志标签页
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_widget.setLayout(log_layout)
        tab_widget.addTab(log_widget, "📝 日志")
        
        main_layout.addWidget(tab_widget)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('就绪')
        
        # 创建菜单栏
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        import_action = QAction('导入链接', self)
        import_action.triggered.connect(self.import_from_excel)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出设置', self)
        export_action.triggered.connect(self.export_settings)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        update_action = QAction('更新yt-dlp', self)
        update_action.triggered.connect(self.update_ytdlp)
        tools_menu.addAction(update_action)
        
        test_action = QAction('测试下载器', self)
        test_action.triggered.connect(self.test_downloader)
        tools_menu.addAction(test_action)
        
        browser_action = QAction('配置浏览器Cookies', self)
        browser_action.triggered.connect(self.configure_browser_cookies)
        tools_menu.addAction(browser_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        manual_action = QAction('使用说明', self)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)
            self.log("从剪贴板粘贴: " + text)
    
    def handle_drop(self, text):
        self.url_input.setText(text)
        self.log("拖放链接: " + text)
    
    def test_proxy(self):
        proxy = self.proxy_input.text().strip()
        if not proxy:
            QMessageBox.information(self, '提示', '未设置代理')
            return
        
        try:
            response = requests.get('https://www.youtube.com', 
                                  proxies={'http': proxy, 'https': proxy}, 
                                  timeout=10)
            if response.status_code == 200:
                QMessageBox.information(self, '成功', '代理连接成功！')
                self.log(f"代理测试成功: {proxy}")
            else:
                QMessageBox.warning(self, '失败', f'代理返回状态码: {response.status_code}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'代理连接失败: {str(e)}')
            self.log(f"代理测试失败: {str(e)}")
    
    def get_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, '警告', '请输入链接')
            return
        
        self.log(f"获取视频信息: {url}")
        
        # 在新线程中获取信息
        thread = threading.Thread(target=self._get_video_info_thread, args=(url,))
        thread.start()
    
    def _get_video_info_thread(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiesfrombrowser': ('chrome',),
            }
            
            if self.proxy_input.text().strip():
                ydl_opts['proxy'] = self.proxy_input.text().strip()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 格式化信息
                info_text = f"标题: {info.get('title', 'N/A')}\n"
                info_text += f"上传者: {info.get('uploader', 'N/A')}\n"
                info_text += f"时长: {info.get('duration', 0) // 60}分钟\n"
                info_text += f"视图: {info.get('view_count', 'N/A')}\n"
                
                if info.get('formats'):
                    info_text += "\n可用格式:\n"
                    formats = {}
                    for f in info['formats']:
                        if f.get('height'):
                            height = f['height']
                            fps = f.get('fps', 30)
                            vcodec = f.get('vcodec', 'unknown')
                            if height not in formats or fps > formats[height]['fps']:
                                formats[height] = {'fps': fps, 'codec': vcodec}
                    
                    for height in sorted(formats.keys(), reverse=True):
                        info_text += f"  {height}p @ {formats[height]['fps']}fps ({formats[height]['codec']})\n"
                
                QMetaObject.invokeMethod(self, "show_video_info", 
                                       Qt.QueuedConnection, 
                                       Q_ARG(str, info_text))
                
        except Exception as e:
                            QMetaObject.invokeMethod(self, "show_error", 
                                   Qt.QueuedConnection, 
                                   Q_ARG(str, f"获取信息失败: {str(e)}"))