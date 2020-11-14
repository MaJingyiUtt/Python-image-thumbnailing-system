import os
from flask import Flask, request,send_from_directory,jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import json
import sqlite3

UPLOAD_FOLDER = './uploads'
THUMBNAIL_FOLDER = './thumbnails'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER


@app.route('/images', methods=['POST'])
def upload_image():
    id = generate_id()
    state="failure"
    if request.files :
        image = request.files['image']
        if image.filename!='' and allowed_file(image.filename):
            state="pending"
            create_thumbnail(image,id)
    saveStateToBdd(id,state)
    return id+"\n"

@app.route('/images/<id>', methods=['GET'])
def see_image_info(id):
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    result=c.execute("SELECT * FROM images WHERE id=?",[id])
    jsondata=[]
    for obj in result:
        jsondata.append(obj)
    conn.close()
    return jsonify(jsondata)

@app.route('/thumbnails/<idfilename>', methods=['GET'])
def uploaded_file(idfilename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'],idfilename)

def saveStateToBdd(id,state):
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    tab=[id,state,""]
    c.execute("INSERT INTO images VALUES (?,?,?)",tab)
    conn.commit()
    for row in c.execute('SELECT * FROM images'):
        print(row)
    conn.close()

def saveMetadataToBdd(id):
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    link="/thumbnails/"+id+".jpg"
    tab=["success",link,id]
    c.execute("UPDATE images SET state = ? AND link = ? WHERE id = ?",tab)
    conn.commit()
    for row in c.execute('SELECT * FROM images'):
        print(row)
    conn.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_id():
    return str(uuid.uuid4())

def create_thumbnail(image,id):
    size = 128, 128
    im = Image.open(image).convert('RGB')
    im.thumbnail(size)
    im.save(os.path.join(app.config['THUMBNAIL_FOLDER'],id+".jpg"))
    saveMetadataToBdd(id)


