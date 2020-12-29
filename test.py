import unittest
import myapp

import sqlite3

class TestMethods(unittest.TestCase):
    @staticmethod
    def create_line_in_bdd(id):
        conn=sqlite3.connect("images.db")
        c=conn.cursor()
        tab=[id,"pending","",""]
        c.execute("INSERT INTO images VALUES (?,?,?,?)",tab)
        conn.commit()
        conn.close()

    @staticmethod
    def delete_line_in_bdd(id):
        conn=sqlite3.connect("images.db")
        c=conn.cursor()
        tab=[id]
        c.execute("DELETE FROM images WHERE id = ?",tab)
        conn.commit()
        conn.close()
    
    def test_allowed_file(self):
        self.assertTrue(myapp.allowed_file("filename.jpg"))
        self.assertFalse(myapp.allowed_file("filename.png"))
    
    def test_generate_id(self):
        # self.assertNotEqual(len(myapp.generate_id()),0)
        self.assertIsNotNone(myapp.generate_id)

    def test_save_to_bdd(self):
        id="id_for_test_1"
        myapp.save_to_bdd(id)
        conn=sqlite3.connect("images.db")
        c=conn.cursor()
        tab=[id]
        result=c.execute("SELECT * from images WHERE id=?",tab)
        jsondata=[]
        for obj in result:
            jsondata.append(obj)
        conn.close()
        print(jsondata[0][1])
        self.assertEqual(jsondata[0][1],"pending")
        self.delete_line_in_bdd(id)
    
    def test_change_state_in_bdd(self):
        id="id_for_test_2"
        self.create_line_in_bdd(id)
        myapp.change_state_in_bdd(id,"success")
        conn=sqlite3.connect("images.db")
        c=conn.cursor()
        tab=[id]
        result=c.execute("SELECT * from images WHERE id=?",tab)
        jsondata=[]
        for obj in result:
            jsondata.append(obj)
        conn.close()
        print(jsondata)
        self.assertEqual(jsondata[0][1],"success")
        self.delete_line_in_bdd(id)
    
    def test_save_link_to_bdd(self):
        id="id_for_test_3"
        self.create_line_in_bdd(id)
        myapp.save_link_to_bdd(id)
        conn=sqlite3.connect("images.db")
        c=conn.cursor()
        tab=[id]
        result=c.execute("SELECT * from images WHERE id=?",tab)
        jsondata=[]
        for obj in result:
            jsondata.append(obj)
        conn.close()
        print(jsondata)
        self.assertEqual(jsondata[0][2],"/thumbnails/"+id+".jpg")
        self.delete_line_in_bdd(id)

    def test_save_metadata_to_bdd(self):
        id="id_for_test_4"
        self.create_line_in_bdd(id)
        myapp.save_metadata_to_bdd("metadata_for_test",id)
        conn=sqlite3.connect("images.db")
        c=conn.cursor()
        tab=[id]
        result=c.execute("SELECT * from images WHERE id=?",tab)
        jsondata=[]
        for obj in result:
            jsondata.append(obj)
        conn.close()
        print(jsondata)
        self.assertEqual(jsondata[0][3],"metadata_for_test")
        self.delete_line_in_bdd(id)
    
