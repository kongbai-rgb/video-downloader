@echo off
chcp 65001 >nul
echo Starting to package Video Downloader...

REM Activate virtual environment
call venv\Scripts\activate

REM Create icon file
echo Creating application icon...
echo import sys > create_icon.py
echo from PIL import Image, ImageDraw, ImageFont >> create_icon.py
echo img = Image.new('RGB', (256, 256), color='#2196F3') >> create_icon.py
echo draw = ImageDraw.Draw(img) >> create_icon.py
echo draw.rectangle([64, 64, 192, 192], fill='white') >> create_icon.py
echo draw.rectangle([80, 80, 176, 120], fill='#2196F3') >> create_icon.py
echo draw.polygon([(128, 120), (100, 150), (156, 150)], fill='#2196F3') >> create_icon.py
echo img.save('icon.ico') >> create_icon.py
python create_icon.py
del create_icon.py

REM Check if video_downloader.py exists
if not exist video_downloader.py (
    echo ERROR: video_downloader.py not found!
    echo Please make sure video_downloader.py is in the current directory.
    pause
    exit /b 1
)

REM Use PyInstaller to package
echo Starting packaging process...
pyinstaller --onefile --windowed --name "VideoDownloader" --icon=icon.ico --add-data "settings.json;." --hidden-import=yt_dlp --hidden-import=instaloader --hidden-import=openpyxl video_downloader.py

echo Packaging complete!
echo Executable file location: dist\VideoDownloader.exe

REM Create release folder
if not exist release mkdir release
if exist "dist\VideoDownloader.exe" (
    copy "dist\VideoDownloader.exe" "release\"
    echo VideoDownloader.exe copied to release folder
) else (
    echo ERROR: VideoDownloader.exe not found in dist folder
)

if exist "操作说明.txt" copy "操作说明.txt" "release\"
if exist "批量下载示例.xlsx" copy "批量下载示例.xlsx" "release\"

echo.
echo Release files are ready in the release folder
pause