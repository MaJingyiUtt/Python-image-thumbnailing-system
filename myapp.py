import os
from flask import Flask, request,send_from_directory,jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
import uuid
import json
import sqlite3

UPLOAD_FOLDER = './uploads'
THUMBNAIL_FOLDER = './thumbnails'

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER


@app.route('/images', methods=['POST'])
def upload_image():
    id = generate_id()
    save_to_bdd(id)
    if request.files :
        image = request.files['image']
        if image.filename!='' and allowed_file(image.filename):
            create_thumbnail(image,id)
            generate_metadata(image,id)
            change_state_in_bdd(id,"success")
        else:
            change_state_in_bdd(id,"failure")
    else:
        change_state_in_bdd(id,"failure")
    return id+"\n"

@app.route('/images-all', methods=['GET'])
def see_all_image_info():
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    result=c.execute("SELECT * FROM images")
    jsondata=[]
    for obj in result:
        jsondata.append(obj)
    conn.close()
    return jsonify(jsondata)

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

def save_to_bdd(id):
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    tab=[id,"pending","",""]
    c.execute("INSERT INTO images VALUES (?,?,?,?)",tab)
    conn.commit()
    conn.close()
    
def change_state_in_bdd(id,state):
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    tab=[state,id]
    c.execute("UPDATE images SET state = ? WHERE id = ?",tab)
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_id():
    return str(uuid.uuid4())

def create_thumbnail(image,id):
    print("create thumbnail")
    size = 128, 128
    im = Image.open(image).convert('RGB')
    im.thumbnail(size)
    im.save(os.path.join(app.config['THUMBNAIL_FOLDER'],id+".jpg"))
    save_link_to_bdd(id)

def save_link_to_bdd(id):
    print("link to bdd")
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    link="/thumbnails/"+id+".jpg"
    tab=[link,id]
    c.execute("UPDATE images SET link = ? WHERE id = ?",tab)
    conn.commit()
    conn.close()


def save_metadata_to_bdd(metadata, id):
    conn=sqlite3.connect("images.db")
    c=conn.cursor()
    tab=[metadata,id]
    c.execute("UPDATE images SET metadata= ? WHERE id = ?",tab)
    conn.commit()
    conn.close()

def generate_metadata(image,id):
    im = Image.open(image)
    exifdata = im.getexif()
    metadata=""
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        metadata+=f"{tag}: {data},"
    save_metadata_to_bdd(metadata,id)