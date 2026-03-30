#!/bin/bash

# Script khởi động Backend KOL Data

echo "🚀 Khởi động Backend KOL Data Management System..."

# Kiểm tra virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Không tìm thấy virtual environment. Đang tạo..."
    python3 -m venv venv
    echo "✅ Đã tạo virtual environment"
fi

# Kích hoạt virtual environment
echo "📦 Kích hoạt virtual environment..."
source venv/bin/activate

# Cài đặt dependencies nếu cần
echo "📥 Kiểm tra dependencies..."
pip install -q -r requirements.txt

# Kiểm tra Playwright browser
if ! playwright show-trace 2>/dev/null; then
    echo "🌐 Cài đặt Playwright browser..."
    playwright install chromium
fi

# Kiểm tra file .env
if [ ! -f ".env" ]; then
    echo "⚠️  Cảnh báo: Không tìm thấy file .env"
    echo "   Vui lòng tạo file .env từ .env.example và cấu hình"
    echo "   cp .env.example .env"
fi

# Khởi động server
echo "✅ Khởi động Flask server..."
python app.py
