from urllib import response
from flask import Flask, request_started, url_for,json, jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask_mysqldb import MySQL, MySQLdb
from flask_restful import Resource, Api
import mysql.connector
import keyring
from pymysql import NULL
import requests
pw= keyring.get_password("mysql","root")
web=conn=mysql.connector.connect(host="localhost",password=pw, user="root", database="website",)
app=Flask(__name__,static_folder="static",static_url_path="/",template_folder="templates")
app.secret_key="secret"
api= Api(app)
@app.route("/")
def week6():
    return render_template("week6.html")
@app.route("/member", methods=["GET", "POST"])
def member():
    username= session['username']
    cur= conn.cursor(dictionary=True)
    cur.execute("SELECT*FROM member WHERE username=%s", [username])
    account=cur.fetchone()
    session["username"]="login"
    usname=account['name']
    return render_template("w7member.html", uname=usname)
@app.route("/signout")
def signout():
    session.pop("username", None)
    session.pop('id',None)
    session.pop('loggedin',None)
    session.pop('name',None)
    return render_template("week6.html")
@app.route("/error")
def error():
    message= request.args.get("message")
    if message == "used":
        return render_template("w6usederror.html")
    else:
        return render_template("w6error.html")
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method== 'POST' and 'name' in request.form and 'username' in request.form and 'password' in request.form :
        name= request.form['name']
        username= request.form['username']
        password=request.form['password']
        cur= conn.cursor(dictionary=True)
        cur.execute("SELECT*FROM member WHERE username=%s",(username,))
        account= cur.fetchone()
        if account:
            return redirect(url_for('error', message="used"))
        else:
            cur.execute("INSERT INTO member(name,username,password) VALUES(%s,%s,%s)", (name,username,password))
            conn.commit()
            return redirect(url_for('week6'))
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username= request.form['username']
        password= request.form['password']
        cur= conn.cursor(dictionary=True)
        cur.execute("SELECT*FROM member WHERE username=%s AND password=%s",(username, password,))
        account=cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id']= account['id']
            session['username'] = account['username']
            session['name']= account['name']
            return redirect(url_for('member'))
        else:
            return redirect(url_for('error', message="wrong"))
@app.route("/api/member", methods=["GET", "PATCH"])
def api():
    if  request.method=="GET" and session["username"]=="login":
        name=request.args.get("name")
        cur= conn.cursor(dictionary=True)
        query="SELECT id, name, username FROM member WHERE name=%s"
        cur.execute(query,(name,))
        result= cur.fetchone()
        if result:
                return jsonify({'data':result})
        else:
            return jsonify({'data':NULL})
    elif request.method== "PATCH":
        update=request.get_json("update")
        newname=update['name']
        id=session['id']
        cur=conn.cursor(dictionary=True)
        cur.execute("UPDATE member SET name=%s WHERE id=%s", (newname, id,))
        conn.commit()
        return jsonify({'ok':True})    
    else:
        return jsonify({'error':True})



    
    
       
app.run(port=3000)