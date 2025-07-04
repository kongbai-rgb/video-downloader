from flask import Flask, request, jsonify, render_template, send_file
import os
import yt_dlp
import tempfile
import base64

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def download_video(url):
    # 使用yt-dlp下载视频到临时文件夹，优先高清mp4，支持代理，自动降级格式
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'proxy': 'http://127.0.0.1:7890',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # 自动查找实际下载的文件（兼容不同格式）
        if not os.path.exists(filename):
            base = os.path.splitext(filename)[0]
            for ext in ['.mp4', '.mkv', '.webm', '.flv', '.avi']:
                alt = base + ext
                if os.path.exists(alt):
                    filename = alt
                    break
        print(f"[DEBUG] yt-dlp 下载文件路径: {filename}")
        return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json(force=True)
    url = data.get('url')
    try:
        filepath = download_video(url)
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1024 * 10:
            # 文件不存在或过小，视为下载失败
            return jsonify({'success': False, 'msg': '下载失败，可能是视频受限或格式不支持，请更换链接再试。'}), 400
        filename = os.path.basename(filepath)
        # 用base64编码完整路径
        b64path = base64.urlsafe_b64encode(filepath.encode('utf-8')).decode('ascii')
        return jsonify({'success': True, 'msg': f'下载已完成，请在浏览器下载栏或本地下载文件夹查找：{filename}', 'download_url': f'/file_by_path/{b64path}'})
    except Exception as e:
        return jsonify({'success': False, 'msg': f'下载失败：{str(e)}'}), 500

@app.route('/file_by_path/<b64path>')
def file_by_path(b64path):
    try:
        filepath = base64.urlsafe_b64decode(b64path.encode('ascii')).decode('utf-8')
        if os.path.exists(filepath):
            filename = os.path.basename(filepath)
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return '文件未找到', 404
    except Exception as e:
        return f'路径解析失败: {e}', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 