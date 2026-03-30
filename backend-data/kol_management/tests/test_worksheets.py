"""
Test script để kiểm tra tính năng lấy danh sách worksheets
"""
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from kol_management.sheets_reader import get_worksheet_names

# Lấy URL từ env hoặc dùng URL mặc định
test_url = os.environ.get('KOL_SHEET_URL', 'https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit')

print(f"📋 Đang lấy danh sách worksheets từ: {test_url[:50]}...")
print()

try:
    worksheets = get_worksheet_names(test_url)
    
    print(f"✅ Tìm thấy {len(worksheets)} worksheet(s):")
    for i, sheet in enumerate(worksheets, 1):
        print(f"   {i}. {sheet}")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
