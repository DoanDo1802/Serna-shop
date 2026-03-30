from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime
import traceback
import requests

cookie_bp = Blueprint('cookie_routes', __name__, url_prefix='/api/cookies')

def update_env_file(env_file, key, value):
    """Helper function to update .env file"""
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write(f"{key}={value}\n")
        return
    
    with open(env_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"\n{key}={value}\n")
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)


@cookie_bp.route('/status', methods=['GET'])
def get_cookie_status():
    try:
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        kalodata_cookie_file = os.path.join(parent_dir, "kalodata", ".cookie.json")
        tiktok_cookie_file = os.path.join(parent_dir, "tiktok", ".tiktok_cookie.json")
        
        status = {
            "kalodata": { "exists": False, "valid": False, "updated_at": None, "source": None, "account_name": None },
            "tiktok": { "exists": False, "valid": False, "updated_at": None, "source": None, "account_name": None }
        }
        
        if os.path.exists(kalodata_cookie_file):
            try:
                with open(kalodata_cookie_file, 'r') as f:
                    data = json.load(f)
                    status["kalodata"]["exists"] = True
                    status["kalodata"]["updated_at"] = data.get("updated_at")
                    status["kalodata"]["valid"] = len(data.get("cookies", [])) > 0
                    status["kalodata"]["source"] = "auto"
                    status["kalodata"]["account_name"] = data.get("account_name")
            except:
                pass
        
        if not status["kalodata"]["valid"] and os.environ.get("KALODATA_COOKIE"):
            status["kalodata"]["exists"] = True
            status["kalodata"]["valid"] = len(os.environ.get("KALODATA_COOKIE", "")) > 50
            status["kalodata"]["source"] = "env"
        
        if os.path.exists(tiktok_cookie_file):
            try:
                with open(tiktok_cookie_file, 'r') as f:
                    data = json.load(f)
                    status["tiktok"]["exists"] = True
                    status["tiktok"]["updated_at"] = data.get("updated_at")
                    status["tiktok"]["valid"] = len(data.get("cookies", [])) > 0
                    status["tiktok"]["source"] = "auto"
                    status["tiktok"]["account_name"] = data.get("account_name")
            except:
                pass
        
        if not status["tiktok"]["valid"] and os.environ.get("TIKTOK_COOKIE"):
            status["tiktok"]["exists"] = True
            status["tiktok"]["valid"] = len(os.environ.get("TIKTOK_COOKIE", "")) > 50
            status["tiktok"]["source"] = "env"
        
        return jsonify({"success": True, "status": status}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cookie_bp.route('/refresh', methods=['POST'])
def refresh_cookies():
    try:
        data = request.json or {}
        platform = data.get('platform', 'all')
        results = {}
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        
        if platform in ['kalodata', 'all']:
            try:
                cookie_file = os.path.join(parent_dir, "kalodata", ".cookie")
                json_file = os.path.join(parent_dir, "kalodata", ".cookie.json")
                if os.path.exists(cookie_file):
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        cookie_str = f.read().strip()
                    if len(cookie_str) > 100:
                        account_name = None
                        if os.path.exists(json_file):
                            try:
                                with open(json_file, 'r') as f:
                                    json_data = json.load(f)
                                    account_name = json_data.get('account_name')
                            except: pass
                        results["kalodata"] = { "success": True, "message": "Cookie Kalodata có sẵn", "account_name": account_name }
                    else:
                        results["kalodata"] = { "success": False, "error": "Cookie quá ngắn, vui lòng nhập lại" }
                else:
                    results["kalodata"] = { "success": False, "error": "Chưa có cookie, vui lòng nhập cookie mới" }
            except Exception as e:
                results["kalodata"] = { "success": False, "error": f"Lỗi kiểm tra cookie: {str(e)}" }
        
        if platform in ['tiktok', 'all']:
            try:
                cookie_file = os.path.join(parent_dir, "tiktok", ".tiktok_cookie")
                json_file = os.path.join(parent_dir, "tiktok", ".tiktok_cookie.json")
                if os.path.exists(cookie_file):
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        cookie_str = f.read().strip()
                    if len(cookie_str) > 100:
                        account_name = None
                        if os.path.exists(json_file):
                            try:
                                with open(json_file, 'r') as f:
                                    json_data = json.load(f)
                                    account_name = json_data.get('account_name')
                            except: pass
                        results["tiktok"] = { "success": True, "message": "Cookie TikTok có sẵn", "account_name": account_name }
                    else:
                        results["tiktok"] = { "success": False, "error": "Cookie quá ngắn, vui lòng nhập lại" }
                else:
                    results["tiktok"] = { "success": False, "error": "Chưa có cookie, vui lòng nhập cookie mới" }
            except Exception as e:
                results["tiktok"] = { "success": False, "error": f"Lỗi kiểm tra cookie: {str(e)}" }
        
        any_success = any(r.get("success", False) for r in results.values())
        return jsonify({ "success": any_success, "results": results }), 200 if any_success else 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@cookie_bp.route('/manual', methods=['POST'])
def set_cookie_manual():
    try:
        data = request.json or {}
        platform = data.get('platform')
        cookie_str = data.get('cookie', '').strip()
        
        if not platform or platform not in ['kalodata', 'tiktok']:
            return jsonify({"success": False, "error": "Platform không hợp lệ"}), 400
        if not cookie_str or len(cookie_str) < 50:
            return jsonify({"success": False, "error": "Cookie quá ngắn hoặc không hợp lệ"}), 400
        
        def parse_cookies_to_json(cookie_str, domain):
            cookies = []
            for part in cookie_str.split(";"):
                part = part.strip()
                if not part or "=" not in part: continue
                name, _, value = part.partition("=")
                name, value = name.strip(), value.strip()
                if name:
                    cookies.append({ "name": name, "value": value, "domain": domain, "path": "/", "expires": -1 })
            return cookies
        
        def get_account_name(platform, cookie_str):
            try:
                if platform == 'tiktok':
                    headers = { 'Cookie': cookie_str, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' }
                    response = requests.get('https://www.tiktok.com/api/user/detail/', headers=headers, timeout=5)
                    if response.status_code == 200:
                        return response.json().get('userInfo', {}).get('user', {}).get('uniqueId')
                elif platform == 'kalodata':
                    headers = { 'Cookie': cookie_str, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' }
                    response = requests.get('https://www.kalodata.com/api/user/info', headers=headers, timeout=5)
                    if response.status_code == 200:
                        user_data = response.json()
                        return user_data.get('data', {}).get('username') or user_data.get('data', {}).get('email')
            except: pass
            return None
        
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        if platform == "kalodata":
            cookie_file = os.path.join(parent_dir, "kalodata", ".cookie")
            json_file = os.path.join(parent_dir, "kalodata", ".cookie.json")
            env_key = "KALODATA_COOKIE"
            domain = ".kalodata.com"
        else:
            cookie_file = os.path.join(parent_dir, "tiktok", ".tiktok_cookie")
            json_file = os.path.join(parent_dir, "tiktok", ".tiktok_cookie.json")
            env_key = "TIKTOK_COOKIE"
            domain = ".tiktok.com"
        
        account_name = get_account_name(platform, cookie_str)
        
        with open(cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookie_str)
        
        cookies = parse_cookies_to_json(cookie_str, domain)
        json_data = { "cookies": cookies, "updated_at": datetime.now().isoformat(), "account_name": account_name }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        env_file = os.path.join(parent_dir, ".env")
        update_env_file(env_file, env_key, cookie_str)
        os.environ[env_key] = cookie_str
        
        response_data = {
            "success": True,
            "message": f"Cookie {platform} đã được lưu thành công",
            "cookie_count": len(cookies)
        }
        if account_name:
            response_data["account_name"] = account_name
            response_data["message"] = f"Cookie {platform} đã được lưu thành công (Tài khoản: {account_name})"
        
        return jsonify(response_data), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
