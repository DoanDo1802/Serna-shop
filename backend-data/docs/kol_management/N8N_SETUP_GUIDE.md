# Hướng dẫn Setup n8n Workflow cho TikTok Stats

## Bước 1: Import Workflow vào n8n

1. Mở n8n UI (thường là `http://localhost:5678`)
2. Click vào menu (3 gạch ngang) ở góc trên bên trái
3. Chọn "Import from File" hoặc "Import from URL"
4. Chọn file `n8n_tiktok_stats_workflow.json`
5. Click "Import"

## Bước 2: Activate Workflow

1. Sau khi import, workflow sẽ hiển thị với các nodes:
   ```
   Webhook → HTTP Request → Code Parse → Edit Fields → Code Calculate → Respond
   ```

2. Click vào node "Webhook" để xem URL
   - Production URL sẽ có dạng: `http://localhost:5678/webhook/tiktok-stats`
   - Test URL sẽ có dạng: `http://localhost:5678/webhook-test/tiktok-stats`

3. Click nút "Active" ở góc trên bên phải để activate workflow

## Bước 3: Test Workflow trong n8n

1. Click vào node "Webhook"
2. Click "Listen for Test Event"
3. Mở terminal và chạy:

```bash
curl -X POST http://localhost:5678/webhook-test/tiktok-stats \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@dimkhongquao/video/7579969522069785874"}'
```

4. Kiểm tra kết quả trong n8n UI

## Bước 4: Cấu hình Backend Python

Thêm vào file `.env`:

```bash
# n8n Webhook URL
N8N_WEBHOOK_URL=http://localhost:5678/webhook/tiktok-stats
```

## Bước 5: Test từ Python

```bash
cd backend-data
python3 -c "
from kol_management.tiktok_stats import get_video_stats_via_n8n
import json

stats = get_video_stats_via_n8n(
    'https://www.tiktok.com/@dimkhongquao/video/7579969522069785874'
)

print(json.dumps(stats, indent=2, ensure_ascii=False))
"
```

## Kết quả mong đợi

```json
{
  "video_id": "7579969522069785874",
  "video_url": "https://www.tiktok.com/@dimkhongquao/video/7579969522069785874",
  "views": 150000,
  "likes": 7500,
  "comments": 300,
  "shares": 150,
  "saves": 50,
  "engagement_rate": 5.33,
  "total_engagement": 8000,
  "author": "dimkhongquao",
  "follower": 50000
}
```

## Troubleshooting

### Lỗi: "Connection refused"

n8n chưa chạy. Start n8n:

```bash
npx n8n
# hoặc
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Lỗi: "Webhook not found"

Workflow chưa được activate. Vào n8n UI và click "Active".

### Lỗi: "__UNIVERSAL_DATA_FOR_REHYDRATION__ not found"

TikTok đang block request. Thử:

1. Thêm cookie vào HTTP Request node
2. Thêm headers đầy đủ hơn
3. Sử dụng proxy

### Lỗi: "Cannot read property 'itemInfo' of undefined"

Cấu trúc JSON của TikTok đã thay đổi. Cần update path trong Edit Fields node.

## Cải tiến Workflow

### 1. Thêm Error Handling

Thêm node "IF" sau "Code - Parse JSON":

```javascript
// Check if data exists
return $json.data && $json.data.__DEFAULT_SCOPE__ && 
       $json.data.__DEFAULT_SCOPE__['webapp.video-detail'];
```

### 2. Thêm Retry Logic

Thêm "HTTP Request" node với retry options:

```json
{
  "options": {
    "retry": {
      "maxRetries": 3,
      "retryInterval": 1000
    }
  }
}
```

### 3. Thêm Rate Limiting

Thêm "Wait" node giữa các requests:

```json
{
  "amount": 2,
  "unit": "seconds"
}
```

### 4. Thêm Caching

Sử dụng Redis hoặc Memory Store để cache kết quả:

```javascript
// Check cache first
const cacheKey = `tiktok:${videoId}`;
const cached = await $cache.get(cacheKey);

if (cached) {
  return cached;
}

// ... fetch data ...

// Save to cache (1 hour)
await $cache.set(cacheKey, result, 3600);
```

### 5. Thêm Logging

Thêm node "Function" để log:

```javascript
console.log(`[TikTok Stats] Processing: ${$json.url}`);
console.log(`[TikTok Stats] Result: ${JSON.stringify($json)}`);
return $json;
```

## Production Deployment

### Option 1: n8n Cloud

1. Sign up tại https://n8n.io
2. Import workflow
3. Update `N8N_WEBHOOK_URL` với production URL

### Option 2: Self-hosted

```bash
# Docker Compose
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_password
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  n8n_data:
```

### Option 3: Railway/Render

Deploy n8n lên Railway hoặc Render và update webhook URL.

## Monitoring

### Check Workflow Status

```bash
curl http://localhost:5678/webhook/tiktok-stats/status
```

### View Execution History

Vào n8n UI → Executions để xem lịch sử chạy workflow.

### Setup Alerts

Thêm node "Send Email" hoặc "Slack" để nhận thông báo khi có lỗi.

## Best Practices

1. ✅ Luôn activate workflow sau khi import
2. ✅ Test với test webhook trước khi dùng production
3. ✅ Thêm error handling cho mọi node
4. ✅ Log tất cả requests để debug
5. ✅ Cache kết quả để giảm load
6. ✅ Rate limit để tránh bị TikTok block
7. ✅ Monitor execution history thường xuyên
8. ✅ Backup workflow definition thường xuyên

## Next Steps

Sau khi setup xong n8n workflow, bạn có thể:

1. Chạy test để lấy stats cho 1 video
2. Chạy ranking để lấy stats cho tất cả KOL
3. Setup cron job để tự động update stats hàng ngày
4. Tích hợp với frontend để hiển thị real-time stats
