#!/usr/bin/python/
#-*-coding:utf-8-*-



from flask import Flask, request, render_template, make_response
import MySQLdb
import hashlib
app = Flask(__name__)



@app.route('/index.html',methods=['GET'])
@app.route('/',methods=['GET'])
def db():
    db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
    cursor = db.cursor()
    cursor.execute("SELECT count(*) from mezun")
    mezun_sayisi = cursor.fetchone()
    cursor.execute("SELECT count(*) from firma")
    firma_sayisi = cursor.fetchone()
    return render_template('index.html', mezun=mezun_sayisi[0], firma=firma_sayisi[0])


@app.route('/contact.html',methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route('/mezun_ara', methods=['GET', 'POST'])
def show_post():
    if request.method == 'POST':
        ogrenci_no1 = str(request.form['ogrenci_no'])
        page_number = str(request.form['page_number'])
        page_number=int(page_number)-1
    if request.method == 'GET':
        ogrenci_no1=0
        page_number=0


    db = MySQLdb.connect("localhost","misafir","misafir","mebsis" ,charset='utf8', init_command='SET NAMES UTF8')
    cursor = db.cursor()
    if(int(ogrenci_no1) == 0):
        cursor.execute("SELECT *  from mezun LIMIT "+ str(page_number*20)+",20;")
    else:
        page_number=0
        cursor.execute("SELECT *  from mezun where ogrenci_no='"+ogrenci_no1+"' LIMIT "+ str(page_number*20)+",20;")
    cursor.fetchall()
    rows = []
    for row in cursor:
        rows.append(row)
    current_page = int(page_number)
    cursor.execute("SELECT count(*) from mezun;")
    page_number = cursor.fetchone()
    page_number = page_number[0]  ## Düzelt
    page_number = int(page_number) / 20
    if current_page<5:
        low_limit=0
        high_limit=current_page+5
    else:
        low_limit=current_page-4
        high_limit=current_page+5
    return render_template('elements.html', data=rows, len=len(rows), page_number=page_number,current_page=current_page,
 low_limit=low_limit, high_limit=high_limit)

@app.route('/login', methods = ['POST'])
def login():
    error = ''
    # Error ekle.
    username = request.form['username']
    password = request.form['password']
    db = MySQLdb.connect("localhost","misafir","misafir", "mebsis", charset='utf8', init_command='SET NAMES UTF8')
    cursor = db.cursor()
    cursor.execute("SELECT password from password where ogrenci_no_fk="+str(username)+";")
    result = cursor.fetchone()

    if(str(result[0]) == hashlib.md5(password.encode()).hexdigest()):
        response =  make_response(render_template('index.html'))
        response.set_cookie('username', username)
        response.set_cookie('password', str(result[0]))
    return response

@app.route('/anasayfa')
def anasayfa():
    return

##  Anasayfaya yönlendirecek. Başkalarının ilanı görülecek. İlanları ekle. İlan yorumları, özel mesajlar. bitti gitti


if __name__ == '__main__':
    app.run()
