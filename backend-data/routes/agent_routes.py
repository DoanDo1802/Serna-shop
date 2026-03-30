from flask import Blueprint, request, jsonify
import traceback
from agent.agent import suggest_filters as agent_suggest_filters

agent_bp = Blueprint('agent_routes', __name__, url_prefix='/api/agent')

@agent_bp.route('/suggest', methods=['POST'])
def agent_suggest():
    try:
        data = request.json or {}
        description = data.get('description', '')
        price = data.get('price', '')
        image_base64 = data.get('image')
        image_url = data.get('image_url')

        if not description:
            return jsonify({"success": False, "error": "Vui lòng nhập mô tả sản phẩm"}), 400

        result = agent_suggest_filters(
            description=description,
            price=price,
            image_base64=image_base64,
            image_url=image_url,
        )

        return jsonify({"success": True, **result}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
