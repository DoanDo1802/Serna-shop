"""
Backend API cho hệ thống quản lý KOL
Cung cấp các endpoint để:
- Lấy dữ liệu KOL từ Kalodata
- Lấy video TikTok
- Gửi tin nhắn TikTok tự động
"""
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Thêm thư mục gốc vào path để import modules
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# ==================== REGISTER BLUEPRINTS ====================
from routes.kalodata_routes import kalodata_bp
app.register_blueprint(kalodata_bp)

from routes.tiktok_routes import tiktok_bp
app.register_blueprint(tiktok_bp)

from routes.product_routes import product_bp
app.register_blueprint(product_bp)

from routes.cookie_routes import cookie_bp
app.register_blueprint(cookie_bp)

from routes.kol_routes import kol_bp
app.register_blueprint(kol_bp)

from routes.agent_routes import agent_bp
app.register_blueprint(agent_bp)

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái server"""
    return jsonify({"status": "ok", "message": "Backend đang hoạt động"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
