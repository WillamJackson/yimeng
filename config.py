import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'S8pdmGjS')
db_address = os.environ.get("MYSQL_ADDRESS", 'sh-cynosdbmysql-grp-fts9hnq6.sql.tencentcdb.com:22267')

# 读取OneThingAI API密钥
api_key = os.environ.get("ONE_THING_AI_API_KEY", 'fd5c8b952a9c2293c1078e7af7f71949')
