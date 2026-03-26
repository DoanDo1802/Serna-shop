# Settings Page - Cookie Management

Trang quản lý cookie tự động cho Kalodata và TikTok.

## Features

### 1. Cookie Status Dashboard
- Hiển thị trạng thái cookie (Hợp lệ / Không hợp lệ / Chưa có)
- Hiển thị nguồn cookie (Tự động / Thủ công)
- Hiển thị thời gian cập nhật lần cuối

### 2. Cookie Refresh
- **Làm mới**: Kiểm tra và chỉ cập nhật nếu cookie hết hạn
- **Force**: Bắt buộc lấy cookie mới, bỏ qua cookie cũ

### 3. Bulk Actions
- Cập nhật tất cả cookies cùng lúc
- Force refresh tất cả

## UI Components

### Status Badges
- 🟢 **Hợp lệ**: Cookie đang hoạt động tốt
- 🔴 **Chưa có**: Chưa có cookie
- ⚪ **Không hợp lệ**: Cookie có vấn đề

### Source Badges
- 🤖 **Tự động**: Cookie được lấy bằng script tự động
- 📝 **Thủ công**: Cookie được nhập vào .env thủ công

## User Flow

### Lần Đầu Tiên
1. User vào Settings page
2. Thấy status "Chưa có" hoặc "Không hợp lệ"
3. Click "Làm mới"
4. Backend mở trình duyệt
5. User đăng nhập thủ công
6. Cookie được lưu tự động

### Lần Sau
1. User vào Settings page
2. Thấy status "Hợp lệ"
3. Click "Làm mới"
4. Backend kiểm tra cookie cũ
5. Nếu còn hạn → Dùng luôn (không cần login)
6. Nếu hết hạn → Yêu cầu login lại

### Force Refresh
1. User click "Force"
2. Backend bỏ qua cookie cũ
3. Mở trình duyệt để login
4. Lấy cookie mới

## API Integration

### Get Status
```typescript
const response = await fetch('http://localhost:5000/api/cookies/status')
const data = await response.json()
```

### Refresh Cookie
```typescript
const response = await fetch('http://localhost:5000/api/cookies/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    platform: 'kalodata', // or 'tiktok' or 'all'
    force: false
  })
})
```

## Error Handling

### Backend Errors
- Connection error → "Không thể kết nối đến backend"
- Cookie error → Hiển thị error message từ backend
- Partial success → Hiển thị kết quả từng platform

### User Feedback
- Loading state với spinner
- Success alert (green)
- Error alert (red)
- Auto-refresh status sau khi update

## Styling

- Uses shadcn/ui components (Card, Button, Badge, Alert)
- Responsive grid layout
- Color-coded status indicators
- Smooth transitions and animations

## Future Enhancements

- [ ] Auto-refresh timer (countdown to next refresh)
- [ ] Cookie expiry prediction
- [ ] Notification when cookie about to expire
- [ ] Cookie history/logs
- [ ] Manual cookie input option
- [ ] Test cookie validity button
