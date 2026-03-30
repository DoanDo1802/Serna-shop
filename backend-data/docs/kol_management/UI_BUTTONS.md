# Hướng dẫn sử dụng các nút trong KOL Management

## Tổng quan UI

Giao diện có 2 phần chính:
1. **Header** - Quản lý Google Sheets
2. **Bảng xếp hạng** - Xem và cập nhật ranking

---

## 1. Header (Phần trên)

### 🔗 Google Sheet URL
- **Chức năng:** Nhập link Google Sheets chứa danh sách KOL
- **Tự động:** Khi paste URL, hệ thống tự động lấy danh sách các tab

### 📋 Dropdown chọn Sheet
- **Chức năng:** Chọn tab nào trong Google Sheets để làm việc
- **Tự động hiện:** Sau khi paste URL hợp lệ
- **Ví dụ:** Sheet1, KOL_management, Data, etc.

### 🔄 Nút "Đồng bộ"
- **Chức năng:** Đọc dữ liệu cơ bản từ Google Sheets
- **Không lấy stats:** Chỉ lấy tên KOL, link, sản phẩm, số bài đăng
- **Tốc độ:** Rất nhanh (~1-2 giây)
- **Khi nào dùng:** 
  - Xem danh sách KOL trong sheet
  - Kiểm tra KOL nào đã đăng bài
  - Không cần số liệu chi tiết

**Tab "Quản lý KOL" sẽ hiển thị:**
- Tên TikTok
- Sản phẩm
- Số bài đăng
- Link bài đăng

---

## 2. Bảng xếp hạng (Tab "Bảng xếp hạng")

### 📊 Nút "Tải bảng xếp hạng" / "Cập nhật từ TikTok"

**Tên nút thay đổi tùy trạng thái:**
- Chưa có dữ liệu: **"Tải bảng xếp hạng"**
- Đã có dữ liệu: **"Cập nhật từ TikTok"**

**Chức năng:**
- Lấy dữ liệu đầy đủ từ TikTok (views, likes, comments, shares)
- Tính toán ranking và KOL score
- Lưu vào Supabase database
- Đồng bộ với Google Sheets (thêm/xóa/cập nhật KOL)

**Tốc độ:** Chậm (~30-60 giây tùy số KOL và video)

**Khi nào dùng:**
- Lần đầu tiên setup
- Muốn cập nhật số liệu mới nhất
- Đã thêm/xóa KOL trong Google Sheets
- Định kỳ mỗi ngày/tuần

**Bảng xếp hạng sẽ hiển thị:**
- Hạng (🥇🥈🥉)
- TikTok Account
- Sản phẩm
- KOL Score
- Số videos
- Thời gian đăng (12d, 5d)
- Lượt xem
- Likes
- Tổng Engagement
- Avg ER (%)

---

## Flow sử dụng

### Lần đầu tiên:

```
1. Paste Google Sheet URL
   ↓
2. Chọn sheet từ dropdown
   ↓
3. (Optional) Click "Đồng bộ" để xem danh sách KOL
   ↓
4. Chuyển sang tab "Bảng xếp hạng"
   ↓
5. Click "Tải bảng xếp hạng"
   ↓
6. Đợi 30-60 giây
   ↓
7. Xem kết quả!
```

### Lần sau (đã có dữ liệu):

```
1. Mở trang / F5
   ↓
2. Dữ liệu tự động load từ database (nhanh!)
   ↓
3. Xem bảng xếp hạng
```

### Khi muốn cập nhật:

```
1. (Optional) Thêm/xóa KOL trong Google Sheets
   ↓
2. Click "Cập nhật từ TikTok"
   ↓
3. Đợi 30-60 giây
   ↓
4. Dữ liệu mới được cập nhật và lưu vào database
```

---

## So sánh các nút

| Nút | Tốc độ | Dữ liệu | Lưu DB | Khi nào dùng |
|-----|--------|---------|--------|--------------|
| **Đồng bộ** | ⚡ Rất nhanh (1-2s) | Cơ bản (tên, link, số bài) | ❌ Không | Xem danh sách nhanh |
| **Tải bảng xếp hạng** | 🐌 Chậm (30-60s) | Đầy đủ (views, likes, ER) | ✅ Có | Lần đầu / Cập nhật định kỳ |
| **F5 trang** | ⚡⚡ Cực nhanh (<1s) | Từ cache | - | Xem lại dữ liệu đã lưu |

---

## Tips & Tricks

### 💡 Tip 1: Xem nhanh danh sách KOL
```
Click "Đồng bộ" → Tab "Quản lý KOL"
Không cần đợi lâu, chỉ xem KOL nào đã đăng bài
```

### 💡 Tip 2: Cập nhật định kỳ
```
Mỗi sáng: Click "Cập nhật từ TikTok"
Cả ngày: F5 để xem lại (không tốn thời gian)
```

### 💡 Tip 3: Thêm KOL mới
```
1. Thêm KOL vào Google Sheets
2. Click "Cập nhật từ TikTok"
3. KOL mới tự động xuất hiện trong bảng xếp hạng
```

### 💡 Tip 4: Xóa KOL
```
1. Xóa KOL khỏi Google Sheets
2. Click "Cập nhật từ TikTok"
3. KOL tự động biến mất khỏi database
```

---

## Troubleshooting

### ❓ Không thấy dropdown chọn sheet
→ Kiểm tra URL Google Sheets có đúng không
→ Đảm bảo sheet được share công khai hoặc có quyền truy cập

### ❓ Nút "Đồng bộ" bị disable
→ Chưa chọn sheet từ dropdown
→ Đang loading worksheets

### ❓ "Tải bảng xếp hạng" chạy mãi không xong
→ Có thể n8n webhook không hoạt động
→ Check console log để xem lỗi
→ Thử lại sau vài phút

### ❓ F5 không thấy dữ liệu
→ Chưa chạy "Tải bảng xếp hạng" lần nào
→ Hoặc đang xem sheet khác (check dropdown)

### ❓ Dữ liệu không cập nhật
→ Đang xem cache, cần click "Cập nhật từ TikTok"
→ Hoặc chưa lưu vào database (check console log)

---

## Best Practices

1. ✅ **Lần đầu:** Chạy "Tải bảng xếp hạng" để tạo cache
2. ✅ **Hàng ngày:** Click "Cập nhật từ TikTok" vào buổi sáng
3. ✅ **Xem lại:** Chỉ cần F5 trang (không cần click gì)
4. ✅ **Nhiều sheet:** Mỗi sheet có cache riêng, tự do chuyển đổi
5. ✅ **Thêm/xóa KOL:** Sửa trong Sheets → Click "Cập nhật từ TikTok"
