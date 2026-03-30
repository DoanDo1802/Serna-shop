from flask import Blueprint, request, jsonify

from tiktok.tiktok import get_tiktok_videos
from tiktok.get_userid import get_tiktok_userid
from tiktok.dmtiktok import send_tiktok_dm_to_user

tiktok_bp = Blueprint('tiktok_routes', __name__, url_prefix='/api/tiktok')

@tiktok_bp.route('/videos', methods=['POST'])
def get_videos():
    try:
        data = request.json
        profile_url = data.get('profile_url')
        
        if not profile_url:
            return jsonify({"success": False, "error": "Thiếu profile_url"}), 400
        
        videos = get_tiktok_videos(profile_url)
        return jsonify({"success": True, "videos": videos}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tiktok_bp.route('/userid', methods=['POST'])
def get_userid():
    try:
        data = request.json
        profile_url = data.get('profile_url')
        
        if not profile_url:
            return jsonify({"success": False, "error": "Thiếu profile_url"}), 400
        
        user_info = get_tiktok_userid(profile_url)
        return jsonify({"success": True, "user_info": user_info}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tiktok_bp.route('/send-dm', methods=['POST'])
def send_dm():
    try:
        data = request.json
        profile_url = data.get('profile_url')
        message = data.get('message')
        
        if not profile_url or not message:
            return jsonify({"success": False, "error": "Thiếu profile_url hoặc message"}), 400
        
        result = send_tiktok_dm_to_user(profile_url, message)
        return jsonify(result), 200 if result.get('success') else 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tiktok_bp.route('/batch-dm', methods=['POST'])
def batch_send_dm():
    try:
        data = request.json
        users = data.get('users', [])
        
        if not users:
            return jsonify({"success": False, "error": "Danh sách users trống"}), 400
        
        results = []
        for user in users:
            try:
                result = send_tiktok_dm_to_user(user['profile_url'], user['message'])
                results.append({
                    "profile_url": user['profile_url'],
                    "success": result.get('success', False),
                    "message": result.get('message') if result.get('success') else None,
                    "error": result.get('error') if not result.get('success') else None
                })
            except Exception as e:
                results.append({
                    "profile_url": user['profile_url'],
                    "success": False,
                    "error": str(e)
                })
        
        return jsonify({"success": True, "results": results}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
