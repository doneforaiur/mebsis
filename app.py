from flask import Flask, render_template, request,redirect
import MySQLdb
app = Flask(__name__)


@app.route('/index.html',methods=['GET'])
def index():
	return redirect('/')

@app.route('/',methods=['GET'])
def db():
    db = MySQLdb.connect("localhost","root","ameleevrim1","mebsis" )

    cursor = db.cursor()

    cursor.execute("SELECT count(*) from mezun")
    cursor.fetchall()
    rows = []

    for row in cursor:
        rows.append(row)
        ##print(row)

    return render_template('index.html', data=rows[0][0])



@app.route('/contact.html',methods=['GET'])
def contact():
	return render_template('contact.html')
	
@app.route('/mezun.html',methods=['GET'])
def mezun():
    db = MySQLdb.connect("localhost","root","ameleevrim1","mebsis" )

    cursor = db.cursor()

    cursor.execute("SELECT ogrenci_no,isim, soyad,firma_no_fk from mezun")
    ##cursor.fetchall()
    rows = []

    for row in cursor:
        rows.append(row)
        ##print(row)
    print(len(rows))
    return render_template('elements.html', data=rows, len=len(rows))

if __name__ == '__main__':
    app.run()
