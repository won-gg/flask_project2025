from flask import Flask, render_template, request
import sys
application = Flask(__name__)

@application.route("/")
def hello():
  return render_template("index.html")

@application.route("/list")
def view_list():
  return render_template("list.html")
@application.route("/review")
def view_review():
  return render_template("review.html")
@application.route("/reg_items")
def reg_item():
  return render_template("reg_items.html")
@application.route("/reg_reviews")
def reg_review():
  return render_template("reg_reviews.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    # 파일 받기
    image_file = request.files["file"]
    image_path = f"static/images/{image_file.filename}"
    image_file.save(image_path)

    # 폼 데이터 받기
    name = request.form.get("name")
    seller = request.form.get("seller")
    addr = request.form.get("addr")
    email = request.form.get("email")
    category = request.form.get("category")
    card = request.form.get("card")
    status = request.form.get("status")
    phone = request.form.get("phone")

    # 잘 들어왔는지 확인
    print(name, seller, addr, email, category, card, status, phone)

    # 결과 페이지로 넘김
    return render_template(
        "result.html",
        data={
            "name": name,
            "seller": seller,
            "addr": addr,
            "email": email,
            "category": category,
            "card": card,
            "status": status,
            "phone": phone,
        },
        img_path=image_path
    )

if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)