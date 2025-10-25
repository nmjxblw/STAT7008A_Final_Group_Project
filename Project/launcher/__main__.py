"""启动模块"""

import flask

launcher_app = flask.Flask("launcher_app")
"""flask应用实例"""

if __name__ == "__main__":
    launcher_app.run()
