# Settings Page - Hướng Dẫn Sử Dụng

## Truy Cập

1. Mở ứng dụng: `http://localhost:3000`
2. Click vào **"Cài đặt"** ở cuối sidebar (bên trái)
3. Hoặc truy cập trực tiếp: `http://localhost:3000/settings`

## Giao Diện

### Layout
```
┌─────────────┬──────────────────────────────────────────┐
│             │  Cài Đặt                                 │
│             │  Quản lý cookie và cấu hình hệ thống     │
│             │                                          │
│  Sidebar    │  ┌──────────────┐  ┌──────────────┐    │
│             │  │  Kalodata    │  │  TikTok      │    │
│  - Tổng quan│  │  Cookie      │  │  Cookie      │    │
│  - Booking  │  │              │  │              │    │
│  - Sản phẩm │  │  Status: ✅  │  │  Status: ✅  │    │
│  - Agent    │  │  Nguồn: 🤖   │  │  Nguồn: 🤖   │    │
│  - Phân tích│  │              │  │              │    │
│             │  │  [Làm mới]   │  │  [Làm mới]   │    │
│  - Cài đặt ◄│  │  [Force]     │  │  [Force]     │    │
│             │  └──────────────┘  └──────────────┘    │
│             │                                          │
│             │  ┌────────────────────────────────────┐ │
│             │  │  Thao Tác Nhanh                    │ │
│             │  │  [Làm mới tất cả]  [Force tất cả]  │ │
│             │  └────────────────────────────────────┘ │
└─────────────┴──────────────────────────────────────────┘
```

## Các Thành Phần

### 1. Cookie Status Cards

Mỗi platform (Kalodata, TikTok) có một card riêng hiển thị:

**Status Badge:**
- 🟢 **Hợp lệ**: Cookie đang hoạt động tốt
- 🔴 **Chưa có**: Chưa có cookie
- ⚪ **Không hợp lệ**: Cookie có vấn đề

**Nguồn:**
- 🤖 **Tự động**: Cookie được lấy bằng script tự động
- 📝 **Thủ công**: Cookie được nhập vào .env thủ công

**Thời gian cập nhật:**
- Hiển thị lần cuối cookie được cập nhật

### 2. Action Buttons

**Làm mới:**
- Kiểm tra cookie hiện tại
- Chỉ cập nhật nếu cookie hết hạn
- Không cần login nếu cookie còn hạn

**Force:**
- Bắt buộc lấy cookie mới
- Bỏ qua cookie cũ
- Luôn yêu cầu login

### 3. Quick Actions

**Làm mới tất cả:**
- Cập nhật cả Kalodata và TikTok cùng lúc
- Tiết kiệm thời gian

**Force tất cả:**
- Force refresh cả 2 platforms

## Quy Trình Sử Dụng

### Lần Đầu Tiên

1. **Vào Settings page**
   - Status hiển thị: 🔴 Chưa có

2. **Click "Làm mới"**
   - Button chuyển sang trạng thái loading
   - Backend mở trình duyệt tự động

3. **Đăng nhập**
   - Trình duyệt mở trang Kalodata/TikTok
   - Bạn đăng nhập thủ công
   - Nhấn ENTER ở terminal khi xong

4. **Hoàn tất**
   - Cookie được lưu tự động
   - Status chuyển sang: 🟢 Hợp lệ
   - Nguồn: 🤖 Tự động

### Lần Sau

1. **Vào Settings page**
   - Status hiển thị: 🟢 Hợp lệ

2. **Click "Làm mới"** (nếu cần)
   - Hệ thống kiểm tra cookie cũ
   - Nếu còn hạn → Dùng luôn (không cần login)
   - Nếu hết hạn → Yêu cầu login lại

3. **Hoàn tất**
   - Cookie được cập nhật
   - Không cần thao tác gì thêm

### Khi Cookie Hết Hạn

1. **Nhận biết:**
   - Status chuyển sang: ⚪ Không hợp lệ
   - Hoặc API trả về lỗi cookie

2. **Refresh:**
   - Click "Làm mới"
   - Hệ thống tự động phát hiện hết hạn
   - Yêu cầu login lại

3. **Hoặc Force:**
   - Click "Force" để bắt buộc lấy mới
   - Không cần chờ hệ thống phát hiện

## Thông Báo

### Success (Xanh)
```
✅ Đã cập nhật cookie kalodata thành công!
```
- Cookie đã được lưu
- Có thể sử dụng ngay

### Error (Đỏ)
```
❌ Không thể kết nối đến backend
```
- Kiểm tra backend đang chạy
- Check URL: http://localhost:5000

```
❌ kalodata: Cookie không hợp lệ
```
- Thử lại với Force
- Đăng nhập lại khi được yêu cầu

## Tips

### 💡 Khi nào cần Refresh?

**Làm mới thường xuyên:**
- Trước khi export dữ liệu Kalodata
- Trước khi gửi tin nhắn TikTok
- Khi thấy API trả về lỗi cookie

**Force refresh khi:**
- Cookie bị lỗi
- Muốn đổi tài khoản
- Cần cookie mới nhất

### 💡 Tiết kiệm thời gian

- Dùng "Làm mới tất cả" thay vì refresh từng cái
- Chỉ Force khi thực sự cần
- Cookie tự động dùng lại, không cần refresh liên tục

### 💡 Troubleshooting

**Backend không response:**
```bash
# Check backend
curl http://localhost:5000/health

# Restart backend
cd backend-data
python3 app.py
```

**Trình duyệt không mở:**
```bash
# Check Playwright
pip install playwright
playwright install chromium
```

**Cookie vẫn không hợp lệ:**
- Thử Force refresh
- Check file .env có cookie không
- Xem log ở terminal backend

## Keyboard Shortcuts

Hiện tại chưa có, nhưng có thể thêm:
- `Ctrl/Cmd + R`: Refresh tất cả
- `Ctrl/Cmd + K`: Mở Kalodata refresh
- `Ctrl/Cmd + T`: Mở TikTok refresh

## Mobile Support

Settings page responsive, hoạt động tốt trên mobile:
- Cards xếp dọc thay vì ngang
- Buttons full-width
- Touch-friendly

## Accessibility

- Keyboard navigation support
- Screen reader friendly
- Color contrast WCAG compliant
- Focus indicators visible

## Future Features

- [ ] Auto-refresh countdown timer
- [ ] Cookie expiry prediction
- [ ] Email notification
- [ ] Cookie history log
- [ ] Manual cookie input
- [ ] Test cookie button
