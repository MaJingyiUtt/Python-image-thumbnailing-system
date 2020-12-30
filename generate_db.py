"""This module is for creating the database of the flask applicaiton"""
import sqlite3

conn = sqlite3.connect("images.db")
c = conn.cursor()
# uncomment the line below and run this file to recreate the database
# c.execute("DROP TABLE IF EXISTS images")
c.execute(
    "CREATE TABLE IF NOT EXISTS images ( \
    id text PRIMARY KEY, \
    state text,link text, \
    metadata text)"
)

conn.commit()
# print all the lines in the database
for row in c.execute("SELECT * FROM images"):
    print(row)

conn.close()
