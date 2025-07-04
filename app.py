import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QMessageBox, QProgressBar, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
import yt_dlp
import openpyxl
import re

class DownloadThread(QThread):
    progress = pyqtSignal(int, float)  # 行号, 进度百分比
    finished = pyqtSignal(int, str)    # 行号, 完成/错误信息
    error = pyqtSignal(int, str)       # 行号, 错误信息

    def __init__(self, url, folder, row):
        super().__init__()
        self.url = url
        self.folder = folder
        self.row = row
        self.max_retries = 3

    def run(self):
        ydl_opts = {
            'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.hook],
            'proxy': 'http://127.0.0.1:7890',
            'format': 'bestvideo+bestaudio/best',
        }
        for attempt in range(1, self.max_retries + 1):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])
                self.finished.emit(self.row, '完成')
                return
            except Exception as e:
                if attempt == self.max_retries:
                    self.error.emit(self.row, f'失败({e})')
                else:
                    continue

    def hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total * 100
                self.progress.emit(self.row, percent)
        elif d['status'] == 'finished':
            self.progress.emit(self.row, 100)

class VideoDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ins & YouTube 视频下载器')
        self.setGeometry(500, 300, 800, 600)
        self.last_import_dir = ''  # 记录上次导入路径
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 链接输入
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(QLabel('视频链接:'))
        self.url_input = QLineEdit()
        hlayout1.addWidget(self.url_input)
        self.download_btn = QPushButton('下载')
        self.download_btn.clicked.connect(self.start_download)
        hlayout1.addWidget(self.download_btn)
        self.import_btn = QPushButton('导入文件')
        self.import_btn.clicked.connect(self.import_file)
        hlayout1.addWidget(self.import_btn)
        layout.addLayout(hlayout1)

        # 下载列表区域（表格）
        self.list_table = QTableWidget()
        self.list_table.setColumnCount(3)
        self.list_table.setHorizontalHeaderLabels(['下载链接', '下载进度', '是否完成'])
        self.list_table.verticalHeader().setVisible(False)
        self.list_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.list_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.list_table.setShowGrid(True)
        self.list_table.setFixedHeight(self.list_table.verticalHeader().defaultSectionSize() * 10 + 30)  # 10行高度
        self.list_table.horizontalHeader().setStretchLastSection(False)
        self.list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.list_table.setColumnWidth(0, int(self.width() * 0.5))
        self.list_table.setColumnWidth(1, int(self.width() * 0.25))
        self.list_table.setColumnWidth(2, int(self.width() * 0.25))
        def resizeEvent(event):
            self.list_table.setColumnWidth(0, int(self.list_table.width() * 0.5))
            self.list_table.setColumnWidth(1, int(self.list_table.width() * 0.25))
            self.list_table.setColumnWidth(2, int(self.list_table.width() * 0.25))
            QWidget.resizeEvent(self, event)
        self.resizeEvent = resizeEvent
        layout.addWidget(self.list_table)

        # 文件夹选择
        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(QLabel('保存到:'))
        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        hlayout3.addWidget(self.folder_input)
        self.folder_btn = QPushButton('选择文件夹')
        self.folder_btn.clicked.connect(self.choose_folder)
        hlayout3.addWidget(self.folder_btn)
        layout.addLayout(hlayout3)

        self.setLayout(layout)

        self.url_input.textChanged.connect(self.sync_list_area)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择保存文件夹')
        if folder:
            self.folder_input.setText(folder)

    def start_download(self):
        folder = self.folder_input.text().strip()
        if not folder:
            QMessageBox.warning(self, '提示', '请选择保存文件夹！')
            return
        self.download_btn.setEnabled(False)
        links = self.url_input.text().splitlines()
        self.download_threads = []
        for i, url in enumerate(links):
            url = url.strip()
            if not url:
                continue
            self.list_table.setItem(i, 1, QTableWidgetItem('0%'))
            self.list_table.setItem(i, 2, QTableWidgetItem('下载中'))
            thread = DownloadThread(url, folder, i)
            thread.progress.connect(self.update_progress)
            thread.finished.connect(self.update_finished)
            thread.error.connect(self.update_error)
            self.download_threads.append(thread)
            thread.start()

    def update_progress(self, row, percent):
        self.list_table.setItem(row, 1, QTableWidgetItem(f'{percent:.0f}%'))

    def update_finished(self, row, msg):
        self.list_table.setItem(row, 2, QTableWidgetItem(msg))
        self.list_table.setItem(row, 1, QTableWidgetItem('100%'))
        # 检查是否全部完成
        if all(self.list_table.item(i, 2) and self.list_table.item(i, 2).text() in ['完成', '失败'] for i in range(self.list_table.rowCount())):
            self.download_btn.setEnabled(True)

    def update_error(self, row, msg):
        self.list_table.setItem(row, 2, QTableWidgetItem('失败'))
        self.list_table.setItem(row, 1, QTableWidgetItem('0%'))
        # 检查是否全部完成
        if all(self.list_table.item(i, 2) and self.list_table.item(i, 2).text() in ['完成', '失败'] for i in range(self.list_table.rowCount())):
            self.download_btn.setEnabled(True)

    def sync_list_area(self):
        links = self.url_input.text().splitlines()
        self.list_table.setRowCount(len(links))
        for i, link in enumerate(links):
            item_link = QTableWidgetItem(link)
            item_progress = QTableWidgetItem('')
            item_status = QTableWidgetItem('')
            self.list_table.setItem(i, 0, item_link)
            self.list_table.setItem(i, 1, item_progress)
            self.list_table.setItem(i, 2, item_status)
            # 交替颜色
            for col in range(3):
                if i % 2 == 0:
                    self.list_table.setRowHeight(i, 25)
                    self.list_table.item(i, col).setBackground(QColor('#f5f5f5'))
                else:
                    self.list_table.setRowHeight(i, 25)
                    self.list_table.item(i, col).setBackground(QColor('#e0e0e0'))

    def import_file(self):
        import os
        default_dir = self.last_import_dir if self.last_import_dir else os.path.join(os.path.expanduser('~'), 'Desktop')
        file_path, _ = QFileDialog.getOpenFileName(self, '选择包含视频链接的文件', default_dir, 'Text/Excel Files (*.txt *.xlsx);;All Files (*)')
        if file_path:
            self.last_import_dir = os.path.dirname(file_path)
            try:
                links = []
                if file_path.lower().endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        links = [line.strip() for line in f if line.strip()]
                elif file_path.lower().endswith('.xlsx'):
                    wb = openpyxl.load_workbook(file_path, read_only=True)
                    for ws in wb.worksheets:
                        for row in ws.iter_rows(values_only=True):
                            for cell in row:
                                if isinstance(cell, str):
                                    found = re.findall(r'https?://\S+', cell)
                                    links.extend(found)
                if links:
                    self.url_input.setText('\n'.join(links))
                else:
                    QMessageBox.warning(self, '提示', '未在文件中识别到有效链接。')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导入文件失败: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VideoDownloader()
    win.show()
    sys.exit(app.exec_()) 