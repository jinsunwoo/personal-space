from flask import Flask, render_template, url_for, jsonify, request, session, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
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

@app.route('/writeEdit')
def writeEdit():
    # {1: 2} -> d.get(3, 23)
    try:
        _id = request.args["id"]
    except KeyError:
        return "Id not present", 400

    #date = request.args.get("date", "")
    #emotion = request.args.get("emotion", "")
    #words = request.args.get("words", "")
    #print("id from writeedit", _id)
    try:
        diary_entry = list(db.diaries.find({"_id": ObjectId(_id)}))[0]
    except IndexError:
        return f"Id does not exist: {_id}", 400

    date = diary_entry["date"]
    emotion = diary_entry["emotion"]
    words = diary_entry["diary"]

    #breakpoint()
    return render_template('write2.html', date=date, emotion=emotion, words=words,_id=_id)


# /readDiary?date=20200822
# /readDiary?date=20200823

#readDiary?date=


# @app.route('/readDiary')
# def readDiary():
#     return render_template('readDiary.html')
@app.route('/readDiary')
def readDiary():
    diary_id  = request.args.get("diary_id")
    if diary_id:
        return render_template("readDiary2.html", diary_id=diary_id)
    return render_template('readDiary.html')


@app.route('/readAll', methods=['GET'])
def read_all():
    diaries = list(db.diaries.find({}).sort('date', -1))
    #breakpoint()
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
    #print(date_receive)
    #print(emotion_receive)

    diary_doc = {'date': date_receive, 'emotion': emotion_receive, 'diary': diary_receive}

    diary_id = request.form.get("diary_id")

    if not diary_id:
        # mongoDB에 데이터 넣기
        db.diaries.insert_one(diary_doc)
    else:
        print(diary_id, "red", diary_doc)

        #db.diaries.delete_one({{"_id": diary_id}})
        #db.diaries.insert_one(diary_doc)
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
    db.diaries.delete_one({'date': date_receive, 'emotion':emotion_receive})
    return jsonify({'result': 'success'})


@app.route('/editDiary', methods=['POST'])
def editDiary():
    date_receive = request.form['date_give']
    emotion_receive = request.form['emotion_give']
    words_receive = request.form['words_give']
    edit_doc = {'date': date_receive, 'emotion': emotion_receive, 'diary': words_receive}
    db.editDiary.insert_one(edit_doc)
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run('0.0.0.0', port=5000, debug=True)