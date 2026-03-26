import gspread
import pandas as pd
import os

# Tên file chứa thông tin xác thực Google Service Account
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'google_credentials.json')

def upload_excel_to_gsheet(excel_path, spreadsheet_url, sheet_name="Sheet1"):
    """
    Đọc dữ liệu từ file Excel và đẩy (ghi đè) lên Google Sheet.
    
    :param excel_path: Đường dẫn tới file Excel (.xlsx)
    :param spreadsheet_url: Đường link đầy đủ của Google Sheet file
    :param sheet_name: Tên của trang tính nội bộ (mặc định Sheet1)
    """
    print(f"\n🚀 Đang chuẩn bị đẩy dữ liệu từ '{excel_path}' lên Google Sheets...")
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Lỗi: Không tìm thấy file cấu hình {CREDENTIALS_FILE}")
        return False
        
    try:
        # 1. Xác thực với Google thông qua file JSON
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        print("✅ Đã kết nối thành công với Google API!")
        
        # 2. Mở file Google Sheet bằng URL
        try:
            sh = gc.open_by_url(spreadsheet_url)
        except gspread.exceptions.APIError as e:
            if e.response.status_code == 403:
                print(f"❌ LỖI QUYỀN TRUY CẬP: Google Sheet của bạn đang từ chối con Bot.")
                print(f"👉 HƯỚNG DẪN: Hãy mở Google Sheet, bấm nút 'Chia sẻ' góc trên bên phải, và thêm cái email sau vào phân quyền 'Người chỉnh sửa' (Editor):")
                print(f"   clawd-sheet@n8n-mac-468610.iam.gserviceaccount.com")
                return False
            else:
                raise e
            
        # 3. Lấy đúng trang tính (Worksheet) cần ghi
        try:
            worksheet = sh.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Nếu trang tính không tồn tại, tạo trang mới
            worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="20")
            print(f"ℹ️ Đã tự động tạo trang tính mới mang tên '{sheet_name}'")

        # 4. Đọc file Excel bằng Pandas và xử lý NaN
        print("📊 Đang phân tích dữ liệu Excel...")
        df = pd.read_excel(excel_path)
        
        # Bỏ đi các cột không cần thiết theo yêu cầu của bạn
        cols_to_drop = [
            "Tổng sản phẩm", 
            "Lượt livestreams", 
            "Lượt videos", 
            "Lượt xem",
            "Thời gian đăng bài lần đầu của nhà sáng tạo"
        ]
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # Xử lý các ô trống (NaN) để Google Sheet không báo lỗi
        df = df.fillna('')
        
        # 5. Đẩy dữ liệu lên Google Sheet (Chế độ NỐI TIẾP thông minh)
        print("☁️ Đang tính toán vị trí nối thêm dữ liệu...")
        
        # Lấy toàn bộ dữ liệu hiện tại trên Sheet để phân tích
        all_data = worksheet.get_all_values()
        
        if len(all_data) == 0:
            # Nếu Sheet trắng tinh -> Ghi cả tiêu đề (Header) + Dữ liệu
            print("📝 Sheet đang trống, bắt đầu ghi dữ liệu kèm Tiêu Đề...")
            data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
            worksheet.update(values=data_to_upload, range_name="A1")
        else:
            # Tìm dòng trống ĐẦU TIÊN thực sự trong bảng (Dựa vào cột B - "Tên nhà sáng tạo")
            # Tránh lỗi append_rows nhảy xuống tận đáy (dòng 50+) do Sheet có kẻ bảng hoặc công thức sẵn
            insert_row_idx = len(all_data) + 1 # Mặc định là dòng cuối cùng
            
            for i, row in enumerate(all_data):
                # Bỏ qua dòng tiêu đề (index 0)
                if i == 0: continue
                
                # Cột B là index 1. Nếu dòng này cột B bị rỗng -> Đây là dòng bắt đầu chèn
                col_b_val = row[1] if len(row) > 1 else ""
                if not str(col_b_val).strip():
                    insert_row_idx = i + 1  # Cộng 1 vì Google Sheet đánh số từ 1
                    break
                    
            print(f"📥 Bảng đang có dữ liệu. Bắt đầu chèn nối tiếp từ dòng số {insert_row_idx}...")
            data_to_append = df.values.tolist()
            worksheet.update(values=data_to_append, range_name=f"A{insert_row_idx}")
            
        print(f"🎉 HOÀN THÀNH! Dữ liệu đã được lưu trữ thành công trên Google Sheets.")
        print(f"🔗 Link kiểm tra: {spreadsheet_url}")
        return True
        
    except Exception as e:
        print(f"❌ Xảy ra lỗi trong quá trình đẩy dữ liệu: {e}")
        return False

# Viết mã test nhanh nếu chạy thẳng file này
if __name__ == "__main__":
    # Thay link Google Sheet thật của bạn vào đây để test
    TEST_SHEET_URL = "https://docs.google.com/spreadsheets/d/XXXXXXXXX/edit"
    test_excel = os.path.join(os.path.dirname(__file__), 'export.xlsx')
    
    if os.path.exists(test_excel):
        upload_excel_to_gsheet(test_excel, TEST_SHEET_URL)
    else:
        print(f"⚠️ Vui lòng cung cấp file Excel mẫu tại {test_excel} để test.")
