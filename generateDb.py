import json
import sqlite3

conn=sqlite3.connect("images.db")
c=conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS images (id text,state text,link text,metadata text)")

conn.commit()
for row in c.execute('SELECT * FROM images'):
    print(row)

conn.close()
