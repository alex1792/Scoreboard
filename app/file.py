# app/file.py
from flask import Blueprint, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from .utils import check_authorization
from flask_jwt_extended import jwt_required

file_bp = Blueprint('file', __name__, url_prefix='/api/files')

# 允許的檔案類型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """上傳檔案"""
    try:
        authorization = check_authorization('host')
        if authorization:
            return authorization
        
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # 確保上傳目錄存在
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            return jsonify({
                "status": "success",
                "message": "File uploaded successfully",
                "filename": filename,
                "file_path": file_path
            })
        else:
            return jsonify({"status": "error", "message": "File type not allowed"}), 400
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to upload file"}), 500

@file_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    """下載檔案"""
    try:
        authorization = check_authorization('host')
        if authorization:
            return authorization
        
        upload_folder = 'uploads'
        file_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to download file"}), 500

@file_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    """列出所有檔案"""
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization
        
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            return jsonify({"status": "success", "data": []})
        
        files = []
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                file_info = {
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                }
                files.append(file_info)
        
        return jsonify({
            "status": "success",
            "data": files
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to list files"}), 500

@file_bp.route('/<filename>', methods=['DELETE'])
@jwt_required()
def delete_file(filename):
    """刪除檔案"""
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization
        
        upload_folder = 'uploads'
        file_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        os.remove(file_path)
        
        return jsonify({
            "status": "success",
            "message": f"File {filename} deleted successfully"
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to delete file"}), 500
