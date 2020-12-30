"""This module is the principle module of this flask application """
import os
import sqlite3
import uuid

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image
from PIL.ExifTags import TAGS

UPLOAD_FOLDER = "./uploads"
THUMBNAIL_FOLDER = "./thumbnails"

ALLOWED_EXTENSIONS = {"jpg"}
THUMBNAIL_WIDTH = 128
THUMBNAIL_HEIGHT = 128

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["THUMBNAIL_FOLDER"] = THUMBNAIL_FOLDER


@app.route("/images", methods=["POST"])
def upload_image():
    """upload image and return an id"""
    image_id = generate_id()
    save_to_bdd(image_id)
    if request.files:
        image = request.files["image"]
        if image.filename != "" and allowed_file(image.filename):
            metadata = generate_metadata(image)
            save_metadata_to_bdd(metadata, image_id)
            create_thumbnail(image, image_id)
            save_link_to_bdd(image_id)
            change_state_in_bdd(image_id, "success")
        else:
            change_state_in_bdd(image_id, "failure")
    else:
        change_state_in_bdd(image_id, "failure")
    return image_id + "\n"


@app.route("/images-all", methods=["GET"])
def see_all_image_info():
    """return all the data of all the images"""
    conn = sqlite3.connect("images.db")
    my_cursor = conn.cursor()
    result = my_cursor.execute("SELECT * FROM images")
    jsondata = []
    for obj in result:
        jsondata.append(obj)
    conn.close()
    return jsonify(jsondata)


@app.route("/images/<image_id>", methods=["GET"])
def see_image_info(image_id):
    """return the data of one image by id"""
    conn = sqlite3.connect("images.db")
    my_cursor = conn.cursor()
    result = my_cursor.execute("SELECT * FROM images WHERE id=?", [image_id])
    jsondata = []
    for obj in result:
        jsondata.append(obj)
    conn.close()
    return jsonify(jsondata)


@app.route("/thumbnails/<idfilename>", methods=["GET"])
def uploaded_file(idfilename):
    """return a thumbnail by id"""
    return send_from_directory(app.config["THUMBNAIL_FOLDER"], idfilename)


def allowed_file(filename):
    """check if the file extention is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_id():
    """generate the image id"""
    return str(uuid.uuid4())


def save_to_bdd(image_id):
    """save id and pending state into the database"""
    conn = sqlite3.connect("images.db")
    my_cursor = conn.cursor()
    tab = [image_id, "pending", "", ""]
    my_cursor.execute("INSERT INTO images VALUES (?,?,?,?)", tab)
    conn.commit()
    conn.close()


def change_state_in_bdd(image_id, state):
    """change the image state to faliure or success by id in the database"""
    conn = sqlite3.connect("images.db")
    my_cursor = conn.cursor()
    tab = [state, image_id]
    my_cursor.execute("UPDATE images SET state = ? WHERE id = ?", tab)
    conn.commit()
    conn.close()


def save_link_to_bdd(image_id):
    """save the thumbnail link to the database by id"""
    conn = sqlite3.connect("images.db")
    my_cursor = conn.cursor()
    link = "/thumbnails/" + image_id + ".jpg"
    tab = [link, image_id]
    my_cursor.execute("UPDATE images SET link = ? WHERE id = ?", tab)
    conn.commit()
    conn.close()


def save_metadata_to_bdd(metadata, image_id):
    """save metadata into the database by id"""
    conn = sqlite3.connect("images.db")
    my_cursor = conn.cursor()
    tab = [metadata, image_id]
    my_cursor.execute("UPDATE images SET metadata= ? WHERE id = ?", tab)
    conn.commit()
    conn.close()


def create_thumbnail(image, image_id):
    """generate a thumbnail and save to the local thumbnails folder"""
    size = THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT
    converted_image = Image.open(image).convert("RGB")
    converted_image.thumbnail(size)
    converted_image.save(
        os.path.join(app.config["THUMBNAIL_FOLDER"], image_id + ".jpg")
    )


def generate_metadata(image):
    """get metadata of the image using Pillow"""
    opened_image = Image.open(image)
    exifdata = opened_image.getexif()
    metadata = ""
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        metadata += f"{tag}: {data},"
    return metadata
