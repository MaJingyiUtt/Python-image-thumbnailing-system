"""This module is for pytest of myapp.py"""
import os
import sqlite3
import unittest

from PIL import Image

import myapp


class TestMethods(unittest.TestCase):
    """This class is for unit test"""

    @staticmethod
    def create_line_in_bdd(image_id):
        """This function creates one line for testing in the database"""
        conn = sqlite3.connect("images.db")
        my_cursor = conn.cursor()
        tab = [image_id, "pending", "", ""]
        my_cursor.execute("INSERT INTO images VALUES (?,?,?,?)", tab)
        conn.commit()
        conn.close()

    @staticmethod
    def delete_line_in_bdd(image_id):
        """This function deletes the line created for testing in the database"""
        conn = sqlite3.connect("images.db")
        my_cursor = conn.cursor()
        tab = [image_id]
        my_cursor.execute("DELETE FROM images WHERE id = ?", tab)
        conn.commit()
        conn.close()

    def test_allowed_file(self):
        """Tests if the allowed_file function workes fine"""
        # jpg is allowed
        self.assertTrue(myapp.allowed_file("filename.jpg"))
        # png is not allowed
        self.assertFalse(myapp.allowed_file("filename.png"))

    def test_generate_id(self):
        """Tests if the image id is well generated"""
        self.assertIsNotNone(myapp.generate_id)

    def test_save_to_bdd(self):
        """Tests if save_to_bdd works well"""
        image_id = "id_for_test_1"
        myapp.save_to_bdd(image_id)
        conn = sqlite3.connect("images.db")
        my_cursor = conn.cursor()
        tab = [image_id]
        result = my_cursor.execute("SELECT * from images WHERE id=?", tab)
        jsondata = []
        for obj in result:
            jsondata.append(obj)
        conn.close()
        self.assertEqual(jsondata[0][1], "pending")
        self.delete_line_in_bdd(image_id)

    def test_change_state_in_bdd(self):
        """Tests if change_state_in_bdd works well"""
        image_id = "id_for_test_2"
        self.create_line_in_bdd(image_id)
        myapp.change_state_in_bdd(image_id, "success")
        conn = sqlite3.connect("images.db")
        my_cursor = conn.cursor()
        tab = [image_id]
        result = my_cursor.execute("SELECT * from images WHERE id=?", tab)
        jsondata = []
        for obj in result:
            jsondata.append(obj)
        conn.close()
        # check state is changed to success
        self.assertEqual(jsondata[0][1], "success")
        self.delete_line_in_bdd(image_id)

    def test_save_link_to_bdd(self):
        """Tests if save_link_to_bdd works well"""
        image_id = "id_for_test_3"
        self.create_line_in_bdd(image_id)
        myapp.save_link_to_bdd(image_id)
        conn = sqlite3.connect("images.db")
        my_cursor = conn.cursor()
        tab = [image_id]
        result = my_cursor.execute("SELECT * from images WHERE id=?", tab)
        jsondata = []
        for obj in result:
            jsondata.append(obj)
        conn.close()
        # check link
        self.assertEqual(jsondata[0][2], "/thumbnails/" + image_id + ".jpg")
        self.delete_line_in_bdd(image_id)

    def test_save_metadata_to_bdd(self):
        """Tests if save_metadata_to_bdd works well"""
        image_id = "id_for_test_4"
        self.create_line_in_bdd(image_id)
        myapp.save_metadata_to_bdd("metadata_for_test", image_id)
        conn = sqlite3.connect("images.db")
        my_cursor = conn.cursor()
        tab = [image_id]
        result = my_cursor.execute("SELECT * from images WHERE id=?", tab)
        jsondata = []
        for obj in result:
            jsondata.append(obj)
        conn.close()
        # check metadata
        self.assertEqual(jsondata[0][3], "metadata_for_test")
        self.delete_line_in_bdd(image_id)

    def test_create_thumbnail(self):
        """Tests if create_thumbnail works well"""
        image_id = "id_for_test_5"
        myapp.create_thumbnail("test.jpg", image_id)
        image_path = os.path.join(
            myapp.app.config["THUMBNAIL_FOLDER"], image_id + ".jpg"
        )
        image = Image.open(image_path)
        width, height = image.size
        self.assertLessEqual(width, myapp.THUMBNAIL_WIDTH)
        self.assertLessEqual(height, myapp.THUMBNAIL_HEIGHT)
        # remove the thumbnail created by this test
        if os.path.exists(image_path):
            os.remove(image_path)

    def test_generate_metadata(self):
        """Tests if generate_metadata works well"""
        result = myapp.generate_metadata("test.jpg")
        self.assertIsNotNone(result)

    def test_upload_image(self):
        """Tests if post /images works well"""
        image = "test.jpg"
        data = {"image": (open(image, "rb"), image)}
        with myapp.app.test_client() as test_client:
            response = test_client.post("/images", data=data)
            self.assertEqual(response.status_code, 200)

    def test_images_all(self):
        """Tests if get /images-all works well"""
        with myapp.app.test_client() as test_client:
            response = test_client.get("/images-all", json={})
            self.assertEqual(response.status_code, 200)

    def test_images_by_id(self):
        """Tests if get /images/<image_id> works well"""
        image_id = "id_for_test_6"
        self.create_line_in_bdd(image_id)
        with myapp.app.test_client() as test_client:
            response = test_client.get("/images/" + image_id)
            self.assertEqual(response.status_code, 200)
        self.delete_line_in_bdd(image_id)

    def test_thumbnails(self):
        """Tests if get /thumbnails/<idfilename> works well"""
        with myapp.app.test_client() as test_client:
            response = test_client.get("/thumbnails/test_thumbnail.jpg")
            self.assertEqual(response.status_code, 200)
