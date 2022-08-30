import sys, os
import mysql.connector
import pandas as pd
import bcrypt
import passwords

def connectDB(database):
    config = {
        'user' : 'mtpBackups',
        'password' : 'notPassword234!',
        'host' : '192.168.25.18',
        'database' : f'{database}'
    }
    db = mysql.connector.connect(**config)
    return db

def insertDB(params):
    name=str(params[0])
    if name == "chanel-rubrik-0":
        name = name.replace("-", "", 2)
    total=int(params[1])
    used=int(params[2])
    try:
        db = connectDB('mtpBackups')
        cursor = db.cursor()
        query = ("INSERT INTO {} (Total, Used) VALUES (%s, %s)".format(name))
        vals = (total, used)
        cursor.execute(query, vals)
        db.commit()
        db.close()
    except mysql.connector.Error as err:
        print(err)

def selectDB(table):
    try:
        table = str(table)
        db = connectDB('mtpBackups')
        cursor = db.cursor()
        query = f"SELECT DATE_FORMAT(dateTime, '%m-%d-%Y'), totalGB, totalOBJ FROM {table}"
        cursor.execute(query)
        result = cursor.fetchall()
        db.close()
        return result
    except mysql.connector.Error as err:
        print(err)

def selectDBWithBucket(table):
    try:
        table = str(table)
        db = connectDB('mtpBackups')
        cursor = db.cursor()
        query = f"SELECT DATE_FORMAT(dateTime, '%m-%d-%Y'), totalGB, totalOBJ, bucket FROM {table}"
        cursor.execute(query)
        result = cursor.fetchall()
        db.close()
        return result
    except mysql.connector.Error as err:
        print(err)

def insert_account(user, hash):
    try:
        db = connectDB('users')
        cursor = db.cursor()
        query = f"INSERT INTO logins (Username, Hash) VALUES (%s, %s)"
        values = (user, hash)
        cursor.execute(query, values)
        db.commit()
        db.close()
        print('Success')
    except mysql.connector.Error as err:
        print(err)

def select_acc():
    try:
        db = connectDB('users')
        cursor = db.cursor()
        query = f"SELECT Username, Hash FROM logins"
        cursor.execute(query)
        result = cursor.fetchall()
        db.close()
        return result
    except mysql.connector.Error as err:
        print(err)
        
def change_pw(user, pw):
    try:
        db = connectDB('users')
        cursor = db.cursor()
        pw_d = passwords.hash_pw(pw).decode('utf-8')
        login_info = (pw_d, user)
        query = f"UPDATE logins SET Hash = (%s) WHERE Username = (%s)"
        cursor.execute(query, login_info)
        result = cursor.fetchall()
        db.commit()
        db.close()
        return result
    except mysql.connector.Error as err:
        print(err)
    
    # "UPDATE logins SET Hash = 'hi' WHERE Username = 'nextiva'"






