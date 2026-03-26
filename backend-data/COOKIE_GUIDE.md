# 🍪 Hướng Dẫn Tự Động Lấy Cookie

## Vấn Đề
Cookie Kalodata và TikTok thường hết hạn sau vài ngày/tuần, phải copy thủ công từ trình duyệt rất mất thời gian.

## Giải Pháp
Dùng script tự động lấy và refresh cookie khi cần.

---

## 🚀 Cách Sử Dụng

### 1. Cài Đặt Dependencies (Nếu Chưa Có)

```bash
cd backend-data
pip install playwright
playwright install chromium
```

### 2. Lấy Cookie Tự Động

#### Cách 1: Update Cả 2 Cookie (Kalodata + TikTok)

```bash
python3 update_cookies.py
```

#### Cách 2: Chỉ Update Kalodata

```bash
python3 update_cookies.py --kalodata
```

#### Cách 3: Chỉ Update TikTok

```bash
python3 update_cookies.py --tiktok
```

#### Cách 4: Force Refresh (Bắt Buộc Lấy Mới)

```bash
python3 update_cookies.py --force
```

### 3. Quy Trình

1. Script sẽ mở trình duyệt tự động
2. Nếu chưa đăng nhập, bạn sẽ thấy thông báo:
   ```
   ⚠️  BẠN CẦN ĐĂNG NHẬP THỦ CÔNG
   1. Trình duyệt đã mở trang login
   2. Vui lòng đăng nhập bằng tài khoản của bạn
   3. Sau khi đăng nhập xong, nhấn ENTER ở terminal
   ```
3. Đăng nhập 1 lần duy nhất
4. Script sẽ tự động:
   - Lưu cookie vào file `.cookie` / `.tiktok_cookie`
   - Update vào file `.env`
   - Lần sau chạy sẽ tự động dùng cookie cũ (không cần login lại)

---

## 📁 File Structure

```
backend-data/
├── .env                          # Cookie được tự động update vào đây
├── update_cookies.py             # Script chính để update cookie
├── kalodata/
│   ├── auto_cookie.py           # Logic lấy cookie Kalodata
│   ├── .cookie                  # Cookie Kalodata (text)
│   └── .cookie.json             # Cookie Kalodata (JSON + metadata)
└── tiktok/
    ├── auto_cookie.py           # Logic lấy cookie TikTok
    ├── .tiktok_cookie           # Cookie TikTok (text)
    └── .tiktok_cookie.json      # Cookie TikTok (JSON + metadata)
```

---

## 🔄 Tự Động Refresh Cookie

### Cách 1: Chạy Thủ Công Khi Cần

```bash
python3 update_cookies.py
```

### Cách 2: Tích Hợp Vào Code

Thêm vào đầu file Python của bạn:

```python
import os
import sys

# Auto refresh cookie nếu hết hạn
try:
    from kalodata.auto_cookie import get_kalodata_cookie
    cookie = get_kalodata_cookie(force_refresh=False)
    os.environ["KALODATA_COOKIE"] = cookie
except Exception as e:
    print(f"⚠️ Không thể refresh cookie: {e}")
```

### Cách 3: Cronjob (Tự Động Hàng Ngày)

Thêm vào crontab:

```bash
# Chạy mỗi ngày lúc 3 giờ sáng
0 3 * * * cd /path/to/backend-data && python3 update_cookies.py --force
```

---

## 🛠️ Troubleshooting

### Lỗi: "Cookie không hợp lệ"
- Chạy lại với `--force`: `python3 update_cookies.py --force`
- Đăng nhập lại thủ công khi script yêu cầu

### Lỗi: "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### Lỗi: "Cloudflare blocking"
- Script sẽ tự động đợi Cloudflare verify
- Nếu vẫn bị chặn, thử lại sau vài phút

### Cookie vẫn hết hạn nhanh
- Một số website có session timeout ngắn
- Chạy `update_cookies.py` trước mỗi lần chạy app:
  ```bash
  python3 update_cookies.py && python3 app.py
  ```

---

## 💡 Tips

1. **Lần đầu chạy**: Bạn phải đăng nhập thủ công 1 lần
2. **Lần sau**: Script tự động dùng cookie cũ, không cần login
3. **Cookie hết hạn**: Script tự động phát hiện và yêu cầu login lại
4. **Headless mode**: Thêm `--headless` để chạy ẩn (chỉ dùng khi đã có cookie)

---

## 🎯 So Sánh

| Cách | Ưu Điểm | Nhược Điểm |
|------|---------|------------|
| **Thủ công** (cũ) | Đơn giản | Mất thời gian, dễ quên |
| **Auto script** (mới) | Tự động, nhanh | Cần setup lần đầu |
| **Cronjob** | Hoàn toàn tự động | Cần config server |

---

## 📞 Support

Nếu gặp vấn đề, check:
1. File `.env` có được update không
2. File `.cookie.json` có tồn tại không
3. Cookie có hợp lệ không (check expiry date)
