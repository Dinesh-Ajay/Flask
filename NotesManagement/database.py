import mysql.connector
db=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='notes_app'
)
cursor = db.cursor()
