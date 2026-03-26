"""
Export Kalodata API - Version dành cho Flask API
Chỉ export functions, không tự động chạy code
"""
import base64
import json
import os
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.kalodata.com"
API_BASE = "https://www.kalodata.com/api"

def parse_cookies(s: str, domain=".kalodata.com", path="/"):
    """Chuyển chuỗi Cookie thành list dict cho context.add_cookies."""
    out = []
    for part in s.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, _, value = part.partition("=")
        name, value = name.strip(), value.strip()
        if name:
            out.append({"name": name, "value": value, "domain": domain, "path": path})
    return out

def export_kalodata_data(start_date=None, end_date=None, revenue_min=50000000,
                         revenue_max=100000000, age_range="25-34", page_size=10,
                         filters=None):
    """
    Export dữ liệu KOL từ Kalodata

    Args:
        start_date: Ngày bắt đầu (YYYY-MM-DD), mặc định 30 ngày trước
        end_date: Ngày kết thúc (YYYY-MM-DD), mặc định hôm qua
        revenue_min: Doanh thu tối thiểu
        revenue_max: Doanh thu tối đa
        age_range: Độ tuổi (vd: "25-34")
        page_size: Số lượng KOL cần export
        filters: Dict các filter nâng cao từ Kalodata (vd: cateIds, creator.filter.followers, ...)

    Returns:
        Đường dẫn file Excel đã export
    """
    if filters is None:
        filters = {}
    # Đọc cookie
    _cookie_file = os.path.join(os.path.dirname(__file__) or ".", ".cookie")
    COOKIE_STR = ""
    
    if os.environ.get("KALODATA_COOKIE"):
        COOKIE_STR = os.environ.get("KALODATA_COOKIE", "")
        print("✅ Đã load cookie từ environment variable")
    elif os.path.isfile(_cookie_file):
        with open(_cookie_file, "r", encoding="utf-8") as f:
            COOKIE_STR = f.read().split("\n")[0].strip()
        print("✅ Đã load cookie từ file .cookie")
    else:
        raise Exception(
            "❌ Không tìm thấy KALODATA_COOKIE!\n"
            "Vui lòng:\n"
            "1. Tạo file .cookie trong thư mục kalodata/, hoặc\n"
            "2. Set biến môi trường KALODATA_COOKIE trong file .env"
        )
    
    if not COOKIE_STR or len(COOKIE_STR) < 50:
        raise Exception(
            "❌ Cookie không hợp lệ (quá ngắn)!\n"
            "Cookie phải có dạng: name1=value1; name2=value2; ..."
        )
    
    # Tính date range nếu không có
    if not start_date or not end_date:
        _today = datetime.now()
        end_date = (_today - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (_today - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Date range: {start_date} → {end_date}")
    
    # Build payload cơ bản
    payload_in = {
        "type": "creator",
        "country": "VN",
        "startDate": start_date,
        "endDate": end_date,
        "cateIds": filters.get("cateIds", []),
        "showCateIds": [],
        "pageNo": 1,
        "pageSize": page_size,
        "sort": [{"field": "revenue", "type": "DESC"}],
        "creator.filter.follower_age": age_range,
        "creator.filter.revenue": f"{revenue_min}-{revenue_max}",
        "i18nData": {
            "filter": [
                {"label": "Thời gian", "value": f"{start_date} - {end_date}"},
                {"label": "Độ tuổi", "value": age_range.replace("-", " - ")},
                {"label": "Doanh thu(đ)", "value": f"{revenue_min} - {revenue_max}"}
            ],
            "sorted": "Doanh thu (Giảm dần)"
        },
        "offset": 1,
        "size": page_size,
    }

    # Merge các filter nâng cao (bỏ qua cateIds vì đã xử lý ở trên)
    for key, value in filters.items():
        if key == "cateIds":
            continue
        if value:  # chỉ thêm filter có giá trị
            payload_in[key] = value

    if filters:
        applied = {k: v for k, v in filters.items() if v}
        print(f"🔧 Filters nâng cao: {applied}")

    payload = {
        "taskId": "",
        "exportType": "LIST_CREATOR",
        "in": payload_in,
    }
    
    downloaded_excel_path = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Tắt headless để bypass Cloudflare dễ hơn
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
        )
        
        # Thêm cookies
        context.add_cookies(parse_cookies(COOKIE_STR))
        context.set_extra_http_headers({
            "country": "VN",
            "currency": "VND",
            "language": "vi-VN",
            "accept": "application/json, text/plain, */*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        })

        page = context.new_page()
        
        # Stealth mode - ẩn dấu hiệu automation
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
        """)
        
        print("🌐 Đang mở trang Kalodata và bypass Cloudflare...")
        page.goto(f"{BASE_URL}/creator", wait_until="domcontentloaded", timeout=60000)
        
        # Đợi Cloudflare challenge xong
        print("⏳ Đang đợi Cloudflare verify (có thể mất 10-20s)...")
        try:
            # Đợi cho đến khi không còn thấy Cloudflare challenge
            page.wait_for_function(
                """() => {
                    return !document.body.innerText.includes('Just a moment') &&
                           !document.body.innerText.includes('Checking your browser');
                }""",
                timeout=30000
            )
            print("✅ Đã bypass Cloudflare!")
        except:
            print("⚠️ Timeout đợi Cloudflare, thử tiếp...")
        
        # Đợi thêm để chắc chắn page đã load xong
        page.wait_for_timeout(5000)

        # Set localStorage
        page.evaluate("""() => {
            localStorage.setItem('region', 'VN');
            localStorage.setItem('currency', 'VND');
            localStorage.setItem('language', 'vi-VN');
        }""")
        
        # Kiểm tra xem đã vào được trang creator chưa
        current_url = page.url
        print(f"📍 Current URL: {current_url}")
        
        if "login" in current_url.lower():
            browser.close()
            raise Exception(
                "❌ Cookie đã hết hạn! Trang redirect về login.\n"
                "Vui lòng chạy: python3 test_cookie.py để lấy cookie mới"
            )
        
        # Đợi page load xong hoàn toàn
        try:
            page.wait_for_selector("text=Nhà sáng tạo", timeout=10000)
            print("✅ Đã vào trang creator thành công!")
        except:
            print("⚠️ Không tìm thấy text 'Nhà sáng tạo', nhưng tiếp tục thử...")

        # Query list để warm up session (dùng chung payload_in)
        query_obj = {k: v for k, v in payload_in.items() if k not in ("i18nData", "offset", "size", "showCateIds")}
        query_payload = json.dumps(query_obj)
        
        print("📊 Đang query danh sách...")
        ql_result = page.evaluate(
            """async (body) => {
                try {
                    const r = await fetch('/creator/queryList', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'accept': 'application/json, text/plain, */*',
                            'country': 'VN',
                            'currency': 'VND',
                            'language': 'vi-VN'
                        },
                        body: body
                    });
                    const text = await r.text();
                    
                    // Kiểm tra xem có phải HTML không
                    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                        return { 
                            success: false, 
                            error: 'Got HTML instead of JSON (Cloudflare or login page)', 
                            raw: text.slice(0, 200) 
                        };
                    }
                    
                    try {
                        return { success: true, data: JSON.parse(text) };
                    } catch(e) {
                        return { success: false, error: 'Not JSON', raw: text.slice(0, 200) };
                    }
                } catch(err) {
                    return { success: false, error: err.message };
                }
            }""",
            query_payload,
        )
        
        if not ql_result.get('success'):
            # Chụp screenshot để debug
            page.screenshot(path="kalodata_error_query.png")
            print("📸 Đã chụp screenshot lỗi: kalodata_error_query.png")
            
            browser.close()
            error_msg = f"Query list failed: {ql_result.get('error', 'Unknown')}"
            if 'raw' in ql_result:
                error_msg += f"\nResponse: {ql_result['raw']}"
            error_msg += "\n\n💡 Có thể do:"
            error_msg += "\n1. Cookie đã hết hạn - Chạy: python3 test_cookie.py"
            error_msg += "\n2. Cloudflare đang chặn - Thử lại sau vài phút"
            error_msg += "\n3. Kalodata đổi API - Cần cập nhật code"
            raise Exception(error_msg)
        
        page.wait_for_timeout(2000)

        # Start export task
        print("📤 Đang tạo export task...")
        payload_js = json.dumps(payload)
        data = page.evaluate(
            """async (payloadStr) => {
                try {
                    const r = await fetch('/export/startTask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'accept': 'application/json, text/plain, */*',
                            'country': 'VN',
                            'currency': 'VND',
                            'language': 'vi-VN'
                        },
                        body: payloadStr
                    });
                    const text = await r.text();
                    try {
                        return { success: true, data: JSON.parse(text) };
                    } catch(e) {
                        return { success: false, error: 'Not JSON', raw: text.slice(0, 200) };
                    }
                } catch(err) {
                    return { success: false, error: err.message };
                }
            }""",
            payload_js,
        )
        
        if not data.get('success'):
            browser.close()
            error_msg = f"Start task failed: {data.get('error', 'Unknown')}"
            if 'raw' in data:
                error_msg += f"\nResponse: {data['raw']}"
            raise Exception(error_msg)
        
        data = data['data']
        
        task_id = data.get("data", {}).get("taskId")
        if not task_id:
            browser.close()
            raise Exception(f"Không lấy được taskId: {data}")
        
        print(f"Task ID: {task_id}")

        # Poll status
        poll_payload = payload.copy()
        poll_payload["taskId"] = task_id
        
        max_wait = 300
        start = time.time()
        is_success = False
        
        print(f"⏳ Đang đợi Kalodata xử lý (tối đa {max_wait}s)...")
        while time.time() - start < max_wait:
            status_res = page.evaluate(
                """async (req_data) => {
                    try {
                        const r = await fetch('/export/startTask', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'accept': 'application/json, text/plain, */*',
                                'country': 'VN',
                                'currency': 'VND',
                                'language': 'vi-VN'
                            },
                            body: JSON.stringify(req_data)
                        });
                        const text = await r.text();
                        try {
                            return { success: true, data: JSON.parse(text) };
                        } catch(e) {
                            return { success: false, error: 'Not JSON' };
                        }
                    } catch(err) {
                        return { success: false, error: err.message };
                    }
                }""",
                poll_payload,
            )
            
            if not status_res.get('success'):
                print(f"⚠️ Poll error: {status_res.get('error')}")
                time.sleep(5)
                continue
            
            code = status_res.get("data", {}).get("data", {}).get("code")
            status_msg = status_res.get("data", {}).get("data", {}).get("statusMessage", "")
            
            print(f"📊 Status code: {code} - {status_msg}")
            
            if code == 2:
                is_success = True
                break
            elif code == 3:
                print("⚠️ Task đang xếp hàng hoặc lỗi, tiếp tục đợi...")
            
            time.sleep(5)

        if not is_success:
            browser.close()
            raise Exception("Timeout khi chờ export")

        # Download file
        print("📥 Đang tải file...")
        download_res = page.evaluate(
            """async (tid) => {
                try {
                    const r = await fetch('/export/downloadFile', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'accept': 'application/json, text/plain, */*',
                            'country': 'VN',
                            'currency': 'VND',
                            'language': 'vi-VN'
                        },
                        body: JSON.stringify({ taskId: tid })
                    });
                    const buffer = await r.arrayBuffer();
                    const bytes = new Uint8Array(buffer);
                    let binary = '';
                    for (let i = 0; i < bytes.byteLength; i++) {
                        binary += String.fromCharCode(bytes[i]);
                    }
                    return { success: true, status: r.status, base64: btoa(binary) };
                } catch(err) {
                    return { success: false, error: err.message };
                }
            }""",
            task_id
        )
        
        if not download_res.get('success'):
            browser.close()
            raise Exception(f"Download failed: {download_res.get('error')}")

        if download_res.get("status") == 200 and download_res.get("base64"):
            file_data = base64.b64decode(download_res["base64"])
            
            export_dir = os.path.join(os.path.dirname(__file__) or ".", "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"export_kalodata_{timestamp}.xlsx"
            excel_abs_path = os.path.join(export_dir, excel_filename)
            
            with open(excel_abs_path, "wb") as f:
                f.write(file_data)
            
            print(f"✅ Đã lưu file: {excel_filename}")
            downloaded_excel_path = excel_abs_path
        else:
            raise Exception("Không tải được file")

        browser.close()
    
    return downloaded_excel_path
