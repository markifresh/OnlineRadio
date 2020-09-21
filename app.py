from application import create_app
from config import DevConfig

cur_conf = DevConfig
app = create_app(cur_conf)

if __name__ == "__main__":
    app.run(host=cur_conf.HOST)