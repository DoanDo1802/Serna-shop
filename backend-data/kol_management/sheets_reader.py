"""
Module đọc dữ liệu KOL từ Google Sheets
"""
import gspread
import os
from typing import List, Dict, Any

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'kalodata', 'google_credentials.json')

def read_kol_data_from_sheets(spreadsheet_url: str, sheet_name: str = "KOL_management") -> List[Dict[str, Any]]:
    """
    Đọc dữ liệu KOL từ Google Sheets
    
    Args:
        spreadsheet_url: URL của Google Sheet
        sheet_name: Tên sheet (mặc định: KOL_management)
    
    Returns:
        List các KOL với thông tin: tiktok_account, tiktok_link, product, post_links
    """
    try:
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        sh = gc.open_by_url(spreadsheet_url)
        worksheet = sh.worksheet(sheet_name)
        
        # Lấy tất cả dữ liệu
        all_data = worksheet.get_all_records()
        
        kols = []
        for row in all_data:
            # Lấy các cột cần thiết
            tiktok_account = row.get('TIKTOK ACCOUNT', '').strip()
            tiktok_link = row.get('LINK TIKTOK', '').strip()
            product = row.get('SẢN PHẨM', '').strip()
            post_links_raw = row.get('LINK BÀI ĐĂNG', '').strip()
            
            # Tách các link bài đăng (có thể có nhiều link, phân cách bằng dấu xuống dòng hoặc dấu phẩy)
            post_links = []
            if post_links_raw:
                # Tách theo xuống dòng hoặc dấu phẩy
                links = post_links_raw.replace('\n', ',').split(',')
                post_links = [link.strip() for link in links if link.strip() and 'tiktok.com' in link]
            
            if tiktok_account:
                kols.append({
                    'tiktok_account': tiktok_account,
                    'tiktok_link': tiktok_link,
                    'product': product,
                    'post_links': post_links,
                    'post_count': len(post_links)
                })
        
        print(f"✅ Đã đọc {len(kols)} KOL từ Google Sheets")
        return kols
        
    except Exception as e:
        print(f"❌ Lỗi đọc Google Sheets: {e}")
        raise

if __name__ == "__main__":
    # Test
    test_url = "https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit"
    kols = read_kol_data_from_sheets(test_url)
    print(f"\nĐã lấy {len(kols)} KOL")
    for kol in kols[:3]:
        print(f"- {kol['tiktok_account']}: {kol['post_count']} bài đăng")
