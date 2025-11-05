from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

## 상품 임시 데이터 8개 (list.html & item_detail.html 사용)
item_data = {
    1: {'title': '100년 된 헤드셋', 'category': 'digitals', 'price': 10000, 'image_path': 'images/item-list/item-img1.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '100주년 기념으로 기존에 사용하던 제품 싸게 판매합니다. 소리 잘 들리고 상태 좋습니다.', 'seller': 'ewhaosp1'},
    2: {'title': 'WONDER', 'category': 'books', 'price': 5000, 'image_path': 'images/item-list/item-img2.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '읽으려고 샀는데 손이 안 가서 판매합니다. 거의 새 책입니다.', 'seller': 'ewhaosp2'},
    3: {'title': '검은색 버뮤다 팬츠', 'category': 'clothes', 'price': 10000, 'image_path': 'images/item-list/item-img3.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '한두 번 입은 바지입니다. 상태 아주 좋습니다.', 'seller': 'ewhaosp3'},
    4: {'title': '고양이 마스킹 테이프', 'category': 'etc', 'price': 4000, 'image_path': 'images/item-list/item-img4.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '처분하려고 팝니다. 마스킹 테이프 걸어둔 것까지 통째로 판매합니다. 반 정도 사용했습니다.', 'seller': 'ewhaosp4'},
    5: {'title': '국제법_김영석 저', 'category': 'books', 'price': 30000, 'image_path': 'images/item-list/item-img5.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '작년 수업 시간에 사용한 교재입니다. 중요한 부분에 필기 있습니다. 오히려 도움이 될 수도 있습니다.', 'seller': 'ewhaosp5'},
    6: {'title': 'LG GRAM', 'category': 'digitals', 'price': 200000, 'image_path': 'images/item-list/item-img6.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '새 노트북 구매로 기존 사용하던 노트북 판매합니다. 전원 이상 없고 화면에 키보드 자국 조금 남아있습니다. 카메라도 잘 작동됩니다.', 'seller': 'ewhaosp6'},
    7: {'title': '아이폰 5s', 'category': 'digitals', 'price': 30000, 'image_path': 'images/item-list/item-img7.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '배터리 고장으로 전원이 안 들어옵니다. 바로 사용은 어렵고, A/S 후 사용 가능할 듯 싶습니다. 싸게 판매합니다.', 'seller': 'ewhaosp7'},
    8: {'title': '폴로 랄프 로렌 바람막이', 'category': 'clothes', 'price': 120000, 'image_path': 'images/item-list/item-img8.jpg', 'fee': 0, 'trade': 'direct', ''
        'description': '온라인 구매했는데 제 생각보다 얇아서 판매합니다. 택 붙어있는 거진 새 상품입니다.', 'seller': 'ewhaosp8'},
}

@application.route("/")
def hello():
  return render_template("index.html")
@application.route("/login")
def login():
  return render_template("login.html")
@application.route("/signup")
def signup():
  return render_template("signup.html")
@application.route("/signup_post", methods=['POST'])
def register_user():
  data=request.form
  pw=request.form['pw']
  pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
  if DB.insert_user(data,pw_hash):
    return render_template("login.html")
  else:
    flash("user id already exist!")
    return render_template("signup.html")
@application.route("/list")
def view_list():
  return render_template("list.html", items=item_data)

@application.route("/item_detail")
def view_item_detail():
  item_id = request.args.get('id', 1, type=int)
  item = item_data.get(item_id, item_data[1]) 

  return render_template(
    "item_detail.html",
    title=item['title'],
    category=item['category'].capitalize(),
    price=item['price'],
    image_path=item['image_path'],
    fee=item['fee'],
    trade=item['trade'],
    description=item['description'],
    seller=item['seller']
  )
@application.route("/review")
def view_review():
  return render_template("review.html")
@application.route("/reg_items")
def reg_item():
  return render_template("reg_items.html")
@application.route("/reg_reviews")
def reg_review():
  return render_template("reg_reviews.html")

@application.route("/submit_item")
def reg_item_submit():
  name=request.args.get("name")
  seller=request.args.get("seller")
  addr=request.args.get("addr")
  email=request.args.get("email")
  category=request.args.get("category")
  card=request.args.get("card")
  status=request.args.get("status")
  phone=request.args.get("phone")

  print(name,seller,addr,email,category,card,status,phone)
  return render_template("reg_items.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    # 파일 받기
    image_file = request.files["file"]
    image_path = f"static/images/{image_file.filename}"
    image_file.save(image_path)
    data = request.form

    DB.insert_item(data['name'], data, image_file.filename)

    return render_template("result.html", data= data, img_path = "static/images/{}".format(image_file.filename))

if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)