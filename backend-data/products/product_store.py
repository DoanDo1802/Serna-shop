"""
Module quản lý sản phẩm - CRUD operations với Supabase
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any
from supabase_client import get_supabase_client


def get_all_products() -> dict[str, Any]:
    """Lấy tất cả sản phẩm từ Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('products').select('*').order('created_at', desc=True).execute()
        
        return {
            'products': response.data,
            'count': len(response.data),
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        print(f"Error getting products: {e}")
        return {
            'products': [],
            'count': 0,
            'updated_at': None
        }


def get_product_by_id(product_id: str) -> dict[str, Any] | None:
    """Lấy sản phẩm theo ID từ Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting product: {e}")
        return None


def create_product(product_data: dict[str, Any]) -> dict[str, Any]:
    """Tạo sản phẩm mới trong Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Tạo ID mới
        product_data['id'] = str(int(datetime.utcnow().timestamp() * 1000))
        product_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Insert vào Supabase
        response = supabase.table('products').insert(product_data).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        raise Exception("Failed to create product")
    except Exception as e:
        print(f"Error creating product: {e}")
        raise


def update_product(product_id: str, product_data: dict[str, Any]) -> dict[str, Any] | None:
    """Cập nhật sản phẩm trong Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Không cho phép update id và created_at
        product_data.pop('id', None)
        product_data.pop('created_at', None)
        
        # Update trong Supabase (trigger sẽ tự động set updated_at)
        response = supabase.table('products').update(product_data).eq('id', product_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error updating product: {e}")
        raise


def delete_product(product_id: str) -> bool:
    """Xóa sản phẩm từ Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('products').delete().eq('id', product_id).execute()
        
        return response.data is not None
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False


def delete_multiple_products(product_ids: list[str]) -> dict[str, Any]:
    """Xóa nhiều sản phẩm từ Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Supabase không hỗ trợ delete với IN, phải xóa từng cái
        deleted_count = 0
        for product_id in product_ids:
            try:
                supabase.table('products').delete().eq('id', product_id).execute()
                deleted_count += 1
            except:
                pass
        
        # Đếm số sản phẩm còn lại
        remaining = supabase.table('products').select('id', count='exact').execute()
        
        return {
            'deleted_count': deleted_count,
            'remaining_count': remaining.count if remaining.count else 0
        }
    except Exception as e:
        print(f"Error deleting products: {e}")
        return {
            'deleted_count': 0,
            'remaining_count': 0
        }
