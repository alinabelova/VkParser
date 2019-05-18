import json

class Post(object):
    def __init__(self, id, text, datetime, ownerId, likesCount, repostsCount, commentsCount, viewsCount):
        self.id = id
        self.text = text
        self.datetime = datetime
        self.ownerId = ownerId
        self.likesCount = likesCount
        self.repostsCount = repostsCount
        self.commentsCount = commentsCount
        self.viewsCount = viewsCount
        self.is_positive = True

class PostEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Post):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

def write_posts_json(data, id):
    with open('posts' + id + '.json', 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile, cls=PostEncoder, ensure_ascii=False)

