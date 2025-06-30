@echo off
echo Packaging Video Downloader...

venv\Scripts\activate

pyinstaller --onefile --windowed --name VideoDownloader video_downloader.py

echo Done!
pause