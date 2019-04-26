from PyQt5 import QtWidgets 
from mydesign import Ui_MainWindow  # importing our generated file 
import sys
#from post import post
import requests
import json
from time import sleep
import time
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from stop_words import get_stop_words
import numpy as np
from concepts import Context

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

class KeyWord(object):
    def __init__(self, post_id, word, is_positive):
        self.post_id = post_id
        self.word = word
        self.is_positive = is_positive

class mywindow(QtWidgets.QMainWindow): 
    def __init__(self):
 
        super(mywindow, self).__init__()
 
        self.ui = Ui_MainWindow()
    
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.btnClicked) # connecting the clicked signal with btnClicked slot
 
    def btnClicked(self): 
        self.ui.label.setText("Button Clicked")
        search_phrases = self.ui.textEdit.toPlainText()
        group_id = self.ui.lineEdit.text()
        date_start = self.ui.dateTimeEdit.dateTime().toMSecsSinceEpoch()
        parse_group('34183390', date_start) #https://vk.com/public34183390
        parse_group('54767216', date_start) #https://vk.com/kraschp
        parse_group('59804801', date_start) #https://vk.com/krsk_overhear

def write_json(data, id):
    with open('posts' + id + '.json', 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile, cls=PostEncoder, ensure_ascii=False)
  #  with open('posts.json', 'w', encoding="utf-8") as file:
   #     json.dump(data, file, indent=2, ensure_ascii=False)
def write_csv_headers():
    with open('posts_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(('Id',
                         'DateTime',
                         'Comments',
                         'Likes',
                         'Reposts',                         
                         'Text'
                         ))

def write_csv(data):
    with open('posts_data.csv', 'a', newline='', encoding="windows-1251") as file:
        writer = csv.writer(file)
        writer.writerow((data['id'],
                         data['datetime'],     
                         data['comments'],
                         data['likes'],
                         data['reposts'],
                         data['text'].replace('\n','')                      
                         ))

def get_data(post):
    try:
        post_id = post['id']
    except:
        post_id = 0
    try:
        post_likes = post['likes']['count']
    except:
        post_likes = 0
    try:
        comments = post['comments']['count']
    except:
        comments = 0
    try:
        reposts = post['reposts']['count']
    except:
        reposts = 0
    try:
        views = post['views']['count']
    except:
        views = 0
    data = Post(post_id, post['text'], time.strftime("%d.%m.%Y, %H:%M:%S", time.localtime(post['date'])), post['owner_id'], post_likes, reposts, comments, views)
    return data


 
def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)
 
def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""
    
    #use only topn items from vector
    sorted_items = sorted_items[:topn]
 
    score_vals = []
    feature_vals = []
    
    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
 
    #create a tuples of feature,score
    #results = zip(feature_vals,score_vals)
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    
    return results

def average_concept_like(concepts, data_posts):
    for concept in concepts:
        like_avg = sum([data_post.likesCount for data_post in data_posts if data_post.id in concept[0]]) / len(concept[0])
        print(like_avg)

def get_formal_concepts(data_posts, keywords):
    matrix = []
    obj = []
    attributes = list(set([x.word for x in keywords]))
    for data_post in data_posts:
        count = 0
        obj.append(data_post.id)
        for k in attributes:
            if k.lower() in data_post.text.lower():
                t = [x for x in matrix if x[0][0]  == data_post.id]
                if not t:
                    matrix.append(([data_post.id], [k]))
                else:
                    t = (t[0][0], t[0][1].append(k))
        if False:            
       # if count < 0:
            data_post.is_positive = False
            for a, *b in matrix:
                print(a, ' '.join(map(str, b)))
    for i in range(len(matrix)):        
        for j in range(i + 1, len(matrix)):
            crossing = sorted(list(set(matrix[i][1]) & set(matrix[j][1])))
            if not crossing:
                continue
            tt = [x for x in matrix if crossing == sorted(x[1])]
            if tt:
                if matrix[i][0][0] not in tt[0][0]:
                    tt[0][0].append(matrix[i][0][0])
                if matrix[j][0][0] not in tt[0][0]:
                    tt[0][0].append(matrix[j][0][0])
                tt = (tt[0][0], crossing)
            else:
                matrix.append(([matrix[i][0][0], matrix[j][0][0]], crossing))
    
    average_concept_like(matrix, data_posts)
    all_attributes = [x for x in matrix if sorted(attributes) == sorted(x[1])]
    all_objects = [x for x in matrix if sorted(obj) == sorted(x[1])]
    if not all_attributes:
        matrix.append(([], attributes))
    if not all_objects:
        matrix.append((obj, []))
    matrix = sorted(matrix, key=lambda x: len(x[0]))

    file1 = open("concepts.txt","a") 
    for m in matrix:
        print(m)
        file1.write(str(m) + '\n')
    file1.close()


def parse_group(group):
    group_id = '-' + group
   # group_id = '-34183390'
    offset = 0
    all_posts = []

 #   while True:
   #     sleep(1)
    r = requests.get('https://api.vk.com/method/wall.get', params={'owner_id': group_id, 'offset': offset, 'count': 30, 'access_token': 'd933e827d933e827d933e82762d95bd7acdd933d933e827857a5be3f0d490a5fdc7bfbe', 'v': '5.95'})
    posts = r.json()['response']['items']
    all_posts.extend(posts)
  #      oldest_post_date = posts[-1]['date']
  #      offset += 100
  #      if oldest_post_date < date_start:
   #         break
    data_posts = []
   #  write_csv_headers()
    for p in all_posts:
        data_posts.append(get_data(p))
    #    post_data = get_data(post)
  #       write_csv(post_data)

    write_json(data_posts, group_id)
  #  corpus = ["This is very strange",
 #         "This is very nice"]
    my_stop_words = get_stop_words('ru')

    vectorizer = TfidfVectorizer(ngram_range=(1,1), stop_words=my_stop_words)
   # vectorizer = CountVectorizer()
    X = vectorizer.fit_transform([data_post.text for data_post in data_posts])
    idf = vectorizer.idf_
    #print (dict(zip(vectorizer.get_feature_names(), idf)))
   
   #***************

    cv=CountVectorizer(max_df=0.85,stop_words=my_stop_words,max_features=10000)
    word_count_vector=cv.fit_transform([data_post.text for data_post in data_posts])
    tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True)
    tfidf_transformer.fit(word_count_vector)
    feature_names=cv.get_feature_names()
    #all keywords 
    keywords = []
    
    #generate tf-idf for the given document
    for data_post in data_posts:
        tf_idf_vector=tfidf_transformer.transform(cv.transform([data_post.text]))
        #sort the tf-idf vectors by descending order of scores
        sorted_items=sort_coo(tf_idf_vector.tocoo()) 
        #extract only the top n; n here is 1
        results = extract_topn_from_vector(feature_names,sorted_items,1)
        result = ''
        if results:
            result = next(iter(results))
        if result != '':
            keyword = KeyWord(data_post.id, result, 1)
            keywords.append(keyword)
 
   
    
    obj = ['g1', 'g2', 'g3', 'g4']
    atr = ['m1', 'm2', 'm3', 'm4']
    matrixTest = []
    aMat = [[ 0 for i in range(4)] for j in range(4)]
    aMat[0][2] = 1
    aMat[0][3] = 1

    aMat[1][1] = 1
    aMat[1][2] = 1

    aMat[2][0] = 1
    aMat[2][3] = 1

    aMat[3][0] = 1
    aMat[3][1] = 1
    aMat[3][2] = 1

    for i in range(len(aMat)):
        atri = []
        for j in range(len(aMat[i])):
            if aMat[i][j] == 1:
                atri.append(atr[j])
        matrixTest.append(([obj[i]], atri))

        #list(set(matrixTest[1][1]) & set(matrixTest[3][1]))
    resultMatrix = []
    

    matrixTestB = []
    for j in range(len(aMat[0])):
        obji = []
        for i in range(len(aMat)):
            if aMat[i][j] == 1:
                obji.append(obj[i])
        matrixTestB.append((atr[j], obji))
        
    c = Context.fromstring('''
  |m1   |m2    |m3   |m4        |
g1|  X  |      |  X  |   X      |
g2|  X  |  X   |  X  |          |
g3|  X  |      |     |     X    |
g4|  X  |   X  |  X  |    X     |
''')
  #  print(c.intension(['King Arthur', 'Sir Robin']))
  #  print(c.extension(['knight', 'mysterious']))
   # for extent, intent in c.lattice:
  #      print('%r %r' % (extent, intent))
    return data_posts, keywords

if __name__ == '__main__':
    common_keywords = []
    data_posts = []
    common_keywords.extend(parse_group('34183390')[1]) #https://vk.com/public34183390
    data_posts.extend(parse_group('34183390')[0]) #https://vk.com/public34183390

    common_keywords.extend(parse_group('54767216')[1]) #https://vk.com/kraschp
    data_posts.extend(parse_group('54767216')[0]) #https://vk.com/public34183390

    common_keywords.extend(parse_group('59804801')[1]) #https://vk.com/krsk_overhear
    data_posts.extend(parse_group('59804801')[0]) #https://vk.com/public34183390

    get_formal_concepts(data_posts, common_keywords)

#app = QtWidgets.QApplication([])
 
#application = mywindow()
 #application.show()
 #sys.exit(app.exec())