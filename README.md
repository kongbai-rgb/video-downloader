# 视频下载器 Pro / Video Downloader Pro

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PyQt5-5.15+-green.svg" alt="PyQt5">
  <img src="https://img.shields.io/badge/yt--dlp-latest-red.svg" alt="yt-dlp">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

一个基于 yt-dlp 的强大视频下载工具，支持 YouTube、Instagram、Twitter、TikTok 等 1000+ 网站的视频下载。

## ✨ 功能特性

- 🌐 **广泛支持** - 支持 1000+ 视频网站
- 📱 **简单易用** - 直观的图形界面，支持拖放操作
- 🎯 **智能下载** - 自动选择最佳画质，支持 4K/60fps
- 📋 **批量处理** - Excel 导入批量下载，播放列表支持
- 🍪 **自动登录** - 智能使用浏览器 Cookies
- 🌍 **代理支持** - 轻松绕过地区限制
- 📝 **字幕下载** - 自动下载多语言字幕
- 🔄 **实时更新** - 一键更新核心组件

## 📸 界面预览

![主界面](screenshots/main.png)

## 🚀 快速开始

### 系统要求

- Windows 10/11 (64位)
- Python 3.8 或更高版本
- FFmpeg（可选，用于视频转换）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/kongbai-rgb/video-downloader.git
cd video-downloader
```

2. **创建虚拟环境**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行程序**
```bash
python video_downloader.py
```

### 使用预编译版本

如果你不想安装 Python，可以直接下载编译好的 exe 文件：

[📥 下载最新版本](https://github.com/kongbai-rgb/video-downloader/releases)

## 📖 使用说明

### 基本使用

1. 输入或粘贴视频链接
2. 选择下载设置（分辨率、格式等）
3. 点击"开始下载"

### 高级功能

- **批量下载**：创建 Excel 文件，每行一个链接，使用"从Excel导入"功能
- **播放列表**：直接粘贴播放列表链接，程序会自动识别并下载
- **代理设置**：在设置中配置 HTTP 代理（如 `http://127.0.0.1:9090`）

### 支持的网站

- YouTube（视频、播放列表、直播）
- Instagram（视频、Reels、Stories）
- Twitter/X
- TikTok
- Facebook
- Bilibili
- 以及 [1000+ 其他网站](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## 🛠️ 开发指南

### 项目结构

```
video-downloader/
├── video_downloader.py    # 主程序
├── requirements.txt       # Python依赖
├── update_tools.bat      # 更新脚本
├── build.bat            # 打包脚本
├── README.md            # 项目说明
├── LICENSE              # 许可证
└── docs/                # 文档目录
    └── 操作说明.txt      # 详细使用说明
```

### 打包发布

```bash
# Windows打包
pyinstaller --onefile --windowed --name "视频下载器Pro" --icon=icon.ico video_downloader.py

# 或使用打包脚本
build.bat
```

### 贡献代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 🔧 故障排除

### 常见问题

**Q: 下载失败提示"Failed to extract"**
- A: 运行 `update_tools.bat` 更新 yt-dlp

**Q: Instagram 无法下载**
- A: 在 Chrome 中登录 Instagram，程序会自动使用 Cookies

**Q: 下载速度很慢**
- A: 检查代理设置，或选择较低的分辨率

**Q: 找不到 FFmpeg**
- A: 下载 [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) 并添加到 PATH

## 📊 技术栈

- **核心下载器**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **GUI框架**: PyQt5
- **视频处理**: FFmpeg
- **数据处理**: pandas, openpyxl

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载核心
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 跨平台 GUI 框架
- [FFmpeg](https://ffmpeg.org/) - 视频处理工具

## 📞 联系方式

- 提交 [Issue](https://github.com/kongbai-rgb/video-downloader/issues) 报告问题
- 查看 [Wiki](https://github.com/kongbai-rgb/video-downloader/wiki) 获取更多信息

---

<p align="center">
  如果这个项目对你有帮助，请给个 ⭐ Star！
</p>