from flask import Blueprint, request, jsonify
import traceback
from products.product_store import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    delete_multiple_products,
)

product_bp = Blueprint('product_routes', __name__, url_prefix='/api/products')

@product_bp.route('', methods=['GET'])
def get_products():
    try:
        result = get_all_products()
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = get_product_by_id(product_id)
        if product:
            return jsonify({"success": True, "product": product}), 200
        else:
            return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@product_bp.route('', methods=['POST'])
def add_product():
    try:
        data = request.json or {}
        if not data.get('name') or not data.get('price'):
            return jsonify({"success": False, "error": "Thiếu tên hoặc giá sản phẩm"}), 400
        
        product = create_product(data)
        return jsonify({"success": True, "product": product}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@product_bp.route('/<product_id>', methods=['PUT'])
def edit_product(product_id):
    try:
        data = request.json or {}
        if not data.get('name') or not data.get('price'):
            return jsonify({"success": False, "error": "Thiếu tên hoặc giá sản phẩm"}), 400
        
        product = update_product(product_id, data)
        if product:
            return jsonify({"success": True, "product": product}), 200
        else:
            return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@product_bp.route('/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    try:
        success = delete_product(product_id)
        if success:
            return jsonify({"success": True, "message": "Đã xóa sản phẩm"}), 200
        else:
            return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@product_bp.route('/batch-delete', methods=['POST'])
def batch_delete_products():
    try:
        data = request.json or {}
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({"success": False, "error": "Danh sách IDs trống"}), 400
        
        result = delete_multiple_products(ids)
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
