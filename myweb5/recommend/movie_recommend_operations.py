from django.db import connection
import pymysql

def insert(user_id, movie_id):
    cursor = connection.cursor()
    cursor.execute("SELECT movie_id FROM movie_recommend WHERE user_id ="+str(user_id))
    data = cursor.fetchall()
    if len(data)>0:
        for m_id in data:
            if int(movie_id) in m_id:
                print("Already exist")
                return
    cursor.execute("INSERT INTO movie_recommend VALUES(NULL,"+str(user_id)+", "+str(movie_id)+")")
    return "success"

def delete(user_id, movie_id):
    cursor = connection.cursor()
    cursor.execute("SELECT movie_id FROM movie_recommend WHERE user_id =" + str(user_id))
    data = cursor.fetchall()
    if len(data)>0:
        for m_id in data:
            if int(movie_id) in m_id:
                print("yes")
                cursor.execute("DELETE FROM movie_recommend WHERE movie_id = " + str(movie_id))
                return "success"
    print("Not exist")
    return

def show(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT movie_id FROM movie_recommend WHERE user_id =" + str(user_id))
    data = cursor.fetchall()
    mylist = []
    if len(data)>0:
        for m_id in data:
            mylist.append(m_id[0])
    return mylist

