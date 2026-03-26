import os
import pandas as pd

# Import các tool đã viết thành module
from datakoc import get_follower_stats
from data_store import load_saved_creators, make_creator_key, merge_creators_into_store, normalize_creator_record

def process_exported_file(excel_path):
    print(f"\n==============================================")
    print(f"Bắt đầu xử lý file Excel: {excel_path}")
    print(f"==============================================\n")
    
    # 1. Đọc file Excel từ exp_playwright.py
    print("📊 Đang đọc file Excel...")
    df = pd.read_excel(excel_path)
    
    # 2. Xóa các cột rác không cần thiết từ đầu
    cols_to_drop = [
        "Tổng sản phẩm", 
        "Lượt livestreams", 
        "Lượt videos", 
        "Lượt xem",
        "Thời gian đăng bài lần đầu của nhà sáng tạo",
        "Tài khoản NST"
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    # 3. Thêm 3 cột mới vào DataFrame nếu chưa có
    new_columns = ["Độ tuổi người xem", "Giới tính người xem", "Tỷ lệ tương tác"]
    for col in new_columns:
        if col not in df.columns:
            df[col] = "" # Khởi tạo cột trống
    # Chuyển DataFrame thành list of dicts để xử lý dễ hơn
    records = df.to_dict('records')
    
    # --- BƯỚC MỚI: DEDUPLICATION (Lọc trùng lặp) ---
    print("\n🛡️ Khởi động hệ thống chống trùng lặp dữ liệu...")
    existing_keys = {key for item in load_saved_creators() if (key := make_creator_key(item))}
    batch_keys = set()
    fresh_records = []
    duplicate_count = 0

    for row in records:
        key = make_creator_key(row)
        if key and (key in existing_keys or key in batch_keys):
            duplicate_count += 1
            continue

        if key:
            batch_keys.add(key)
        fresh_records.append(row)

    print(f"✂️ Đã gạch bỏ {duplicate_count} KOL trùng lặp. Giữ lại {len(fresh_records)} KOL mới tinh.")
    records = fresh_records
    # -----------------------------------------------
    
    if not records:
        print("\n✅ TẤT CẢ KOL TRONG FILE NÀY ĐỀU ĐÃ CÓ TRÊN SHEET. TIẾN TRÌNH DỪNG LẠI!")
        return
    print(f"\n🔍 Bắt đầu quét chuyên sâu cho {len(records)} KOLs...")
    for idx, row in enumerate(records):
        CreatorName = row.get("Tên nhà sáng tạo", f"KOL {idx}")
        ProfileLink = row.get("Link chi tiết trên Kalodata", "")
        
        print(f"\n[{idx+1}/{len(records)}] Đang quét KOL: {CreatorName}")
        
        if not ProfileLink or not str(ProfileLink).startswith("http"):
            print("  -> Không có Link Profile hợp lệ. Bỏ qua.")
            continue
            
        # Gọi hàm lấy dữ liệu từ datakoc.py
        stats = get_follower_stats(ProfileLink)
        
        if stats:
            # Lấp dữ liệu vào 3 cột rỗng
            row["Độ tuổi người xem"] = stats.get("top_2_ages", "")
            row["Giới tính người xem"] = stats.get("majority_gender", "")
            row["Tỷ lệ tương tác"] = stats.get("engagement_rate", "")
        else:
            print("  -> Thất bại, để trống dữ liệu.")
            
    # 5. Lưu lại thành DataFrame mới
    augmented_df = pd.DataFrame(records)
    
    # 6. Ghi đè vào một file Excel Tạm (augmented_export.xlsx)
    augmented_excel_path = excel_path.replace(".xlsx", "_hoan_thien.xlsx")
    augmented_df.to_excel(augmented_excel_path, index=False)
    print(f"\n✅ Đã lưu xong file dữ liệu Hoàn Thiện tại: {augmented_excel_path}")

    persist_result = merge_creators_into_store(
        [normalize_creator_record(row) for row in records],
        deduplicate=True,
        last_crawl={
            "source": "process_all",
            "file_path": excel_path,
        },
    )
    print(
        f"\n💾 Đã lưu {persist_result['new_count']} KOL mới vào local store. "
        f"Tổng đang lưu: {persist_result['count']} KOL."
    )
    
if __name__ == "__main__":
    # Test thử trên 1 file mới nhất trong thư mục exports
    export_dir = os.path.join(os.path.dirname(__file__), "exports")
    
    if os.path.exists(export_dir):
        files = [os.path.join(export_dir, f) for f in os.listdir(export_dir) if f.endswith(".xlsx") and "hoan_thien" not in f]
        if files:
            # Lấy file mới nhất
            latest_file = max(files, key=os.path.getctime)
            process_exported_file(latest_file)
        else:
            print("Chưa có file export nào từ kalodata.")
    else:
        print(f"Không tìm thấy thư mục {export_dir}")
