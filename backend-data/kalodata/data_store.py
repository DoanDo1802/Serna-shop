"""
Module quản lý KOL creators với Supabase
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any
import pandas as pd
from supabase_client import get_supabase_client


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return False
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def _pick_value(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record and not _is_missing(record[key]):
            return record[key]
    return None


def _as_string(value: Any) -> str:
    return '' if _is_missing(value) else str(value).strip()


def _as_float(value: Any) -> float:
    if _is_missing(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(',', '').replace('%', '')
    return float(text) if text else 0.0


def _as_int(value: Any) -> int:
    return int(round(_as_float(value)))


def normalize_creator_record(
    record: dict[str, Any],
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    period = _as_string(_pick_value(record, 'period', 'Phạm vi thời gian')).replace('~', ' - ')
    if not period and (start_date or end_date):
        parts = [item for item in [start_date, end_date] if item]
        period = ' - '.join(parts)

    return {
        'period': period,
        'name': _as_string(_pick_value(record, 'name', 'Tên nhà sáng tạo')),
        'followers': _as_int(_pick_value(record, 'followers', 'Lượng theo dõi')),
        'revenue_livestream': _as_float(_pick_value(record, 'revenue_livestream', 'Doanh số livestream(₫)')),
        'revenue_video': _as_float(_pick_value(record, 'revenue_video', 'Doanh số video(₫)')),
        'kalodata_url': _as_string(_pick_value(record, 'kalodata_url', 'Link chi tiết trên Kalodata')),
        'tiktok_url': _as_string(_pick_value(record, 'tiktok_url', 'Link TikTok')),
        'age_range': _as_string(_pick_value(record, 'age_range', 'Độ tuổi người xem')),
        'gender': _as_string(_pick_value(record, 'gender', 'Giới tính người xem')),
        'engagement_rate': _as_float(_pick_value(record, 'engagement_rate', 'Tỷ lệ tương tác')),
    }


def read_creators_from_excel(
    file_path: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """Đọc creators từ Excel file"""
    df = pd.read_excel(file_path)
    creators: list[dict[str, Any]] = []

    for row in df.to_dict('records'):
        creator = normalize_creator_record(row, start_date=start_date, end_date=end_date)
        if creator['name'] or creator['kalodata_url'] or creator['tiktok_url']:
            creators.append(creator)

    return creators


def enrich_creators(creators: list[dict[str, Any]], stats_provider) -> list[dict[str, Any]]:
    """Enrich creators với follower stats"""
    for idx, creator in enumerate(creators):
        print(f"[{idx + 1}/{len(creators)}] Đang lấy stats cho: {creator['name']}")
        if not creator['kalodata_url']:
            continue

        try:
            stats = stats_provider(creator['kalodata_url'])
            if not stats:
                continue

            creator['age_range'] = _as_string(stats.get('top_2_ages'))
            creator['gender'] = _as_string(stats.get('majority_gender'))
            creator['engagement_rate'] = _as_float(stats.get('engagement_rate'))
        except Exception as exc:
            print(f"  ⚠️ Lỗi khi lấy stats: {exc}")

    return creators


def load_saved_payload() -> dict[str, Any]:
    """Load creators từ Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('kalodata_creators').select('*').order('created_at', desc=True).execute()
        
        return {
            'data': response.data,
            'count': len(response.data),
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'last_crawl': None
        }
    except Exception as e:
        print(f"Error loading creators: {e}")
        return {
            'data': [],
            'count': 0,
            'updated_at': None,
            'last_crawl': None
        }


def save_creators_to_supabase(creators: list[dict[str, Any]]) -> dict[str, Any]:
    """Lưu creators vào Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Insert từng creator (bỏ qua duplicate)
        inserted_count = 0
        for creator in creators:
            try:
                supabase.table('kalodata_creators').insert(creator).execute()
                inserted_count += 1
            except Exception as e:
                # Bỏ qua lỗi duplicate
                if 'duplicate' not in str(e).lower() and 'unique' not in str(e).lower():
                    print(f"Error inserting {creator['name']}: {e}")
        
        # Get total count
        total = supabase.table('kalodata_creators').select('id', count='exact').execute()
        
        return {
            'data': creators,
            'count': total.count if total.count else 0,
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'new_count': inserted_count,
            'duplicate_count': len(creators) - inserted_count
        }
    except Exception as e:
        print(f"Error saving creators: {e}")
        raise


def merge_creators_into_store(
    incoming_records: list[dict[str, Any]],
    deduplicate: bool = True,
    last_crawl: dict[str, Any] | None = None,
    duplicate_count_override: int | None = None,
    deduplicate_applied: bool | None = None,
) -> dict[str, Any]:
    """Merge creators vào Supabase"""
    normalized_incoming = [normalize_creator_record(record) for record in incoming_records]
    
    if deduplicate:
        # Filter duplicate trước khi insert
        supabase = get_supabase_client()
        existing = supabase.table('kalodata_creators').select('name, period, kalodata_url').execute()
        
        existing_keys = set()
        for item in existing.data:
            key = f"{item['name']}|{item['period']}|{item.get('kalodata_url', '')}"
            existing_keys.add(key)
        
        fresh_records = []
        duplicate_count = 0
        for record in normalized_incoming:
            key = f"{record['name']}|{record['period']}|{record.get('kalodata_url', '')}"
            if key in existing_keys:
                duplicate_count += 1
            else:
                fresh_records.append(record)
                existing_keys.add(key)
    else:
        fresh_records = normalized_incoming
        duplicate_count = 0
    
    # Insert fresh records
    result = save_creators_to_supabase(fresh_records)
    
    return {
        **result,
        'new_records': fresh_records,
        'new_count': len(fresh_records),
        'duplicate_count': duplicate_count if deduplicate else result.get('duplicate_count', 0),
        'last_crawl': last_crawl
    }


def delete_creators_by_names(names: list[str]) -> dict[str, Any]:
    """Xóa creators theo tên từ Supabase"""
    try:
        supabase = get_supabase_client()
        
        deleted_count = 0
        for name in names:
            try:
                supabase.table('kalodata_creators').delete().eq('name', name).execute()
                deleted_count += 1
            except:
                pass
        
        # Get remaining count
        remaining = supabase.table('kalodata_creators').select('id', count='exact').execute()
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'remaining_count': remaining.count if remaining.count else 0
        }
    except Exception as e:
        print(f"Error deleting creators: {e}")
        return {
            'success': False,
            'deleted_count': 0,
            'error': str(e)
        }


# Backward compatibility - giữ tên hàm cũ
def filter_creators_for_store(
    incoming_records: list[dict[str, Any]],
    existing_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Filter duplicate creators (backward compatibility)"""
    normalized_incoming = [normalize_creator_record(record) for record in incoming_records]
    
    if existing_records is None:
        # Load from Supabase
        payload = load_saved_payload()
        existing_records = payload['data']
    
    existing_keys = set()
    for item in existing_records:
        key = f"{item['name']}|{item['period']}|{item.get('kalodata_url', '')}"
        existing_keys.add(key)
    
    fresh_records = []
    duplicate_count = 0
    for record in normalized_incoming:
        key = f"{record['name']}|{record['period']}|{record.get('kalodata_url', '')}"
        if key in existing_keys:
            duplicate_count += 1
        else:
            fresh_records.append(record)
    
    return {
        'fresh_records': fresh_records,
        'duplicate_count': duplicate_count,
        'normalized_incoming': normalized_incoming,
    }
