# 🔄 Hướng Dẫn Đổi Tài Khoản

## Quy Trình Mới (Đã Cải Thiện)

### Khi Click "Force":

1. **Trình duyệt mở** (không load cookie cũ)
2. **Bạn có thời gian:**
   - Logout tài khoản cũ (nếu muốn đổi)
   - Login tài khoản mới
   - Hoặc giữ nguyên tài khoản hiện tại
3. **Terminal hiển thị:**
   ```
   🔄 FORCE REFRESH MODE
   ============================================================
   Bạn có thể:
   1. Giữ nguyên tài khoản hiện tại (nếu đã login)
   2. Logout và đăng nhập tài khoản khác
   3. Đăng nhập nếu chưa login
   ============================================================
   
   👉 Nhấn ENTER khi đã sẵn sàng...
   ```
4. **Sau khi xong** → Nhấn ENTER
5. **Cookie được lưu** với tài khoản bạn chọn

---

## Ví Dụ: Đổi Tài Khoản TikTok

### Bước 1: Click Force
- Vào Settings: http://localhost:3000/settings
- Click nút **"Force"** ở card TikTok

### Bước 2: Trình Duyệt Mở
- TikTok mở ra
- **Không tự động login** (vì không load cookie cũ)

### Bước 3: Đăng Nhập
**Option A: Đổi tài khoản**
1. Nếu đang login tài khoản cũ → Click avatar → Logout
2. Login tài khoản mới

**Option B: Giữ nguyên**
1. Nếu đã login đúng tài khoản → Không cần làm gì

**Option C: Chưa login**
1. Click "Log in"
2. Đăng nhập tài khoản của bạn

### Bước 4: Xác Nhận
- Quay lại terminal
- Nhấn ENTER
- Cookie được lưu!

---

## So Sánh: Làm Mới vs Force

| | Làm Mới | Force |
|---|---------|-------|
| **Load cookie cũ** | ✅ Có | ❌ Không |
| **Tự động login** | ✅ Có | ❌ Không |
| **Đổi tài khoản** | ❌ Khó | ✅ Dễ |
| **Khi nào dùng** | Refresh cookie cùng tài khoản | Đổi tài khoản hoặc lấy mới |

---

## Tips

### 💡 Muốn đổi tài khoản?
→ Dùng **Force**

### 💡 Chỉ muốn refresh cookie?
→ Dùng **Làm mới**

### 💡 Không chắc?
→ Dùng **Force** (an toàn hơn, có thời gian kiểm tra)

---

## Troubleshooting

### Trình duyệt vẫn tự động login tài khoản cũ?
- Có thể do browser cache
- Giải pháp: Logout rồi login lại

### Muốn test với tài khoản khác nhưng không muốn mất cookie cũ?
```bash
# Backup cookie hiện tại
cp backend-data/tiktok/.tiktok_cookie backend-data/tiktok/.tiktok_cookie.backup
cp backend-data/tiktok/.tiktok_cookie.json backend-data/tiktok/.tiktok_cookie.json.backup

# Sau khi test xong, restore
cp backend-data/tiktok/.tiktok_cookie.backup backend-data/tiktok/.tiktok_cookie
cp backend-data/tiktok/.tiktok_cookie.json.backup backend-data/tiktok/.tiktok_cookie.json
```

---

## Tóm Tắt

**Trước đây:**
- Click Force → Trình duyệt mở → Tự động login tài khoản cũ → Không có cơ hội đổi

**Bây giờ:**
- Click Force → Trình duyệt mở (không login) → Bạn chọn tài khoản → Nhấn ENTER → Xong!

Đơn giản và linh hoạt hơn! 🎉
