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
  #  data = {
   #     id: post_id,
   #     datetime: time.strftime("%d.%m.%Y, %H:%M:%S", time.localtime(post['date'])),
   #     likes: post_likes,
    #    text: post['text'],
     #   comments: comments,
      #  reposts: reposts
       # }
  
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

def parse_group(group):
    group_id = '-' + group
   # group_id = '-34183390'
    offset = 0
    all_posts = []

 #   while True:
   #     sleep(1)
    r = requests.get('https://api.vk.com/method/wall.get', params={'owner_id': group_id, 'offset': offset, 'count': 4, 'access_token': 'd933e827d933e827d933e82762d95bd7acdd933d933e827857a5be3f0d490a5fdc7bfbe', 'v': '5.92'})
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
    matrix = []
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
            keyword = KeyWord(data_post.id, result, 1)
        else:
            keyword = KeyWord(data_post.id, result, -1)
        keywords.append(keyword)
 
    
    for data_post in data_posts:
        count = 0
        for k in keywords:
            if k.word in data_post.text:
                count += k.is_positive
        if count < 0:
            data_post.is_positive = False
    return keywords
      #    print (vectorizer.vocabulary_)
 #   print ((X.todense())) 
  #  vocab = np.array(vectorizer.get_feature_names())
   # print ("Document term matrix:")
    #chunk_names = ['Chunk-0', 'Chunk-1', 'Chunk-2', 'Chunk-3']
    #formatted_row = '{:>12}' * (len(chunk_names) + 1)
    #print ('\n', formatted_row.format('Word', *chunk_names), '\n')

  #  for word, item in zip(vocab, X.T) :
   #     output = [str(x) for x in item.data]
       # print(formatted_row.format(word, *output))


if __name__ == '__main__':
    common_keywords = []
    common_keywords.extend(parse_group('34183390')) #https://vk.com/public34183390
    common_keywords.extend(parse_group('54767216')) #https://vk.com/kraschp
    common_keywords.extend(parse_group('59804801')) #https://vk.com/krsk_overhear

    # now print the results
    print("\n===Keywords===")
    for k in common_keywords:
      print(k.post_id)
      print(k.word)
#app = QtWidgets.QApplication([])
 
#application = mywindow()
 #application.show()
 #sys.exit(app.exec())