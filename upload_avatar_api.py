"""
小 J 頭像上傳 API
支持上傳白色頭髮圖片
"""

from flask import Blueprint, request, jsonify, send_from_directory
import os
from pathlib import Path
from werkzeug.utils import secure_filename

avatar_bp = Blueprint('avatar', __name__)

# 允許的文件類型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
UPLOAD_FOLDER = 'static'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """檢查文件擴展名是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@avatar_bp.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    """上傳小 J 頭像"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '沒有文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': '未選擇文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件類型'}), 400
        
        # 確保上傳目錄存在
        upload_dir = Path(UPLOAD_FOLDER)
        upload_dir.mkdir(exist_ok=True)
        
        # 保存為標準名稱
        filename = 'little_j_white_hair.png'
        filepath = upload_dir / filename
        
        # 檢查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '文件太大（最大 5MB）'}), 400
        
        # 保存文件
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'message': '頭像上傳成功',
            'filename': filename,
            'url': f'/static/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/api/avatar/info', methods=['GET'])
def get_avatar_info():
    """獲取頭像信息"""
    try:
        static_dir = Path(UPLOAD_FOLDER)
        possible_names = [
            'little_j_white_hair.png',
            'little_j_white_hair.jpg',
            'little_j_white_hair.svg',
            'little_j_white_hair.gif'
        ]
        
        for name in possible_names:
            path = static_dir / name
            if path.exists():
                file_size = path.stat().st_size
                return jsonify({
                    'exists': True,
                    'filename': name,
                    'size': file_size,
                    'url': f'/static/{name}'
                })
        
        return jsonify({
            'exists': False,
            'message': '未找到頭像文件'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/static/<filename>')
def serve_avatar(filename):
    """提供頭像文件"""
    return send_from_directory(UPLOAD_FOLDER, filename)
