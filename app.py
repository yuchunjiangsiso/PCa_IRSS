# app.py - 主应用文件
from flask import Flask
from owlready2 import get_ontology

app = Flask(__name__)
# ontology_loaded = False  # 状态标志
#
# @app.before_request
# def load_ontology_once():
#     global ontology_loaded
#     if not ontology_loaded:
#         app.extensions['onto'] = get_ontology("prostateCancerOntology.owl").load(reload=True)
#         ontology_loaded = True

# 导入路由模块（确保在本体加载后导入）
from routes.routes import bp
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)