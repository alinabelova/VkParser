import json

class Like(object):
    def __init__(self, post_id, account_id, type, first_name, last_name):
        self.post_id = post_id
        self.account_id = account_id
        self.type = type
        self.first_name = first_name
        self.last_name = last_name

class LikeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Like):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

def write_likes_json(data, id):
    with open('likes' + id + '.json', 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile, cls=LikeEncoder, ensure_ascii=False)