from flask import Flask, render_template, url_for, jsonify, request, session, redirect
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbpspace1 # dbpersonalspace 라는 이름의 db 만듬


# HTML 화면 보기
@app.route('/')
def loginpage():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/main')
def main():
     return render_template('main.html')


@app.route('/write')
def write():
    return render_template('write.html')


# /readDiary?date=20200822
# /readDiary?date=20200823

#readDiary?date=


# @app.route('/readDiary')
# def readDiary():
#     return render_template('readDiary.html')
@app.route('/readDiary')
def readDiary():
    return render_template('readDiary.html')


@app.route('/readAll', methods=['GET'])
def read_all():
    diaries = list(db.diaries.find({}, {'_id': False}).sort('date', -1))
    #print(diaries)
    return jsonify({'result': 'success', 'diaries': diaries})


@app.route('/saveDiary', methods=['POST'])
def save_diary():
    # 클라이언트에서 date, emotion, diary 데이터 받기
    date_receive = request.form['date_give']
    emotion_receive = request.form['emotion_give']
    diary_receive = request.form['diary_give']
    #print(date_receive)
    #print(emotion_receive)

    diary_doc = {'date': date_receive, 'emotion': emotion_receive, 'diary': diary_receive}

    # mongoDB에 데이터 넣기
    db.diaries.insert_one(diary_doc)

    return jsonify({'result': 'success'})


@app.route('/deleteDiary', methods=['POST'])
def delete_diary():
    date_receive = request.form['date_give']
    emotion_receive = request.form['emotion_give']
    # words_receive = request.form['words_give']

    print(date_receive)
    print(emotion_receive)
    # print(words_receive)
    db.diaries.delete_one({'date': date_receive, 'emotion':emotion_receive})
    return jsonify({'result': 'success'})



if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run('0.0.0.0', port=5000, debug=True)