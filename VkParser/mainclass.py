from PyQt5 import QtWidgets 
from mydesign import Ui_MainWindow  # importing our generated file 
import sys
import requests
import json
from time import sleep
import time
import csv

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
        parse_group(group_id, date_start)

def write_json(data):
    with open('posts.json', 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
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
    data = {
        'id': post_id,
        'datetime': time.strftime("%d.%m.%Y, %H:%M:%S", time.localtime(post['date'])),
        'likes': post_likes,
        'text': post['text'],
        'comments': comments,
        'reposts': reposts
        }
    return data

def parse_group(group, date_start):
    group_id = '-' + group
    #group_id = '-34183390'
    offset = 0
    all_posts = []

    while True:
        sleep(1)
        r = requests.get('https://api.vk.com/method/wall.get', params={'owner_id': group_id, 'offset': offset, 'count': 100, 'access_token': 'd933e827d933e827d933e82762d95bd7acdd933d933e827857a5be3f0d490a5fdc7bfbe', 'v': '5.92'})
        posts = r.json()['response']['items']
        all_posts.extend(posts)
        oldest_post_date = posts[-1]['date']
        offset += 100
        if oldest_post_date < date_start:
            break
    data_posts = []
    write_csv_headers()
    for post in all_posts:
        post_data = get_data(post)
        write_csv(post_data)

    print(len(all_posts))
  #  write_json(r.json())

#if __name__ == '__main__':
 #   main()


app = QtWidgets.QApplication([])
 
application = mywindow()
 
application.show()
 
sys.exit(app.exec())