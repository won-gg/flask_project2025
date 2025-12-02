from flask import Flask, render_template, session
from database import DBhandler
from routes import auth_route, item_route, review_route, user_route

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

application.register_blueprint(auth_route.bp)
application.register_blueprint(item_route.bp)
application.register_blueprint(review_route.bp)
application.register_blueprint(user_route.bp)

@application.route("/")
def hello():
  render_template("index.html", user_id=session.get("id"), user_nickname=session.get("nickname"))
  return item_route.view_list()

if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)