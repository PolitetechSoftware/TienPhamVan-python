import sqlite3

# connect to database
conn = sqlite3.connect('metrics_collection.db')
 
# create cursor object
cur = conn.cursor()