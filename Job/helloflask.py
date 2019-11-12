# coding: utf-8

from flask import *
app = Flask(__name__)

@app.route('/', methods=["GET","POST"])
def hello_world():
    if request.method=='POST':
        if request.files:
            for f in request.files:
                f = request.files[f]
                f.save('exam/'+f.filename)
        else:
            print('No files')
    return "Hello, World!\n"

if __name__ == '__main__':
    app.run()