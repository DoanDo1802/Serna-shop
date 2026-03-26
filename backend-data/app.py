"""
Backend API cho hệ thống quản lý KOL
Cung cấp các endpoint để:
- Lấy dữ liệu KOL từ Kalodata
- Lấy video TikTok
- Gửi tin nhắn TikTok tự động
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import os
import sys

# Load environment variables
load_dotenv()

# Thêm thư mục gốc vào path để import modules
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# Import các functions (không tự động chạy code)
# Sử dụng Supabase để lưu trữ dữ liệu
from kalodata.data_store import (
    enrich_creators,
    filter_creators_for_store,
    load_saved_payload,
    merge_creators_into_store,
    read_creators_from_excel,
    delete_creators_by_names,
)
from kalodata.exp_playwright_api import export_kalodata_data
from kalodata.upload_sheets import upload_excel_to_gsheet
from agent.agent import suggest_filters as agent_suggest_filters
from tiktok.tiktok import get_tiktok_videos
from tiktok.get_userid import get_tiktok_userid
from tiktok.dmtiktok import send_tiktok_dm_to_user
from products.product_store import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    delete_multiple_products,
)
from kol_management.kol_processor import process_kol_data, rank_kols_by_engagement
from kol_management.sheets_reader import read_kol_data_from_sheets

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái server"""
    return jsonify({"status": "ok", "message": "Backend đang hoạt động"}), 200

@app.route('/api/kalodata/export', methods=['POST'])
def export_kalodata():
    """
    Export dữ liệu KOL từ Kalodata và enrich với follower stats
    Body: {
        "start_date": "2026-02-14",
        "end_date": "2026-03-14",
        "revenue_min": 50000000,
        "revenue_max": 100000000,
        "age_range": "25-34",
        "page_size": 10,
        "enrich": true,  // Có lấy thêm dữ liệu follower không
        "deduplicate": true  // Lọc trùng với dữ liệu đã lưu
    }
    """
    try:
        data = request.json or {}
        crawl_params = {
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'revenue_min': data.get('revenue_min', 50000000),
            'revenue_max': data.get('revenue_max', 100000000),
            'age_range': data.get('age_range', '25-34'),
            'page_size': data.get('page_size', 10),
            'enrich': data.get('enrich', False),
            'deduplicate': data.get('deduplicate', True),
            'filters': data.get('filters', {}),
        }

        # Export dữ liệu
        file_path = export_kalodata_data(
            start_date=crawl_params['start_date'],
            end_date=crawl_params['end_date'],
            revenue_min=crawl_params['revenue_min'],
            revenue_max=crawl_params['revenue_max'],
            age_range=crawl_params['age_range'],
            page_size=crawl_params['page_size'],
            filters=crawl_params['filters'],
        )
        
        creators = read_creators_from_excel(
            file_path,
            start_date=crawl_params['start_date'],
            end_date=crawl_params['end_date'],
        )

        duplicate_count = 0
        if crawl_params['deduplicate']:
            filter_result = filter_creators_for_store(creators)
            creators = filter_result['fresh_records']
            duplicate_count = filter_result['duplicate_count']
            print(f"🛡️ Đã lọc trùng trước enrich: bỏ qua {duplicate_count} KOL, còn {len(creators)} KOL mới.")
        
        # Enrich với follower stats nếu được yêu cầu
        if crawl_params['enrich'] and creators:
            print(f"\n🔍 Đang enrich dữ liệu cho {len(creators)} KOLs...")
            from kalodata.datakoc import get_follower_stats
            creators = enrich_creators(creators, get_follower_stats)

        persist_result = merge_creators_into_store(
            creators,
            deduplicate=False,
            last_crawl={
                'file_path': file_path,
                'ran_at': datetime.utcnow().isoformat() + 'Z',
                'params': crawl_params,
            },
            duplicate_count_override=duplicate_count,
            deduplicate_applied=crawl_params['deduplicate'],
        )
        
        return jsonify({
            "success": True, 
            "file_path": file_path,
            **persist_result,
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kalodata/data', methods=['GET'])
def get_saved_kalodata():
    """Lấy dữ liệu Kalodata đã lưu để hiển thị lại sau khi F5."""
    try:
        payload = load_saved_payload()
        return jsonify({"success": True, **payload}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/kalodata/delete', methods=['POST'])
def delete_kalodata():
    """
    Xóa các KOL theo tên
    Body: {
        "names": ["Tên KOL 1", "Tên KOL 2"]
    }
    """
    try:
        data = request.json or {}
        names = data.get('names', [])
        
        if not names or not isinstance(names, list):
            return jsonify({"success": False, "error": "Danh sách names không hợp lệ"}), 400
        
        result = delete_creators_by_names(names)
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/kalodata/upload', methods=['POST'])
def upload_kalodata():
    """
    Upload file Excel lên Google Sheets
    Body: {
        "excel_path": "kalodata/exports/export_kalodata_20260314_120000.xlsx",
        "google_sheet_url": "https://docs.google.com/spreadsheets/...",
        "sheet_name": "Sheet1"
    }
    """
    try:
        data = request.json
        excel_path = data.get('excel_path')
        sheet_url = data.get('google_sheet_url', os.environ.get('GOOGLE_SHEET_URL'))
        sheet_name = data.get('sheet_name', 'Sheet1')
        
        if not excel_path or not sheet_url:
            return jsonify({"success": False, "error": "Thiếu excel_path hoặc google_sheet_url"}), 400
        
        # Upload lên Google Sheets
        upload_excel_to_gsheet(excel_path, sheet_url, sheet_name)
        
        return jsonify({"success": True, "message": "Đã upload thành công"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tiktok/videos', methods=['POST'])
def get_videos():
    """
    Lấy danh sách video từ TikTok profile
    Body: {
        "profile_url": "https://www.tiktok.com/@username"
    }
    """
    try:
        data = request.json
        profile_url = data.get('profile_url')
        
        if not profile_url:
            return jsonify({"success": False, "error": "Thiếu profile_url"}), 400
        
        videos = get_tiktok_videos(profile_url)
        return jsonify({"success": True, "videos": videos}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tiktok/userid', methods=['POST'])
def get_userid():
    """
    Lấy User ID từ TikTok profile URL
    Body: {
        "profile_url": "https://www.tiktok.com/@username"
    }
    """
    try:
        data = request.json
        profile_url = data.get('profile_url')
        
        if not profile_url:
            return jsonify({"success": False, "error": "Thiếu profile_url"}), 400
        
        user_info = get_tiktok_userid(profile_url)
        return jsonify({"success": True, "user_info": user_info}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tiktok/send-dm', methods=['POST'])
def send_dm():
    """
    Gửi tin nhắn tự động đến TikTok user
    Body: {
        "profile_url": "https://www.tiktok.com/@username",
        "message": "Nội dung tin nhắn"
    }
    """
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

@app.route('/api/tiktok/batch-dm', methods=['POST'])
def batch_send_dm():
    """
    Gửi tin nhắn hàng loạt đến nhiều TikTok users
    Body: {
        "users": [
            {"profile_url": "https://www.tiktok.com/@user1", "message": "Tin nhắn 1"},
            {"profile_url": "https://www.tiktok.com/@user2", "message": "Tin nhắn 2"}
        ]
    }
    """
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

@app.route('/api/agent/suggest', methods=['POST'])
def agent_suggest():
    """
    Agent gợi ý filter Kalodata dựa trên sản phẩm.
    Body: {
        "description": "Mô tả sản phẩm",
        "price": "150000",
        "image": "base64 encoded image (optional)",
        "image_url": "URL ảnh sản phẩm (optional)"
    }
    """
    try:
        data = request.json or {}
        description = data.get('description', '')
        price = data.get('price', '')
        image_base64 = data.get('image')
        image_url = data.get('image_url')

        if not description:
            return jsonify({"success": False, "error": "Vui lòng nhập mô tả sản phẩm"}), 400

        result = agent_suggest_filters(
            description=description,
            price=price,
            image_base64=image_base64,
            image_url=image_url,
        )

        return jsonify({"success": True, **result}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============= PRODUCT APIs =============

@app.route('/api/products', methods=['GET'])
def get_products():
    """Lấy danh sách tất cả sản phẩm"""
    try:
        result = get_all_products()
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Lấy thông tin một sản phẩm"""
    try:
        product = get_product_by_id(product_id)
        if product:
            return jsonify({"success": True, "product": product}), 200
        else:
            return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/products', methods=['POST'])
def add_product():
    """
    Thêm sản phẩm mới
    Body: {
        "name": "Tên sản phẩm",
        "description": "Mô tả",
        "specifications": "Thông số kỹ thuật",
        "price": 150000,
        "status": "in_stock",
        "image": "base64 hoặc URL"
    }
    """
    try:
        data = request.json or {}
        
        if not data.get('name') or not data.get('price'):
            return jsonify({"success": False, "error": "Thiếu tên hoặc giá sản phẩm"}), 400
        
        product = create_product(data)
        return jsonify({"success": True, "product": product}), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/products/<product_id>', methods=['PUT'])
def edit_product(product_id):
    """
    Cập nhật sản phẩm
    Body: {
        "name": "Tên sản phẩm",
        "description": "Mô tả",
        "specifications": "Thông số kỹ thuật",
        "price": 150000,
        "status": "in_stock",
        "image": "base64 hoặc URL"
    }
    """
    try:
        data = request.json or {}
        
        if not data.get('name') or not data.get('price'):
            return jsonify({"success": False, "error": "Thiếu tên hoặc giá sản phẩm"}), 400
        
        product = update_product(product_id, data)
        if product:
            return jsonify({"success": True, "product": product}), 200
        else:
            return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/products/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    """Xóa một sản phẩm"""
    try:
        success = delete_product(product_id)
        if success:
            return jsonify({"success": True, "message": "Đã xóa sản phẩm"}), 200
        else:
            return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/products/batch-delete', methods=['POST'])
def batch_delete_products():
    """
    Xóa nhiều sản phẩm
    Body: {
        "ids": ["id1", "id2", "id3"]
    }
    """
    try:
        data = request.json or {}
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({"success": False, "error": "Danh sách IDs trống"}), 400
        
        result = delete_multiple_products(ids)
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== COOKIE MANAGEMENT APIs ====================

@app.route('/api/cookies/status', methods=['GET'])
def get_cookie_status():
    """
    Kiểm tra trạng thái cookie hiện tại
    """
    try:
        import json
        from datetime import datetime
        
        kalodata_cookie_file = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie.json")
        tiktok_cookie_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
        
        status = {
            "kalodata": {
                "exists": False,
                "valid": False,
                "updated_at": None,
                "source": None,
                "account_name": None
            },
            "tiktok": {
                "exists": False,
                "valid": False,
                "updated_at": None,
                "source": None,
                "account_name": None
            }
        }
        
        # Check Kalodata cookie
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
        
        # Fallback to env
        if not status["kalodata"]["valid"] and os.environ.get("KALODATA_COOKIE"):
            status["kalodata"]["exists"] = True
            status["kalodata"]["valid"] = len(os.environ.get("KALODATA_COOKIE", "")) > 50
            status["kalodata"]["source"] = "env"
        
        # Check TikTok cookie
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
        
        # Fallback to env
        if not status["tiktok"]["valid"] and os.environ.get("TIKTOK_COOKIE"):
            status["tiktok"]["exists"] = True
            status["tiktok"]["valid"] = len(os.environ.get("TIKTOK_COOKIE", "")) > 50
            status["tiktok"]["source"] = "env"
        
        return jsonify({"success": True, "status": status}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/cookies/refresh', methods=['POST'])
def refresh_cookies():
    """
    Refresh cookies - Kiểm tra cookie có tồn tại và lấy tên tài khoản đã lưu
    Body: {
        "platform": "kalodata" | "tiktok" | "all"
    }
    """
    try:
        import json
        from datetime import datetime
        
        data = request.json or {}
        platform = data.get('platform', 'all')
        
        results = {}
        
        if platform in ['kalodata', 'all']:
            try:
                cookie_file = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie")
                json_file = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie.json")
                
                if os.path.exists(cookie_file):
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        cookie_str = f.read().strip()
                    
                    # Simple validation - check if cookie exists and has reasonable length
                    if len(cookie_str) > 100:
                        # Try to get account name from JSON file
                        account_name = None
                        if os.path.exists(json_file):
                            try:
                                with open(json_file, 'r') as f:
                                    json_data = json.load(f)
                                    account_name = json_data.get('account_name')
                            except:
                                pass
                        
                        results["kalodata"] = {
                            "success": True,
                            "message": "Cookie Kalodata có sẵn",
                            "account_name": account_name
                        }
                    else:
                        results["kalodata"] = {
                            "success": False,
                            "error": "Cookie quá ngắn, vui lòng nhập lại"
                        }
                else:
                    results["kalodata"] = {
                        "success": False,
                        "error": "Chưa có cookie, vui lòng nhập cookie mới"
                    }
            except Exception as e:
                results["kalodata"] = {
                    "success": False,
                    "error": f"Lỗi kiểm tra cookie: {str(e)}"
                }
        
        if platform in ['tiktok', 'all']:
            try:
                cookie_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie")
                json_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
                
                if os.path.exists(cookie_file):
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        cookie_str = f.read().strip()
                    
                    # Simple validation - check if cookie exists and has reasonable length
                    if len(cookie_str) > 100:
                        # Try to get account name from JSON file
                        account_name = None
                        if os.path.exists(json_file):
                            try:
                                with open(json_file, 'r') as f:
                                    json_data = json.load(f)
                                    account_name = json_data.get('account_name')
                            except:
                                pass
                        
                        results["tiktok"] = {
                            "success": True,
                            "message": "Cookie TikTok có sẵn",
                            "account_name": account_name
                        }
                    else:
                        results["tiktok"] = {
                            "success": False,
                            "error": "Cookie quá ngắn, vui lòng nhập lại"
                        }
                else:
                    results["tiktok"] = {
                        "success": False,
                        "error": "Chưa có cookie, vui lòng nhập cookie mới"
                    }
            except Exception as e:
                results["tiktok"] = {
                    "success": False,
                    "error": f"Lỗi kiểm tra cookie: {str(e)}"
                }
        
        # Check if any succeeded
        any_success = any(r.get("success", False) for r in results.values())
        
        return jsonify({
            "success": any_success,
            "results": results
        }), 200 if any_success else 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/cookies/manual', methods=['POST'])
def set_cookie_manual():
    """
    Set cookie thủ công
    Body: {
        "platform": "kalodata" | "tiktok",
        "cookie": "cookie_string"
    }
    """
    try:
        import json
        from datetime import datetime
        import requests
        
        data = request.json or {}
        platform = data.get('platform')
        cookie_str = data.get('cookie', '').strip()
        
        if not platform or platform not in ['kalodata', 'tiktok']:
            return jsonify({"success": False, "error": "Platform không hợp lệ"}), 400
        
        if not cookie_str or len(cookie_str) < 50:
            return jsonify({"success": False, "error": "Cookie quá ngắn hoặc không hợp lệ"}), 400
        
        # Parse cookie string to JSON format
        def parse_cookies_to_json(cookie_str, domain):
            cookies = []
            for part in cookie_str.split(";"):
                part = part.strip()
                if not part or "=" not in part:
                    continue
                name, _, value = part.partition("=")
                name, value = name.strip(), value.strip()
                if name:
                    cookies.append({
                        "name": name,
                        "value": value,
                        "domain": domain,
                        "path": "/",
                        "expires": -1
                    })
            return cookies
        
        # Get account name from cookie
        def get_account_name(platform, cookie_str):
            try:
                if platform == 'tiktok':
                    # Try to get TikTok username from API
                    headers = {
                        'Cookie': cookie_str,
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    response = requests.get('https://www.tiktok.com/api/user/detail/', headers=headers, timeout=5)
                    if response.status_code == 200:
                        user_data = response.json()
                        return user_data.get('userInfo', {}).get('user', {}).get('uniqueId')
                elif platform == 'kalodata':
                    # Try to get Kalodata username
                    headers = {
                        'Cookie': cookie_str,
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    response = requests.get('https://www.kalodata.com/api/user/info', headers=headers, timeout=5)
                    if response.status_code == 200:
                        user_data = response.json()
                        return user_data.get('data', {}).get('username') or user_data.get('data', {}).get('email')
            except:
                pass
            return None
        
        # Determine paths and domain
        if platform == "kalodata":
            cookie_file = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie")
            json_file = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie.json")
            env_key = "KALODATA_COOKIE"
            domain = ".kalodata.com"
        else:  # tiktok
            cookie_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie")
            json_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
            env_key = "TIKTOK_COOKIE"
            domain = ".tiktok.com"
        
        # Get account name
        account_name = get_account_name(platform, cookie_str)
        
        # Save text format
        with open(cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookie_str)
        
        # Save JSON format
        cookies = parse_cookies_to_json(cookie_str, domain)
        json_data = {
            "cookies": cookies,
            "updated_at": datetime.now().isoformat(),
            "account_name": account_name
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        # Update .env
        env_file = os.path.join(os.path.dirname(__file__), ".env")
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
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


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


# ==================== KOL MANAGEMENT APIs ====================

@app.route('/api/kol/sync', methods=['POST'])
def sync_kol_data():
    """
    Đồng bộ dữ liệu KOL từ Google Sheets và lấy stats từ TikTok
    Body: {
        "spreadsheet_url": "https://docs.google.com/spreadsheets/...",
        "sheet_name": "KOL_management",
        "fetch_stats": true  // Có lấy stats từ TikTok không
    }
    """
    try:
        data = request.json or {}
        spreadsheet_url = data.get('spreadsheet_url', os.environ.get('KOL_SHEET_URL'))
        sheet_name = data.get('sheet_name', 'KOL_management')
        fetch_stats = data.get('fetch_stats', False)
        
        if not spreadsheet_url:
            return jsonify({"success": False, "error": "Thiếu spreadsheet_url"}), 400
        
        if fetch_stats:
            # Lấy đầy đủ dữ liệu + stats
            kols = process_kol_data(spreadsheet_url, sheet_name)
        else:
            # Chỉ lấy dữ liệu cơ bản từ Sheets
            kols = read_kol_data_from_sheets(spreadsheet_url, sheet_name)
        
        return jsonify({
            "success": True,
            "kols": kols,
            "total": len(kols)
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kol/ranking', methods=['POST'])
def get_kol_ranking():
    """
    Lấy bảng xếp hạng KOL theo engagement
    Body: {
        "spreadsheet_url": "https://docs.google.com/spreadsheets/...",
        "sheet_name": "KOL_management"
    }
    """
    try:
        data = request.json or {}
        spreadsheet_url = data.get('spreadsheet_url', os.environ.get('KOL_SHEET_URL'))
        sheet_name = data.get('sheet_name', 'KOL_management')
        
        if not spreadsheet_url:
            return jsonify({"success": False, "error": "Thiếu spreadsheet_url"}), 400
        
        # Lấy dữ liệu và xếp hạng
        kols = process_kol_data(spreadsheet_url, sheet_name)
        ranked_kols = rank_kols_by_engagement(kols)
        
        return jsonify({
            "success": True,
            "ranking": ranked_kols,
            "total": len(ranked_kols)
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kol/upload-stats', methods=['POST'])
def upload_kol_stats():
    """
    Upload stats thủ công từ CSV
    Body: {
        "csv_data": "video_url,views,likes,comments,shares\\n..."
    }
    """
    try:
        data = request.json or {}
        csv_data = data.get('csv_data', '')
        
        if not csv_data:
            return jsonify({"success": False, "error": "Thiếu csv_data"}), 400
        
        # Parse CSV data
        import csv
        import io
        from kol_management.manual_stats import save_manual_stats
        
        reader = csv.DictReader(io.StringIO(csv_data))
        count = 0
        
        for row in reader:
            video_url = row.get('video_url', '').strip()
            if not video_url:
                continue
            
            stats = {
                'video_url': video_url,
                'views': int(row.get('views', 0)),
                'likes': int(row.get('likes', 0)),
                'comments': int(row.get('comments', 0)),
                'shares': int(row.get('shares', 0)),
                'saves': int(row.get('saves', 0)),
                'engagement_rate': 0.0
            }
            
            # Tính engagement rate: ER = (Like + Comment + Share + Save) / View × 100%
            if stats['views'] > 0:
                total_engagement = stats['likes'] + stats['comments'] + stats['shares'] + stats['saves']
                stats['engagement_rate'] = round((total_engagement / stats['views']) * 100, 2)
            
            save_manual_stats(video_url, stats)
            count += 1
        
        return jsonify({
            "success": True,
            "message": f"Đã import {count} video stats",
            "count": count
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
