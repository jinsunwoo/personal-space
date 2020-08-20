from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbhomework


## HTML 화면 보기
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

@app.route('/readDiary')
def readDiary():
    return render_template('readDiary.html')



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)