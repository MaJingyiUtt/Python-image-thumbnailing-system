import os
from flask import Flask, request,send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

UPLOAD_FOLDER = './uploads'
THUMBNAIL_FOLDER = './thumbnails'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER


@app.route('/images', methods=['POST'])
def upload_image():
    if request.method=="POST":

        if request.files :

            image = request.files['image']

            if image.filename=='':
                return 'Image must have a filename\n'
                
            if not allowed_file(image.filename):
                return "Only "+str(ALLOWED_EXTENSIONS)+" extensions are allowed\n"
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                id = generate_id()
                create_thumbnail(image,id)
                return filename+" and its thumbnail "+id+".jpg are saved ! \n"

@app.route('/thumbnails/<idfilename>', methods=['GET'])
def uploaded_file(idfilename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'],idfilename)

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