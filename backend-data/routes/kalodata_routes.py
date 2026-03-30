from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import traceback

from kalodata.data_store import (
    enrich_creators,
    filter_creators_for_store,
    load_saved_payload,
    merge_creators_into_store,
    read_creators_from_excel,
    delete_creators_by_names,
)
from kalodata.exp_playwright_api import export_kalodata_data
from kalodata.upload_sheets import upload_excel_to_gsheet

kalodata_bp = Blueprint('kalodata_routes', __name__, url_prefix='/api/kalodata')

@kalodata_bp.route('/export', methods=['POST'])
def export_kalodata():
    try:
        data = request.json or {}
        crawl_params = {
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'revenue_min': data.get('revenue_min', 50000000),
            'revenue_max': data.get('revenue_max', 100000000),
            'age_range': data.get('age_range', '25-34'),
            'page_size': data.get('page_size', 10),
            'enrich': data.get('enrich', False),
            'deduplicate': data.get('deduplicate', True),
            'filters': data.get('filters', {}),
        }

        file_path = export_kalodata_data(
            start_date=crawl_params['start_date'],
            end_date=crawl_params['end_date'],
            revenue_min=crawl_params['revenue_min'],
            revenue_max=crawl_params['revenue_max'],
            age_range=crawl_params['age_range'],
            page_size=crawl_params['page_size'],
            filters=crawl_params['filters'],
        )
        
        creators = read_creators_from_excel(
            file_path,
            start_date=crawl_params['start_date'],
            end_date=crawl_params['end_date'],
        )

        duplicate_count = 0
        if crawl_params['deduplicate']:
            filter_result = filter_creators_for_store(creators)
            creators = filter_result['fresh_records']
            duplicate_count = filter_result['duplicate_count']
            print(f"🛡️ Đã lọc trùng trước enrich: bỏ qua {duplicate_count} KOL, còn {len(creators)} KOL mới.")
        
        if crawl_params['enrich'] and creators:
            print(f"\n🔍 Đang enrich dữ liệu cho {len(creators)} KOLs...")
            from kalodata.datakoc import get_follower_stats
            creators = enrich_creators(creators, get_follower_stats)

        persist_result = merge_creators_into_store(
            creators,
            deduplicate=False,
            last_crawl={
                'file_path': file_path,
                'ran_at': datetime.utcnow().isoformat() + 'Z',
                'params': crawl_params,
            },
            duplicate_count_override=duplicate_count,
            deduplicate_applied=crawl_params['deduplicate'],
        )
        
        return jsonify({
            "success": True, 
            "file_path": file_path,
            **persist_result,
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kalodata_bp.route('/data', methods=['GET'])
def get_saved_kalodata():
    try:
        payload = load_saved_payload()
        return jsonify({"success": True, **payload}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@kalodata_bp.route('/delete', methods=['POST'])
def delete_kalodata():
    try:
        data = request.json or {}
        names = data.get('names', [])
        
        if not names or not isinstance(names, list):
            return jsonify({"success": False, "error": "Danh sách names không hợp lệ"}), 400
        
        result = delete_creators_by_names(names)
        return jsonify(result), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@kalodata_bp.route('/upload', methods=['POST'])
def upload_kalodata():
    try:
        data = request.json
        excel_path = data.get('excel_path')
        sheet_url = data.get('google_sheet_url', os.environ.get('GOOGLE_SHEET_URL'))
        sheet_name = data.get('sheet_name', 'Sheet1')
        
        if not excel_path or not sheet_url:
            return jsonify({"success": False, "error": "Thiếu excel_path hoặc google_sheet_url"}), 400
        
        upload_excel_to_gsheet(excel_path, sheet_url, sheet_name)
        return jsonify({"success": True, "message": "Đã upload thành công"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
