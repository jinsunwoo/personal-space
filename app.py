from flask import Flask, render_template, url_for, jsonify, request, session, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.ps2  # dbpersonalspace 라는 이름의 db 만듬

SECRET_KEY = 'apple'
import jwt
import datetime
import hashlib


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


@app.route('/writeEdit')
def writeEdit():
    # {1: 2} -> d.get(3, 23)
    try:
        _id = request.args["id"]
    except KeyError:
        return "Id not present", 400

    # date = request.args.get("date", "")
    # emotion = request.args.get("emotion", "")
    # words = request.args.get("words", "")
    # print("id from writeedit", _id)
    try:
        diary_entry = list(db.diaries.find({"_id": ObjectId(_id)}))[0]
    except IndexError:
        return "Id does not exist: {_id}", 400

    date = diary_entry["date"]
    emotion = diary_entry["emotion"]
    words = diary_entry["diary"]

    print(words)

    # breakpoint()
    return render_template('write2.html', date=date, emotion=emotion, words=words, _id=_id)


# /readDiary?date=20200822
# /readDiary?date=20200823

# readDiary?date=


# @app.route('/readDiary')
# def readDiary():
#     return render_template('readDiary.html')
@app.route('/readDiary')
def readDiary():
    diary_id = request.args.get("diary_id")
    if diary_id:
        return render_template("readDiary2.html", diary_id=diary_id)
    return render_template('readDiary.html')


@app.route('/readAll', methods=['GET'])
def read_all():
    diaries = list(db.diaries.find({}).sort('date', -1))
    # breakpoint()
    print(diaries)
    diaries = [{key: str(value) if key == "_id" else value for key, value in diary.items()} for diary in diaries]
    print(diaries)
    return jsonify({'result': 'success', 'diaries': diaries})


@app.route("/readOne/<path:diary_id>", methods=["GET"])
def read_one(diary_id):
    diary_id = ObjectId(diary_id)

    try:
        diary = list(db.diaries.find({"_id": diary_id}))[0]
        diaries = [diary]
        diaries = [{key: str(value) if key == "_id" else value for key, value in diary.items()} for diary in diaries]
    except IndexError:
        diaries = [{}]

    return jsonify({'result': 'success', 'diaries': diaries})


@app.route('/saveDiary', methods=['POST'])
def save_diary():
    # 클라이언트에서 date, emotion, diary 데이터 받기
    date_receive = request.form['date_give']
    emotion_receive = request.form['emotion_give']
    diary_receive = request.form['diary_give']
    # print(date_receive)
    # print(emotion_receive)
    diary_doc = {'date': date_receive, 'emotion': emotion_receive, 'diary': diary_receive}

    diary_id = request.form.get("diary_id")

    if not diary_id:
        # mongoDB에 데이터 넣기
        db.diaries.insert_one(diary_doc)
    else:
        print(diary_id, "red", diary_doc)

        # db.diaries.delete_one({{"_id": diary_id}})
        # db.diaries.insert_one(diary_doc)
        diary_id = ObjectId(diary_id)
        db.diaries.update_one({"_id": diary_id}, {"$set": diary_doc})

    return jsonify({'result': 'success'})


@app.route('/deleteDiary', methods=['POST'])
def delete_diary():
    date_receive = request.form['date_give']
    emotion_receive = request.form['emotion_give']
    # words_receive = request.form['words_give']

    # print(date_receive)
    # print(emotion_receive)
    # print(words_receive)
    db.diaries.delete_one({'date': date_receive, 'emotion': emotion_receive})
    return jsonify({'result': 'success'})


@app.route('/editDiary', methods=['POST'])
def editDiary():
    date_receive = request.form['date_give']
    emotion_receive = request.form['emotion_give']
    words_receive = request.form['words_give']
    edit_doc = {'date': date_receive, 'emotion': emotion_receive, 'diary': words_receive}
    db.editDiary.insert_one(edit_doc)
    return jsonify({'result': 'success'})


# register part
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash})
    return jsonify({'result': 'success'})


# log in part
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # encode pw
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # find user with id and pw
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
    print('print result: ', result)

    # if found, make jwt
    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # give out token
        return jsonify({'result': 'success', 'token': token})
    # if not found
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/userid', methods=['GET'])
def api_valid():
    # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
    # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
    token_receive = request.headers['token_give']

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'userID': userinfo['id']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run('0.0.0.0', port=5000, debug=True)
