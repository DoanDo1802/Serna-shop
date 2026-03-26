"""
Export Kalodata bằng Playwright (trình duyệt thật) để tránh Cloudflare chặn.
Cookie đọc từ .cookie hoặc KALODATA_COOKIE.
"""
import base64
import json
import os
import time

from playwright.sync_api import sync_playwright

BASE_URL = "https://www.kalodata.com"
API_BASE = "https://www.kalodata.com/api"

_cookie_file = os.path.join(os.path.dirname(__file__) or ".", ".cookie")
if os.environ.get("KALODATA_COOKIE"):
    COOKIE_STR = os.environ.get("KALODATA_COOKIE", "")
elif os.path.isfile(_cookie_file):
    with open(_cookie_file, "r", encoding="utf-8") as f:
        COOKIE_STR = f.read().split("\n")[0].strip()
else:
    COOKIE_STR = ""


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


# Nếu API báo "Please fill in the data range": DevTools → startTask → tab Payload, copy nguyên Request Payload (JSON) và thay vào đây
# Tự động tính date range 30 ngày gần nhất (giống website)
from datetime import datetime, timedelta
_today = datetime.now()
_end = (_today - timedelta(days=1)).strftime("%Y-%m-%d")
_start = (_today - timedelta(days=30)).strftime("%Y-%m-%d")
print(f"Date range: {_start} → {_end}")

payload = {
    "taskId": "",
    "exportType": "LIST_CREATOR",
    "in": {
        "type": "creator",
        "country": "VN",
        "startDate": _start,
        "endDate": _end,
        "cateIds": [],
        "showCateIds": [],
        "pageNo": 1,
        "pageSize": 10, # <--- BẠN ĐỂ NGUYÊN HOẶC CHỈ ĐIỀN CÁC MỐC TRÒN NHƯ 10, 20, 50, 100
        "sort": [
            {
                "field": "revenue",
                "type": "DESC"
            }
        ],
        "creator.filter.follower_age": "25-34",
        "creator.filter.revenue": "50000000-100000000",
        "i18nData": {
            "filter": [
                {"label": "Thời gian", "value": f"{_start} - {_end}"},
                {"label": "Độ tuổi", "value": "25 - 34"},
                {"label": "Doanh thu(đ)", "value": "50000000 - 100000000"}
            ],
            "sorted": "Doanh thu (Giảm dần)"
        },
        "offset": 1,
        "size": 10 # <--- VÀ SỬA ĐỒNG BỘ SỐ NÀY NỮA LÀ ĐƯỢC
    }
}


if not COOKIE_STR or not COOKIE_STR.strip():
    print("Chưa có Cookie. Tạo file .cookie hoặc set KALODATA_COOKIE.")
    exit(1)
downloaded_excel_path = None

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
    )
    context.add_cookies(parse_cookies(COOKIE_STR))
    context.set_extra_http_headers({
        "country": "VN",
        "currency": "VND",
        "language": "vi-VN",
    })

    # Mở trang trước để "ấm" session và pass Cloudflare
    print("Loading creator page...")
    page = context.new_page()
    page.goto(f"{BASE_URL}/creator", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    # Set localStorage values giống website
    page.evaluate("""() => {
        localStorage.setItem('region', 'VN');
        localStorage.setItem('currency', 'VND');
        localStorage.setItem('language', 'vi-VN');
        localStorage.setItem('shopee_country', 'VN');
    }""")

    # Gọi queryList trước để "prime" session (server lưu query hiện tại)
    query_payload = json.dumps({
        "country": "VN",
        "startDate": _start,
        "endDate": _end,
        "cateIds": [],
        "showCateIds": [],
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
        "creator.filter.follower_age": "18-24",
        "creator.filter.revenue": "25000000-250000000"
    })
    print("Priming session with queryList...")
    ql_result = page.evaluate(
        """async (body) => {
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
            try { return JSON.parse(text); } catch(e) { return { _raw: text.slice(0, 300), status: r.status }; }
        }""",
        query_payload,
    )
    ql_code = ql_result.get("code")
    print(f"queryList response code: {ql_code}")
    if ql_result.get("_raw"):
        print("queryList raw:", ql_result.get("_raw", "")[:200])

    page.wait_for_timeout(1000)

    # Gọi startTask sau khi đã query
    payload_js = json.dumps(payload)
    print("Creating export task...")
    data = page.evaluate(
        """async (payloadStr) => {
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
            try { return JSON.parse(text); } catch (e) { return { _raw: text.slice(0, 500), status: r.status }; }
        }""",
        payload_js,
    )
    if data.get("_raw"):
        print("API trả về không phải JSON (có thể trang chưa load xong hoặc bị chặn):", data.get("_raw", "")[:300])
        browser.close()
        exit(1)
    if data.get("code") not in (0, None, 200) or "data" not in data:
        print("API startTask:", data)
        browser.close()
        exit(1)
    task_id = data["data"].get("taskId")
    if not task_id:
        print("Không có taskId:", data)
        browser.close()
        exit(1)
    print("Task ID:", task_id)

    # Chờ export xong bằng cách gọi lại startTask với taskId đã có
    max_wait = 300 # Tăng thời gian chờ lên 5 phút
    start = time.time()
    
    # Payload để poll status giống hệt lúc tạo, chỉ đổi taskId
    poll_payload = payload.copy()
    poll_payload["taskId"] = task_id
    
    is_success = False
    
    print(f"\n⏳ Hệ thống đang đợi Kalodata tạo file Excel (Tối đa {max_wait} giây)...")
    while time.time() - start < max_wait:
        status_res = page.evaluate(
            """async (req_data) => {
                try {
                    const r = await fetch('/export/startTask', {
                        method: 'POST',
                        headers: {
                            'accept': 'application/json, text/plain, */*',
                            'content-type': 'application/json',
                            'country': 'VN',
                            'currency': 'VND',
                            'language': 'vi-VN'
                        },
                        body: JSON.stringify(req_data)
                    });
                    const text = await r.text();
                    try {
                        return JSON.parse(text);
                    } catch(e) {
                        return { _raw: text.slice(0, 200), status: r.status };
                    }
                } catch(err) {
                    return { _error: err.message };
                }
            }""",
            poll_payload,
        )
        s = status_res.get("data") or {}
        code = s.get("code")
        
        print(f"Poll code: {code} | Trạng thái: {s.get('statusMessage', 'Đang xử lý...')}")
        
        # Code 2 = Xong
        if code == 2:
             is_success = True
             break
        # Code 3 = Có thể là lỗi hoặc đang xếp hàng, cứ tiếp tục chờ thay vì tắt ngang
        elif code == 3:
             print(f"⚠️ Kalodata báo mã 3 (Có thể đang quá tải / chờ lâu). Gắng đợi thêm...")
             
        time.sleep(5) # Tăng nhịp chờ lên 5s để đỡ bị spam request

    if not is_success:
        print("Timeout hoặc Lỗi khi chờ export từ Kalodata.")
        browser.close()
        exit(1)

    print("\nExport task completed! Downloading file...")
    
    download_res = page.evaluate(
        """async (tid) => {
            try {
                const r = await fetch('/export/downloadFile', {
                    method: 'POST',
                    headers: {
                        'accept': 'application/json, text/plain, */*',
                        'content-type': 'application/json',
                        'country': 'VN',
                        'currency': 'VND',
                        'language': 'vi-VN'
                    },
                    body: JSON.stringify({ taskId: tid })
                });
                
                // Trả về base64 để Python có thể ghi ra file dễ dàng
                const buffer = await r.arrayBuffer();
                const bytes = new Uint8Array(buffer);
                let binary = '';
                for (let i = 0; i < bytes.byteLength; i++) {
                    binary += String.fromCharCode(bytes[i]);
                }
                return { status: r.status, base64: btoa(binary) };
            } catch(err) {
                return { _error: err.message };
            }
        }""",
        task_id
    )

    if "_error" in download_res:
         print("Lỗi khi tải file:", download_res["_error"])
    elif download_res.get("status") == 200 and download_res.get("base64"):
         import base64
         import datetime
         
         file_data = base64.b64decode(download_res["base64"])
         
         # Khởi tạo thư mục chứa file xuất
         export_dir = os.path.join(os.path.dirname(__file__) or ".", "exports")
         os.makedirs(export_dir, exist_ok=True)
         
         # Đặt tên file theo thời gian để không bao giờ bị trùng
         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
         excel_filename = f"export_kalodata_{timestamp}.xlsx"
         excel_abs_path = os.path.join(export_dir, excel_filename)
         
         with open(excel_abs_path, "wb") as f:
             f.write(file_data)
         print(f"Đã lưu thành công {len(file_data)} bytes vào thư mục exports/: {excel_filename}")
         downloaded_excel_path = excel_abs_path
             
    else:
         print("Tải file thất bại:", download_res)

    browser.close()

if downloaded_excel_path:
    # ----- TIẾN HÀNH XỬ LÝ VÀ ĐẨY LÊN GOOGLE SHEETS -----
    print("\n🚀 Đang chuyển giao file Excel sang hệ thống phân tích Follower chuyên sâu ...")
    try:
        import sys
        sys.path.append(os.path.dirname(__file__))
        from process_all import process_exported_file
        
        process_exported_file(downloaded_excel_path)
    except Exception as e:
        import traceback
        print(f"❌ Lỗi khi gọi hệ thống xử lý trung gian process_all: {e}")
        traceback.print_exc()
