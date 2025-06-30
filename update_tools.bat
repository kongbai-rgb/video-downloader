@echo off
chcp 65001 >nul
cls
echo =====================================
echo    视频下载器 Pro - 更新工具
echo =====================================
echo.

cd /d "D:\video downloader"

echo [1] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo    请先安装Python 3.8或更高版本
    pause
    exit /b 1
)
echo ✓ Python已安装

echo.
echo [2] 激活虚拟环境...
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    echo ✓ 虚拟环境已激活
) else (
    echo ❌ 虚拟环境不存在，正在创建...
    python -m venv venv
    call venv\Scripts\activate
    echo ✓ 虚拟环境创建成功
)

echo.
echo [3] 更新pip...
python -m pip install --upgrade pip --quiet
echo ✓ pip已更新

echo.
echo [4] 更新yt-dlp到最新版本...
pip install --upgrade yt-dlp
if errorlevel 0 (
    echo ✓ yt-dlp更新成功！
    yt-dlp --version
) else (
    echo ❌ yt-dlp更新失败
)

echo.
echo [5] 更新其他依赖...
pip install --upgrade -r requirements.txt --quiet 2>nul
if not exist requirements.txt (
    echo    创建requirements.txt...
    (
        echo yt-dlp
        echo PyQt5
        echo requests
        echo openpyxl
        echo pyinstaller
        echo pillow
    ) > requirements.txt
    pip install --upgrade -r requirements.txt
)
echo ✓ 依赖更新完成

echo.
echo [6] 检查FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg未安装
    echo.
    echo    正在下载FFmpeg...
    echo    请访问: https://www.gyan.dev/ffmpeg/builds/
    echo    下载"release essentials"版本
    echo    解压到当前目录或添加到系统PATH
    echo.
) else (
    echo ✓ FFmpeg已安装
)

echo.
echo [7] 清理缓存...
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
if exist .cache rmdir /s /q .cache 2>nul
yt-dlp --rm-cache-dir 2>nul
echo ✓ 缓存已清理

echo.
echo [8] 测试yt-dlp...
echo    测试YouTube...
yt-dlp --simulate "https://www.youtube.com/watch?v=dQw4w9WgXcQ" >nul 2>&1
if errorlevel 0 (
    echo ✓ YouTube测试通过
) else (
    echo ❌ YouTube测试失败，可能需要代理
)

echo.
echo =====================================
echo    更新完成！
echo =====================================
echo.
echo 提示：
echo 1. 如果下载失败，检查代理设置
echo 2. 某些视频需要在浏览器登录
echo 3. 定期运行此脚本保持最新
echo.
echo 当前版本信息：
yt-dlp --version
echo.
pause