import os
from flask import Flask, request,send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                return "Image saved, ID = "+"\n"
