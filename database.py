import pyrebase
import json 
class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
    def get_user_manners_grade(self, user_id):
        users = self.db.child("user").get()
        if str(users.val()) == "None":
            return None

        for res in users.each():
            value = res.val()
            if value.get('id') == user_id:
                return value.get('manners_grade', 'B+') 
        return None
    def insert_item(self, data, img_path, seller_manners_grade):

        items = self.db.child("item").get().val()

        if not items:
            item_id = "1"
        elif isinstance(items, list):
            item_id = str(len(items))
        else:
            item_id = str(len(items.key()) + 1)

        item_info ={
        "seller": data['id'],
        "phone": data['tel'],
        "addr": data['addr'],
        "trade": data['type'],
        "title": data['item'],
        "price": data['price'],
        "status": data['status'],
        "category": data['category'],
        "explain": data['explain'],
        "img_path": img_path,
        "sale": "Y",
        "seller_manners_grade": seller_manners_grade
        }

        self.db.child("item").child(item_id).set(item_info)
    
        return True
    
    def get_items(self):
        items = self.db.child("item").get().val()
        return items
    
    def get_item_by_id(self, item_id):
        item = self.db.child("item").child(item_id).get().val()
        return item
    
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        print("users###",users.val())
        if str(users.val()) == "None":
            return True
        else:
            for res in users.each():
                value = res.val()
                if value['id'] == id_string:
                    return False
            return True
        
    def insert_user(self, data, pw):
        user_info ={
            "idNum": data['idNum'],   
            "email": data['email'],
            "phoneNum": data['phoneNum'],
            "id": data['id'],
            "pw": pw,
            "manners_grade": "B+"
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False
        
    def find_user(self, id, pw_hash):
        users = self.db.child("user").get()
        if str(users.val()) == "None":
            return False

        for res in users.each():
            value = res.val()
            if value['id'] == id and value['pw'] == pw_hash:
                return value['id']
        
        return False
    def get_user_manners_grade(self, user_id):
        users = self.db.child("user").get()
        if str(users.val()) == "None":
            return None

        for res in users.each():
            value = res.val()
            if value.get('id') == user_id:
                return value.get('manners_grade', 'B+')
        return None
    
    def reg_review(self, data, img_path,reviewer_manners_grade):
        review_info ={
            "item_id": data['item_id'],
            "item_name": data['item_name'],
            "rating": data['rating_input'],
            "title": data['review_title'],
            "content": data['content'],
            "reviewer_id": data['id'],
            "reviewer_manners_grade": reviewer_manners_grade,
            "img_path": img_path
        }   
        self.db.child("review").child(data['item_id']).set(review_info)
        return True
    
    def get_reviews(self):
        reviews = self.db.child("review").get().val()
        if reviews is None:
            return {}
        return reviews
    
    def get_review_by_id(self, item_id):
        review = self.db.child("review").child(item_id).get().val()
        return review
    
    ## 좋아요 상태 조회
    def get_heart_byname(self, uid, item_id):
        # heart/{uid}/{item_id} 전체를 가져옴
        res = self.db.child("heart").child(uid).child(item_id).get()

        if res.val() is None:
            return ""

        return res.val()

    ## 좋아요 추가/취소 : 좋아요 취소 시 데이터베이스에서 해당 항목 제거
    def update_heart(self, user_id, isHeart, item_id, item_title, item_img_path):
        heart_ref = self.db.child("heart").child(user_id).child(item_id)

        if isHeart == "N":
            heart_ref.remove()
            return True

        heart_info = {
            "interested": "Y",
            "title": item_title,
            "img_path": item_img_path
        }
        heart_ref.set(heart_info)
        return True
    
    ## 특정 아이템에 대한 좋아요 수 집계
    def count_hearts_for_item(self, item_id):
        hearts_root = self.db.child("heart").get()
        if hearts_root.val() is None:
            return 0

        count = 0
        for user_node in hearts_root.each():
            user_hearts = user_node.val()
            if user_hearts is None:
                continue

            # user_hearts가 list면 dict로 변환
            if isinstance(user_hearts, list):
                # list 안에 dict가 들어있다고 가정
                user_hearts_dict = {str(i): v for i, v in enumerate(user_hearts) if v}
            else:
                user_hearts_dict = user_hearts

            # item_id에 해당하는 좋아요 정보 가져오기
            heart_info = user_hearts_dict.get(str(item_id))
            if heart_info and heart_info.get("interested") == "Y":
                count += 1
                
        return count
    
    ## 특정 사용자가 좋아요한 아이템 목록 조회
    def get_liked_items_by_user(self, user_id):
        hearts = self.db.child("heart").child(user_id).get()
        if hearts.val() is None:
            return {}

        liked_items = {}
        for item in hearts.each():
            liked_items[item.key()] = item.val()
        
        return liked_items
    def update_item_sale(self, item_id, sale):
        self.db.child("item").child(str(item_id)).update({"sale":sale})
        return True
    
    ## 특정 사용자가 판매한 아이템 목록 조회
    def get_items_by_user_id(self, user_id):
        items = self.db.child("item").get()
        data = items.val()

        # DB가 None일 때
        if not data:
            return {}

        user_items = {}

        for idx, value in enumerate(data):
            if not value:      # None, 빈 값은 건너뛰기
                continue

            # seller가 원하는 user_id와 같을 때만 추가
            if value.get('seller') == user_id:
                user_items[idx] = value  # idx를 key로 사용
        
        return user_items
    
    ## 특정 사용자가 작성한 리뷰 조회
    def get_reviews_by_user(self, user_id):
        reviews = self.db.child("review").get()

        print(">>> Reviews data:", reviews.val())
        if not reviews.val():
            return {}

        result = {}
        print(">>> Checking userid:", user_id)

        for res in reviews.each():
            key = res.key()
            value = res.val()

            # value가 None이면 건너뛰기
            if not value:
                continue

            # reviewer_id가 일치하는지 체크
            
            if value.get('reviewer_id') == user_id:
                result[key] = value

        return result