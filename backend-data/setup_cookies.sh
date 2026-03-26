#!/bin/bash

# Script setup cookie tự động cho lần đầu tiên

echo "🚀 Setup Cookie Tự Động"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 chưa được cài đặt!"
    exit 1
fi

# Check Playwright
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "📦 Đang cài đặt Playwright..."
    pip install playwright
    playwright install chromium
fi

echo "✅ Dependencies đã sẵn sàng"
echo ""

# Run update script
echo "🔄 Đang lấy cookie..."
python3 update_cookies.py

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ SETUP THÀNH CÔNG!"
    echo "======================================"
    echo ""
    echo "💡 Giờ bạn có thể:"
    echo "   1. Chạy backend: python3 app.py"
    echo "   2. Update cookie khi cần: python3 update_cookies.py"
    echo ""
else
    echo ""
    echo "❌ Setup thất bại. Vui lòng kiểm tra lỗi ở trên."
    exit 1
fi
