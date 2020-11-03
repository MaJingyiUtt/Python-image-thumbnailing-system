# Python-image-thumbnailing-system

Presentation
------------

* This is a Flask application that provides an API that read uploaded images,
extract its metadata, thumbnails them and make the thumbnail images available
for consumption by the user.

API
---
| Method | Link | Description |
| :------------ | :-------------: | -------------: |
| POST | /images | upload a new image, responds an image ID |
| GET | /images/<id> |  describe image processing state (pending, success, failure) metadata and links to thumbnail  |
| GET | /thumbnails/<id>.jpg | a way to read the generated thumbnail |


