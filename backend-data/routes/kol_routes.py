from flask import Blueprint, request, jsonify
import os
import traceback
import json
from kol_management.kol_processor import process_kol_data, rank_kols_by_engagement
from kol_management.sheets_reader import read_kol_data_from_sheets, read_generic_sheet_data

kol_bp = Blueprint('kol_routes', __name__, url_prefix='/api/kol')

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'kol_management', 'database')
APPROVED_FILE = os.path.join(DB_DIR, 'approved_kols.json')
PROCESSED_BOOKINGS_FILE = os.path.join(DB_DIR, 'processed_bookings.json')
REJECTION_HISTORY_FILE = os.path.join(DB_DIR, 'rejection_history.json')
RANKING_FILE = os.path.join(DB_DIR, 'kol_ranking.json')

def load_json_db(file_path, default_type=list):
    if not os.path.exists(file_path):
        return default_type()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_type()

def save_json_db(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@kol_bp.route('/approved-list', methods=['GET'])
def get_approved_kols():
    return jsonify({"success": True, "kols": load_json_db(APPROVED_FILE)})

@kol_bp.route('/processed-bookings', methods=['GET'])
def get_processed_bookings():
    return jsonify({"success": True, "ids": load_json_db(PROCESSED_BOOKINGS_FILE)})

@kol_bp.route('/rejection-history', methods=['GET'])
def get_rejection_history():
    return jsonify({"success": True, "history": load_json_db(REJECTION_HISTORY_FILE, default_type=dict)})

@kol_bp.route('/ranking', methods=['GET'])
def get_kol_ranking():
    """Lấy bảng xếp hạng KOL từ JSON database"""
    try:
        ranking = load_json_db(RANKING_FILE, default_type=list)
        # Sắp xếp theo KOL Score giảm dần
        ranking.sort(key=lambda x: x.get('kol_score', 0), reverse=True)
        return jsonify({"success": True, "ranking": ranking})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/update-ranking', methods=['POST'])
def update_kol_ranking():
    """Cập nhật bảng xếp hạng bằng cách quét stats của tất cả video của KOL đã duyệt"""
    try:
        from kol_management.tiktok_stats import get_video_stats
        from kol_management.video_scoring import rank_kols_by_score
        
        approved_kols = load_json_db(APPROVED_FILE)
        kol_data_for_scoring = []
        
        for kol in approved_kols:
            tiktok_account = kol.get('tiktok_account')
            post_links = kol.get('post_links', [])
            
            video_stats = []
            for url in post_links:
                stats = get_video_stats(url)
                if 'error' not in stats:
                    video_stats.append(stats)
            
            # Chuẩn bị dữ liệu cho video_scoring
            kol_entry = {
                "tiktok_account": tiktok_account,
                "tiktok_link": kol.get('tiktok_link', ''),
                "booking_code": kol.get('booking_code', 'N/A'),
                "product": kol.get('product', '-'),
                "videos": video_stats
            }
            kol_data_for_scoring.append(kol_entry)
            
        # Sử dụng hệ thống tính điểm phức tạp
        ranked_kols = rank_kols_by_score(kol_data_for_scoring, method='weighted')
        
        # Thêm các trường tổng hợp để hiển thị dễ dàng ở frontend
        for kol in ranked_kols:
            valid_videos = kol.get('scored_videos', [])
            kol['total_videos'] = len(valid_videos)
            kol['total_views'] = sum(v.get('views', 0) for v in valid_videos)
            kol['total_likes'] = sum(v.get('likes', 0) for v in valid_videos)
            kol['total_comments'] = sum(v.get('comments', 0) for v in valid_videos)
            kol['total_shares'] = sum(v.get('shares', 0) for v in valid_videos)
            kol['total_engagement'] = sum(v.get('total_engagement', 0) for v in valid_videos)
            
            # Tính tuổi video mới nhất (ngày)
            if valid_videos:
                kol['latest_video_age'] = round(min(v.get('age_in_days', 90) for v in valid_videos), 1)
            else:
                kol['latest_video_age'] = None
                
            # Engagement rate trung bình
            if kol['total_views'] > 0:
                kol['avg_engagement_rate'] = round((kol['total_engagement'] / kol['total_views'] * 100), 2)
            else:
                kol['avg_engagement_rate'] = 0.0
            
            # Đảm bảo kol_score có độ chính xác 2 chữ số
            kol['kol_score'] = round(kol.get('kol_score', 0), 2)
            
        # Lưu vào JSON
        save_json_db(RANKING_FILE, ranked_kols)
        
        return jsonify({"success": True, "count": len(ranked_kols)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

def send_email_helper(email_to, subject, body_html):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_pass:
        raise Exception("Chưa cấu hình SMTP server (SMTP_USER/SMTP_PASSWORD)")
        
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html'))
    
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    return True

@kol_bp.route('/approve', methods=['POST'])
def approve_kol():
    try:
        data = request.json or {}
        kol = data.get('kol')
        booking_id = data.get('booking_id') # timestamp
        
        if not kol or not booking_id:
            return jsonify({"success": False, "error": "Thiếu dữ dữ liệu hoặc booking_id"}), 400
        
        # Thêm vào danh sách duyệt
        approved = load_json_db(APPROVED_FILE)
        # Kiểm tra trùng theo tiktok_account
        if not any(a.get('tiktok_account') == kol.get('tiktok_account') for a in approved):
            # Tạo mã booking ngẫu nhiên: BK-XXXXXX
            import string
            import random
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_code = f"BK-{random_suffix}"
            
            kol['booking_code'] = new_code
            approved.append(kol)
            save_json_db(APPROVED_FILE, approved)
        
        # Đánh dấu booking đã xử lý
        processed = load_json_db(PROCESSED_BOOKINGS_FILE)
        if booking_id not in processed:
            processed.append(booking_id)
            save_json_db(PROCESSED_BOOKINGS_FILE, processed)
            
        # Tự động gửi email chúc mừng nếu có email
        reg_info = kol.get('registration_info', {})
        email_to = reg_info.get('email')
        tiktok_account = kol.get('tiktok_account')
        booking_code = kol.get('booking_code')
        
        if email_to and booking_code:
            try:
                subject = f"Chúc mừng! Bạn đã được duyệt tham gia chiến dịch KOL - {tiktok_account}"
                form_link = f"https://docs.google.com/forms/d/e/1FAIpQLSf2z19Pl28n74yPwG7fLcfk4vkaojoiZah-n3vaEylekFJ3wg/viewform?usp=pp_url&entry.587310383={booking_code}"
                
                body = f"""
                <html>
                <body>
                    <p>Chào bạn <b>{tiktok_account}</b>,</p>
                    <p>Chúc mừng bạn đã được duyệt tham gia chiến dịch KOL của chúng tôi!</p>
                    <p>Mã Booking của bạn là: <b style="color: #007bff; font-size: 1.2em;">{booking_code}</b></p>
                    <p>Vui lòng thực hiện video và cập nhật link video vào form theo đường dẫn dưới đây:</p>
                    <p><a href="{form_link}" style="display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Cập nhật link video tại đây</a></p>
                    <p>Hoặc copy link này: {form_link}</p>
                    <br>
                    <p>Cảm ơn bạn đã đồng hành cùng IonQ!</p>
                    <p>Trân trọng,</p>
                    <p><b>Đội ngũ IonQ</b></p>
                </body>
                </html>
                """
                send_email_helper(email_to, subject, body)
                print(f"✅ Đã tự động gửi email chúc mừng tới {email_to}")
            except Exception as mail_err:
                print(f"⚠️ Không thể gửi email tự động: {mail_err}")
            
        return jsonify({"success": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/reject', methods=['POST'])
def reject_kol():
    try:
        data = request.json or {}
        booking_id = data.get('booking_id')
        tiktok_id = data.get('tiktok_id')
        
        if not booking_id:
            return jsonify({"success": False, "error": "Thiếu booking_id"}), 400
            
        # Đánh dấu booking đã xử lý
        processed = load_json_db(PROCESSED_BOOKINGS_FILE)
        if booking_id not in processed:
            processed.append(booking_id)
            save_json_db(PROCESSED_BOOKINGS_FILE, processed)
        
        # Cập nhật lịch sử từ chối theo tiktok_id (nếu có)
        if tiktok_id:
            history = load_json_db(REJECTION_HISTORY_FILE, default_type=dict)
            history[str(tiktok_id)] = history.get(str(tiktok_id), 0) + 1
            save_json_db(REJECTION_HISTORY_FILE, history)
            
        return jsonify({"success": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/send-notification', methods=['POST'])
def send_notification():
    try:
        data = request.json or {}
        email_to = data.get('email')
        booking_code = data.get('booking_code')
        tiktok_account = data.get('tiktok_account')
        
        if not email_to or not booking_code:
            return jsonify({"success": False, "error": "Thiếu thông tin người nhận hoặc mã booking"}), 400
            
        # Tạo nội dung email nhắc nhở
        subject = f"[Nhắc nhở] Hoàn thiện Video Booking - {tiktok_account}"
        form_link = f"https://docs.google.com/forms/d/e/1FAIpQLSf2z19Pl28n74yPwG7fLcfk4vkaojoiZah-n3vaEylekFJ3wg/viewform?usp=pp_url&entry.587310383={booking_code}"
        
        body = f"""
        <html>
        <body>
            <p>Chào bạn <b>{tiktok_account}</b>,</p>
            <p>Chúng tôi nhận thấy bạn chưa hoàn thành video cho đợt booking mã <b>{booking_code}</b>.</p>
            <p>Vui lòng sớm hoàn thiện và cập nhật link video vào form theo đường dẫn dưới đây để chúng tôi ghi nhận kết quả:</p>
            <p><a href="{form_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Cập nhật link video tại đây</a></p>
            <p>Hoặc copy link này: {form_link}</p>
            <br>
            <p>Trân trọng,</p>
            <p><b>Đội ngũ IonQ</b></p>
        </body>
        </html>
        """
        
        send_email_helper(email_to, subject, body)
        return jsonify({"success": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/sync-videos', methods=['POST'])
def sync_videos():
    try:
        from kol_management.sheets_reader import read_sheet_raw_values
        sheet_url = os.getenv('KOL_SHEET_URL')
        if not sheet_url:
            return jsonify({"success": False, "error": "Chưa có KOL_SHEET_URL"}), 500
            
        # Đọc dữ liệu dạng List of Lists để tránh lỗi trùng header
        raw_rows = read_sheet_raw_values(sheet_url, 'Video')
        if not raw_rows or len(raw_rows) < 1:
            return jsonify({"success": True, "updated": 0})
            
        headers = [str(h).lower().strip() for h in raw_rows[0]]
        data_rows = raw_rows[1:]
        
        # Xác định các index cột cần thiết
        booking_id_idx = -1
        video_link_indices = []
        
        for i, header in enumerate(headers):
            if 'booking id' in header:
                booking_id_idx = i
            elif 'link video' in header:
                video_link_indices.append(i)
                
        if booking_id_idx == -1:
            return jsonify({"success": False, "error": "Không tìm thấy cột 'Booking ID' trong sheet Video"}), 400
            
        approved_kols = load_json_db(APPROVED_FILE)
        updated_count = 0
        
        for kol in approved_kols:
            booking_code = kol.get('booking_code')
            if not booking_code:
                continue
                
            all_links = set(kol.get('post_links', []))
            
            for row in data_rows:
                # Đảm bảo row đủ độ dài
                if len(row) <= booking_id_idx:
                    continue
                    
                row_booking_id = str(row[booking_id_idx]).strip()
                
                if row_booking_id == booking_code:
                    # Lấy từ tất cả các cột video đã tìm thấy
                    for idx in video_link_indices:
                        if len(row) > idx:
                            val = str(row[idx]).strip()
                            if val and val.startswith('http'):
                                all_links.add(val)
            
            # Cập nhật lại cho KOL
            new_links = list(all_links)
            if len(new_links) != len(kol.get('post_links', [])):
                kol['post_links'] = new_links
                kol['post_count'] = len(new_links)
                updated_count += 1
                
        if updated_count > 0:
            save_json_db(APPROVED_FILE, approved_kols)
            
        return jsonify({"success": True, "updated": updated_count})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/delete-approved', methods=['POST'])
def delete_approved_kol():
    try:
        data = request.json or {}
        tiktok_account = data.get('tiktok_account')
        
        approved = load_json_db(APPROVED_FILE)
        approved = [a for a in approved if a.get('tiktok_account') != tiktok_account]
        save_json_db(APPROVED_FILE, approved)
        
        return jsonify({"success": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/sheet-data', methods=['POST'])
def get_generic_sheet_data():
    try:
        data = request.json or {}
        spreadsheet_url = data.get('spreadsheet_url', os.environ.get('KOL_SHEET_URL'))
        sheet_name = data.get('sheet_name')
        
        if not spreadsheet_url or not sheet_name:
            return jsonify({"success": False, "error": "Thiếu spreadsheet_url hoặc sheet_name"}), 400
        
        records = read_generic_sheet_data(spreadsheet_url, sheet_name)
        
        return jsonify({
            "success": True,
            "data": records,
            "total": len(records)
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/sync', methods=['POST'])
def sync_kol_data():
    try:
        data = request.json or {}
        spreadsheet_url = data.get('spreadsheet_url', os.environ.get('KOL_SHEET_URL'))
        sheet_name = data.get('sheet_name', 'KOL_management')
        fetch_stats = data.get('fetch_stats', False)
        
        if not spreadsheet_url:
            return jsonify({"success": False, "error": "Thiếu spreadsheet_url"}), 400
        
        if fetch_stats:
            kols = process_kol_data(spreadsheet_url, sheet_name)
        else:
            kols = read_kol_data_from_sheets(spreadsheet_url, sheet_name)
        
        return jsonify({
            "success": True,
            "kols": kols,
            "total": len(kols)
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/ranking', methods=['POST'])
def get_kol_ranking_legacy():
    try:
        data = request.json or {}
        spreadsheet_url = data.get('spreadsheet_url', os.environ.get('KOL_SHEET_URL'))
        sheet_name = data.get('sheet_name', 'KOL_management')
        
        if not spreadsheet_url:
            return jsonify({"success": False, "error": "Thiếu spreadsheet_url"}), 400
        
        kols = process_kol_data(spreadsheet_url, sheet_name)
        ranked_kols = rank_kols_by_engagement(kols)
        
        return jsonify({
            "success": True,
            "ranking": ranked_kols,
            "total": len(ranked_kols)
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kol_bp.route('/upload-stats', methods=['POST'])
def upload_kol_stats():
    try:
        data = request.json or {}
        csv_data = data.get('csv_data', '')
        
        if not csv_data:
            return jsonify({"success": False, "error": "Thiếu csv_data"}), 400
        
        import csv
        import io
        from kol_management.manual_stats import save_manual_stats
        
        reader = csv.DictReader(io.StringIO(csv_data))
        count = 0
        
        for row in reader:
            video_url = row.get('video_url', '').strip()
            if not video_url:
                continue
            
            stats = {
                'video_url': video_url,
                'views': int(row.get('views', 0)),
                'likes': int(row.get('likes', 0)),
                'comments': int(row.get('comments', 0)),
                'shares': int(row.get('shares', 0)),
                'saves': int(row.get('saves', 0)),
                'engagement_rate': 0.0
            }
            
            if stats['views'] > 0:
                total_engagement = stats['likes'] + stats['comments'] + stats['shares'] + stats['saves']
                stats['engagement_rate'] = round((total_engagement / stats['views']) * 100, 2)
            
            save_manual_stats(video_url, stats)
            count += 1
        
        return jsonify({
            "success": True,
            "message": f"Đã import {count} video stats",
            "count": count
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
