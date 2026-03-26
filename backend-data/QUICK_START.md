# 🚀 Quick Start - Auto Cookie

## TL;DR

```bash
# Setup lần đầu (chỉ 1 lần)
bash setup_cookies.sh

# Hoặc thủ công:
python3 update_cookies.py

# Chạy app
python3 app.py
```

## Chi tiết

### 1. Lần đầu tiên

```bash
cd backend-data
bash setup_cookies.sh
```

Script sẽ:
- ✅ Cài đặt Playwright (nếu chưa có)
- ✅ Mở trình duyệt để bạn đăng nhập
- ✅ Tự động lưu cookie vào `.env`

### 2. Khi cookie hết hạn

```bash
python3 update_cookies.py
```

### 3. Chỉ update 1 loại cookie

```bash
# Chỉ Kalodata
python3 update_cookies.py --kalodata

# Chỉ TikTok
python3 update_cookies.py --tiktok
```

### 4. Force refresh

```bash
python3 update_cookies.py --force
```

## Quy trình

1. **Lần đầu**: Đăng nhập thủ công 1 lần
2. **Lần sau**: Script tự động dùng cookie cũ
3. **Hết hạn**: Script tự động phát hiện và yêu cầu login lại

## Files

- `update_cookies.py` - Script chính
- `kalodata/auto_cookie.py` - Logic Kalodata
- `tiktok/auto_cookie.py` - Logic TikTok
- `.env` - Cookie được lưu ở đây
- `COOKIE_GUIDE.md` - Hướng dẫn chi tiết

## Troubleshooting

**Lỗi: "Playwright not installed"**
```bash
pip install playwright
playwright install chromium
```

**Lỗi: "Cookie không hợp lệ"**
```bash
python3 update_cookies.py --force
```

**Cookie vẫn hết hạn nhanh**
```bash
# Chạy trước mỗi lần start app
python3 update_cookies.py && python3 app.py
```
