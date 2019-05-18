from PyQt5 import QtWidgets 
from mydesign import Ui_MainWindow  # importing our generated file 
import sys
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
from colour import Color
import graphviz as gv
from post import *
from like import *
from post_keyword import KeyWord

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
    for index, concept in enumerate(concepts):
        like_avg = 0
        if len(concept[0]) > 0:          
            like_avg = sum([data_post.likesCount for data_post in data_posts if data_post.id in concept[0]]) / len(concept[0])
        concept_list = list(concept)
        concept_list.append(like_avg)
        concepts[index] = tuple(concept_list)
        print(like_avg)
    return concepts

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
    
    
    all_attributes = [x for x in matrix if sorted(attributes) == sorted(x[1])]
    all_objects = [x for x in matrix if sorted(obj) == sorted(x[1])]
    if not all_attributes:
        matrix.append(([], attributes))
    if not all_objects:
        matrix.append((obj, []))
    matrix = average_concept_like(matrix, data_posts)
    matrix = sorted(matrix, key=lambda x: len(x[1]))
    d = gv.Digraph(
        directory=None, edge_attr=dict(dir='none', labeldistance='1.5', minlen='2'))
    red = Color("red")
    colors = list(red.range_to(Color("green"), len(matrix)))
    file1 = open("concepts.txt","a") 
    for m in matrix:
        print(m)
        file1.write(str(m) + '\n')
    file1.close()
    
    matrixForGraph = []
    for tup in matrix:
        if len([x for x in matrixForGraph if x[1] == tup[1]]) == 0:
           matrixForGraph.append(tup)
    matrixForGraph = sorted(matrixForGraph, key=lambda x: x[2])
    
    i = 0
    for m in matrixForGraph:   
        nodename = ', '.join([str(x) for x in m[1]])
        if matrixForGraph[0] == m:
            node_label = ' '
        else:
            node_label = nodename
        d.node(nodename, node_label, color=colors[i].hex_l, style='filled')
        t = [x for x in matrixForGraph if set(m[1]).issubset(x[1]) and len(m[1]) < len(x[1])]
        if len(t) > 0:
            all_neighbours = sorted(t, key=lambda x: len(x[1]))
            nearest_neighbours = [x for x in all_neighbours if len(x[1]) == len(all_neighbours[0][1])]
          
            for neighbour in nearest_neighbours:
               node_name2 = ', '.join([str(x) for x in neighbour[1]])               
               d.edges([(node_label, node_name2)])
        i += 1
    d.view()

def parse_group(group):
    group_id = '-' + group
    offset = 0
    all_posts = []

    r = requests.get('https://api.vk.com/method/wall.get', params={'owner_id': group_id, 'offset': offset, 'count': 10, 'access_token': 'd933e827d933e827d933e82762d95bd7acdd933d933e827857a5be3f0d490a5fdc7bfbe', 'v': '5.95'})
    posts = r.json()['response']['items']
    all_posts.extend(posts)

    data_posts = []
    likes_response = []
    all_likes = []

    for p in all_posts:
        data_posts.append(get_data(p))
        r = requests.get('https://api.vk.com/method/likes.getList', 
                         params={'owner_id': group_id, 'offset': offset, 'type': 'post', 'item_id': p['id'],
                                 'filter': 'likes', 'friends_only': 0, 'extended': 1, 'count': p['likes']['count'],
                                 'access_token': 'd933e827d933e827d933e82762d95bd7acdd933d933e827857a5be3f0d490a5fdc7bfbe', 'v': '5.95'})
        likes_response.extend(r.json()['response']['items'])
        
    for like_response in likes_response:
        like = Like(group_id, like_response['id'], like_response['type'],
                    like_response['first_name'], like_response['last_name'])
        all_likes.append(like)
    write_likes_json(all_likes, group_id)

    write_posts_json(data_posts, group_id)
    my_stop_words = get_stop_words('ru')

    vectorizer = TfidfVectorizer(ngram_range=(1,1), stop_words=my_stop_words)
    X = vectorizer.fit_transform([data_post.text for data_post in data_posts])
    idf = vectorizer.idf_
   
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