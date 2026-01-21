from flask import Flask, request, jsonify, render_template
import json
import threading
import os
from device_control import (
    get_devices,
    switch_device,
    run_yanghao,
    stop_yanghao,
    device_status,
    get_default_config
)
from config_manager import ConfigManager

app = Flask(__name__, template_folder='templates', static_folder='static')

# 初始化配置管理器
config_manager = ConfigManager("config/config.json")
current_device = {"device_id": None}

# ==================== 页面路由 ====================
@app. route("/")
def index():
    """主页仪表板"""
    return render_template("index.html")

@app.route("/device")
def device_page():
    """设备管理页面"""
    return render_template("device.html")

@app.route("/keyword")
def keyword_page():
    """关键词管理页面"""
    return render_template("keyword. html")

@app.route("/param")
def param_page():
    """核心参数页面"""
    return render_template("param.html")

@app.route("/visit")
def visit_page():
    """访问控制页面"""
    return render_template("visit.html")

@app.route("/interact")
def interact_page():
    """互动配置页面"""
    return render_template("interact.html")

@app.route("/status")
def status_page():
    """状态监控页面"""
    return render_template("status.html")

# ==================== API 接口 ====================

@app.route("/api/devices", methods=["GET"])
def api_devices():
    """获取已连接设备列表"""
    try:
        devices = get_devices()
        return jsonify({"success": True, "data": devices})
    except Exception as e:
        return jsonify({"success": False, "error":  str(e)})

@app.route("/api/device/switch", methods=["POST"])
def api_device_switch():
    """切换设备"""
    try: 
        device_id = request.json.get("device_id")
        if not device_id: 
            return jsonify({"success":  False, "error": "设备ID不能为空"})
        
        # 如果有其他设备在运行，先停止
        if current_device["device_id"]:
            stop_yanghao(current_device["device_id"])
        
        result = switch_device(device_id)
        if result: 
            current_device["device_id"] = device_id
            # 初始化新设备配置（如无则复制默认配置）
            if not config_manager.get_config(device_id):
                default_cfg = get_default_config()
                config_manager.save_config(device_id, default_cfg)
            return jsonify({"success": True, "message": f"已切换到设备:  {device_id}"})
        else:
            return jsonify({"success": False, "error":  "设备连接失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/config/<device_id>", methods=["GET"])
def api_get_config(device_id):
    """获取设备配置"""
    try:
        config = config_manager.get_config(device_id)
        if not config:
            config = get_default_config()
        return jsonify({"success":  True, "data": config})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/config/<device_id>", methods=["PUT"])
def api_save_config(device_id):
    """保存设备配置"""
    try:
        config = request.json
        config_manager.save_config(device_id, config)
        return jsonify({"success": True, "message": "配置已保存"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/config/keywords/<device_id>", methods=["GET", "PUT"])
def api_keywords(device_id):
    """管理关键词"""
    try:
        if request.method == "GET": 
            config = config_manager.get_config(device_id)
            keywords = config.get("keywords", []) if config else []
            return jsonify({"success": True, "data": keywords})
        else:
            keywords = request.json.get("keywords", [])
            config = config_manager.get_config(device_id)
            config["keywords"] = keywords
            config_manager.save_config(device_id, config)
            return jsonify({"success": True, "message": "关键词已更新"})
    except Exception as e:
        return jsonify({"success": False, "error":  str(e)})

# ==================== 养号控制 ====================

@app.route("/api/yanghao/start", methods=["POST"])
def api_start_yanghao():
    """启动养号"""
    try: 
        device_id = request. json.get("device_id") or current_device["device_id"]
        if not device_id:
            return jsonify({"success": False, "error": "未选择设备"})
        
        config = config_manager.get_config(device_id)
        if not config:
            return jsonify({"success": False, "error": "配置不完整"})
        
        if not config.get("keywords"):
            return jsonify({"success": False, "error": "请先添加搜索关键词"})
        
        # 启动养号线程
        threading.Thread(
            target=run_yanghao,
            args=(device_id, config),
            daemon=True
        ).start()
        
        return jsonify({"success": True, "message": "养号已启动"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/yanghao/stop", methods=["POST"])
def api_stop_yanghao():
    """停止养号"""
    try: 
        device_id = request.json.get("device_id") or current_device["device_id"]
        if not device_id: 
            return jsonify({"success": False, "error": "未选择设备"})
        
        stop_yanghao(device_id)
        return jsonify({"success": True, "message": "已停止养号"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/yanghao/status/<device_id>")
def api_status(device_id):
    """获取养号状态"""
    try:
        status = device_status(device_id)
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/config/default", methods=["GET", "PUT"])
def api_default_config():
    """管理默认配置模板"""
    try:
        if request.method == "GET": 
            default_cfg = config_manager.get_default_template()
            return jsonify({"success": True, "data": default_cfg})
        else:
            cfg = request.json
            config_manager.set_default_template(cfg)
            return jsonify({"success":  True, "message": "默认模板已更新"})
    except Exception as e:
        return jsonify({"success": False, "error":  str(e)})

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "请求不存在"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": "服务器错误"}), 500

if __name__ == '__main__':
    # 确保配置文件存在
    os.makedirs("config", exist_ok=True)
    if not os.path.exists("config/config.json"):
        with open("config/config.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
    
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)