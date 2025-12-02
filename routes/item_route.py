from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler

bp = Blueprint('item', __name__)
DB = DBhandler()

@bp.route("/reg_items")
def reg_item():
  if 'id' not in session:
        flash("상품을 등록하려면 로그인이 필요합니다.")
        return redirect(url_for('auth.login'))
  
  user_id = session.get('id')
  user_phone = session.get('phoneNum')

  seller_manners_grade = DB.get_user_manners_grade(user_id)

  return render_template("reg_items.html", user_id=user_id, user_phone = user_phone, seller_manners_grade=seller_manners_grade)

@bp.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    if 'id' not in session:
        flash("상품을 등록하려면 로그인이 필요합니다.")
        return redirect(url_for('auth.login'))
    
    image_files = request.files.getlist("file") #파일 여러 장 받기
    image_paths = [] 

    for file in image_files:
        if file.filename != '':
            file.save("static/images/{}".format(file.filename))
            image_paths.append(file.filename)

    data = request.form

    seller_id = session.get('id')
    seller_manners_grade = DB.get_user_manners_grade(seller_id)

    
    DB.insert_item(data, image_paths, seller_manners_grade)

    return redirect(url_for('item.view_list'))

## 상품 리스트 페이지 + 검색 기능 추가
@bp.route("/list")
def view_list():
    page = request.args.get("page",0,type=int)
    cat = (request.args.get("cat", "all") or "all").lower().strip()
    q = (request.args.get("q", "") or "").lower().strip()
    per_page=8
    per_row=4
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)

    data = DB.get_items()

    if data is None:
        data = {}
    elif isinstance(data, list):
            new_data = {}
            for i, item in enumerate(data):
                if item is not None:
                    new_data[str(i)] = item
            data = new_data
    
    all_data_items = list(data.items())

    # 필터링: 카테고리 및 검색어
    if cat != "all" or q != "":
        filtered_items = []
        for iid, it in all_data_items:
            item_cat = str(it.get("category", "")).lower().strip()
            item_name = str(it.get("title", "")).lower()
            item_desc = str(it.get("explain", "")).lower()

            if (cat == "all" or item_cat == cat):   # 카테고리 조건
                if (q == "" or q in item_name or q in item_desc):  # 검색 조건
                    filtered_items.append((iid, it))
    else:
        filtered_items = all_data_items

    filtered_count = len(filtered_items)
    current_page_items = filtered_items[start_idx:end_idx]

    data = dict(current_page_items)
    tot_count = len(data)
    for i in range(row_count):
        if (i==row_count -1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])

    data = {}
    for iid, it in current_page_items:
        heart_cnt = DB.count_hearts_for_item(iid)
        it['heart_count'] = heart_cnt
        data[iid] = it


    return render_template(
        "list.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page = page,
        page_count=int((filtered_count/per_page)+1),
        cat=cat,
        total=filtered_count,
        q=q,
    )


@bp.route("/item_detail")
def view_item_detail():
  item_id = request.args.get('id', type=int)

  item = DB.get_item_by_id(item_id) 

  heart_cnt = DB.count_hearts_for_item(str(item_id))
  image_list = item.get("img_path", [])

  seller_grade = item.get("seller_manners_grade", "A+")
  return render_template(
    "item_detail.html",
    image_list=image_list,
    item_id=item_id,
    title=item['title'],
    category=item['category'].capitalize(),
    price=item['price'],
    image_path=item['img_path'],
    fee=2500, #택배 기본값
    trade=item['trade'],
    description=item['explain'],
    seller=item['seller'],
    heart_cnt=heart_cnt,
    sale=item.get('sale', 'Y'),
    seller_manners_grade=seller_grade,
  )

# 판매 완료 기능
@bp.route("/purchase/<item_id>/", methods=['POST'])
def purchase_item(item_id):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    item = DB.get_item_by_id(item_id)
    if item.get("sale") == "N":
        return jsonify({'error': '이미 판매 완료된 상품입니다.'}), 400
    DB.update_item_sale(item_id, "N")

    return jsonify({'msg': '구매 완료!'})
