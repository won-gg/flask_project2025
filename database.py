import pyrebase
import json 
class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_item(self, name, data, img_path):
        item_info ={
        "seller": data['seller'],
        "addr": data['addr'],
        "email": data['email'],
        "category": data['category'],
        "card": data['card'],
        "status": data['status'],
        "phone": data['phone'],
        "img_path": img_path
        }
        self.db.child("item").child(name).set(item_info)
        print(data,img_path)
        return True
    
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
            "pw": pw
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
    
    def get_items(self):
        items = self.db.child("item").get().val()
        return items
    
    def reg_review(self, data, img_path):
        review_info ={
            "item_id": data['item_id'],
            "item_name": data['item_name'],
            "rating": data['rating_input'],
            "title": data['review_title'],
            "content": data['content'],
            "reviewer_id": data['id'],
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
    
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value=""
        if hearts.val() == None:
            return target_value
        
        for res in hearts.each():
            key_value = res.key()
            if key_value == name:
                target_value=res.val()
                return target_value
        return target_value

    def update_heart(self, user_id, isHeart, item):
        heart_info ={
            "interested": isHeart
        }
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True
    
    def count_hearts_for_item(self, item_name):
        hearts_root = self.db.child("heart").get()
        if hearts_root.val() is None:
            return 0

        count = 0
        for user_node in hearts_root.each():
            user_hearts = user_node.val()
            if user_hearts is None:
                continue

            heart_info = user_hearts.get(item_name)
            if heart_info and heart_info.get("interested") == "Y":
                count += 1
        return count
