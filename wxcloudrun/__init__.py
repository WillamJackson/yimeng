from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import config
from flask_migrate import Migrate

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化web应用
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG

# 设定数据库链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/yimeng'.format(config.username, config.password,
                                                                             config.db_address)

# 初始化DB操作对象
db = SQLAlchemy(app)
migrate = Migrate()

# 加载控制器
from wxcloudrun.comfyui import comfyui_views
from wxcloudrun.users import user_views

# 加载配置
app.config.from_object('config')
