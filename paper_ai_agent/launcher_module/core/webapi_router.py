import flask


def create_webapi_router(app: flask.Flask) -> flask.Blueprint:
    """创建WebAPI路由蓝图"""
    webapi_router = flask.Blueprint("webapi_router", __name__)

    @webapi_router.route("/api/status", methods=["GET"])
    def get_status():
        """获取系统状态的API接口"""
        return flask.jsonify({"status": "running", "message": "系统运行正常"})

    # 在此处添加更多的API路由

    return webapi_router
