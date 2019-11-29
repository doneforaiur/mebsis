#!/usr/bin/python3/
#-*-coding:utf-8-*-


from flask import Flask, request, url_for, render_template, make_response, redirect
import MySQLdb
import hashlib
app = Flask(__name__)

def get_name(ogrenci_no):
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	cursor.execute("SELECT isim from mezun where ogrenci_no=" +str(ogrenci_no)+";")
	username = cursor.fetchone()
	username = username[0].capitalize().decode('utf8')
	return username


@app.route('/index.html',methods=['GET'])
@app.route('/',methods=['GET'])
def index():
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	cursor.execute("SELECT count(*) from mezun")
	mezun_sayisi = cursor.fetchone()
	cursor.execute("SELECT count(*) from firma")
	firma_sayisi = cursor.fetchone()
	cursor.execute("SELECT count(*) from ilan")
	ilan_sayisi = cursor.fetchone()
	if(request.cookies.get('username') != None):
		return redirect(url_for('anasayfa'))
	return render_template('index.html', ilan_sayisi=ilan_sayisi[0],mezun=mezun_sayisi[0], firma=firma_sayisi[0], username=None)


@app.route('/contact.html',methods=['GET'])
def contact():
	if(request.cookies.get('username') == None):
		username = None
	else:
		username = request.cookies.get('username')
		db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
		cursor = db.cursor()		
		cursor.execute("SELECT isim from mezun where ogrenci_no=" +str(username)+";")
		username = cursor.fetchone()
		username = username[0].capitalize().decode('utf8')

	return render_template('contact.html', username=username)


@app.route('/mezun_ara', methods=['GET', 'POST'])
def mezunlar():
	if request.method == 'POST':
		ogrenci_no1 = request.args.get('ogrenci_no')
		page_number = str(request.form['page_number'])
		page_number=int(page_number)-1

	if request.method == 'GET':
		if(request.args.get('ogrenci_no') != None):
			ogrenci_no1 = request.args.get('ogrenci_no')
		else:
			ogrenci_no1 = 0
		page_number=0

	db = MySQLdb.connect("localhost","misafir","misafir","mebsis" ,charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	if(ogrenci_no1 == None):
		ogrenci_no1 = 0
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
	if(request.cookies.get('username') == None):
		username = None
	else:
		username = request.cookies.get('username')
		cursor.execute("SELECT isim from mezun where ogrenci_no=" +str(username)+";")
		username = cursor.fetchone()
		username = username[0].capitalize().decode('utf8')
	return render_template('elements.html', username=username, ogrenci_no=request.cookies.get('username'),data=rows, len=len(rows), page_number=page_number,current_page=current_page,
											low_limit=low_limit, high_limit=high_limit)

@app.route('/login', methods = ['GET','POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	db = MySQLdb.connect("localhost","misafir","misafir", "mebsis", charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	cursor.execute("SELECT password from password where ogrenci_no_fk="+str(username)+";")
	result = cursor.fetchone()

	if(str(result[0]) == hashlib.md5(password.encode()).hexdigest()):
		response = redirect(url_for('anasayfa'))
		response.set_cookie('username', username)
		response.set_cookie('password', str(result[0]))
	return response


@app.route('/cikis_yap', methods= ['POST'])
def cikis_yap():
	resp = redirect(url_for('index'))
	resp.set_cookie('username', expires=0)
	resp.set_cookie('password', expires=0)
	return resp


@app.route('/anasayfa')
def anasayfa():
	if(request.cookies.get('username') == None):
		return redirect(url_for('index'))
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	cursor.execute("SELECT count(*) from mezun")
	mezun_sayisi = cursor.fetchone()
	cursor.execute("SELECT count(*) from firma")
	firma_sayisi = cursor.fetchone()
	username = request.cookies.get('username')
	if(username != None):
		userno = request.cookies.get('username')
		username = get_name(userno)
	
	cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE ilan.ilani_acan_fk IN (SELECT following_id from takip where follower_id='"+str(userno)+"');")
	ilanlar = cursor.fetchall()
	ilanlar = list(map(list, ilanlar))
	print(ilanlar)
	
	return render_template('anasayfa.html',aktif=False,ilanlar=ilanlar, len=len(ilanlar), username=username,ogrenci_no=userno)


@app.route('/ilan')
def ilan():
	userno = request.cookies.get('username')
	username = get_name(userno)
	
	ilan_turu = request.args.get('ilan_turu')
	if(ilan_turu == "standart"):
		ilan_turu = 1
	elif(ilan_turu == "staj"):
		ilan_turu = 0
	else:
		ilan_turu = None
		
	cursor = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' ).cursor()

	if(request.args.get('ilan_no') != None):
		ilan_no = str(request.args.get('ilan_no'))
		cursor.execute("SELECT isim, soyad, ogrenci_no FROM mezun WHERE ogrenci_no IN (select ilani_acan_fk from ilan where ilan_id='"+ilan_no+"');")
		ilanlar = cursor.fetchall()
		ilanlar = list(map(list, ilanlar))
		return render_template('anasayfa.html',aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)
	
	if(ilan_turu == None):
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk;")
	else:
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id,acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE ilan_tipi='"+str(ilan_turu)+"';")
	
	
	ilanlar = cursor.fetchall() # Mezunlardaki gibi pagination yap.
	ilanlar = list(map(list, ilanlar))
	return render_template('anasayfa.html',aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)


@app.route('/profil', methods=['GET', 'POST'])
def profil():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis")
	cursor = db.cursor()
	cursor.execute("SELECT * from mezun where ogrenci_no=" +str(ogrenci_no)+";")
	ogrenci = cursor.fetchone()

	cursor.execute("SELECT unvan from firma where ticari_sicil='"+str(ogrenci[10])+"';")
	firma = cursor.fetchone() # TODO; Düzeltilmesi gerekiyor.
	firma = firma[0]
	isim = ogrenci[1].capitalize()
	soyad = ogrenci[2].capitalize()
	
	if(request.cookies.get('username') == None):
		username = None
	else:
		userno = request.cookies.get('username')
		username = get_name(userno)
		
	cursor.execute("SELECT ogrenci_no from mezun where ogrenci_no IN (SELECT following_id from takip where follower_id='"+str(userno)+"');")
	takip_edilenler = cursor.fetchall()
	return render_template('profil.html',takip_edilenler=str(takip_edilenler), username=username, userno=userno,ogrenci_no=ogrenci_no, isim=isim.decode('latin1'), soyad=soyad.decode('latin1'), firma=firma)

@app.route('/takipciler', methods=['GET'])
def takipciler():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	cursor.execute("SELECT ogrenci_no, isim, soyad from mezun where ogrenci_no IN (SELECT follower_id FROM takip WHERE following_id='" +str(ogrenci_no)+"');")
	result = cursor.fetchall()
	if(request.cookies.get('username') == None):
		username = None
	else:
		userno = request.cookies.get('username')
		username = get_name(userno)
	return render_template('elements.html', username=username,ogrenci_no=userno,data=result, len=len(result), low_limit=0, high_limit=0)


@app.route('/takipedilenler', methods=['GET'])
def takipedilenler():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	cursor.execute("SELECT ogrenci_no, isim, soyad from mezun where ogrenci_no IN (SELECT following_id FROM takip WHERE follower_id='" +str(ogrenci_no)+"');")
	result = cursor.fetchall()
	if(request.cookies.get('username') == None):
		username = None
	else:
		userno = request.cookies.get('username')
		username = get_name(userno)
	return render_template('elements.html',username=username,ogrenci_no=userno, data=result, len=len(result), low_limit=0, high_limit=0)

@app.route('/takip_et', methods = ['GET'])
def takip_et():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	userno = request.cookies.get('username')
	cursor.execute("INSERT INTO takip(follower_id, following_id) VALUES('"+str(userno)+"','"+str(ogrenci_no)+"')")
	db.commit()
	return redirect(url_for('profil', ogrenci_no=ogrenci_no))
	
@app.route('/takipten_cikar', methods = ['GET'])
def takipten_cikar():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	userno = request.cookies.get('username')
	cursor.execute("delete from takip where follower_id='"+str(userno)+"' and following_id='"+str(ogrenci_no)+"'")
	db.commit()
	return redirect(url_for('profil', ogrenci_no=ogrenci_no))
	

@app.route('/mesaj', methods = ["POST","GET"])
def mesaj():
	if request.method == "GET":
		username = request.cookies.get('username')
		message_to = request.args.get('message_to')
		if(username == None):
			return redirect(url_for('anasayfa'))
		if(message_to == None):
			db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
			cursor = db.cursor()
			cursor.execute("SELECT * from konusma where kullanici_bir='"+str(username)+"' or kullanici_iki='"+str(username)+"';")
			mesaj_data = cursor.fetchall() # Temizlenmesi gerek.
			mesaj_data_list = list(map(list, mesaj_data))
			message_to_name = []	
			for i in range(0,len(mesaj_data)):
				if(mesaj_data_list[i][1] == username):
					mesaj_data_list[i][1] = mesaj_data_list[i][2]
					mesaj_data_list[i][2] = username
				cursor.execute("SELECT isim, soyad from mezun where ogrenci_no='"+mesaj_data_list[i][1]+"';")
				message_to_name.append(cursor.fetchone())
			return render_template('mesaj.html', data=mesaj_data_list, len=len(mesaj_data),message_to_name=message_to_name, username=username, message_to=message_to)
		
		db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
		cursor = db.cursor()
		cursor.execute("SELECT mesaji_atan, mesaj, mesaj_tarihi from mesaj where konusma_id_fk IN (SELECT konusma_id FROM konusma where (kullanici_bir='"+str(username)+"' OR kullanici_bir='"+str(message_to)+"') AND (kullanici_iki='"+str(message_to)+"' OR kullanici_iki='"+str(username)+"'));")
		mesaj_data = cursor.fetchall() # Temizlenmesi gerek.
		return render_template('mesaj.html', data=mesaj_data, len=len(mesaj_data), username=username, message_to=message_to)

	if request.method == "POST":
		username = request.cookies.get('username')
		message_to = request.args.get('message_to')
		message = request.form['cevap']
		db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
		cursor = db.cursor()
		cursor.execute("SELECT konusma_id FROM konusma where (kullanici_bir='"+str(username)+"' OR kullanici_bir='"+str(message_to)+"') AND (kullanici_iki='"+str(message_to)+"' OR kullanici_iki='"+str(username)+"');")
		konusma_id_fk = cursor.fetchone() # Temizlenmesi gerek.
		if(konusma_id_fk == None):
			cursor.execute("INSERT INTO konusma(kullanici_bir, kullanici_iki) VALUES ('"+str(username)+"','"+str(message_to)+"');")	
			db.commit()
			konusma_id_fk = cursor.execute("SELECT konusma_id FROM konusma where (kullanici_bir='"+str(username)+"' OR kullanici_bir='"+str(message_to)+"') AND (kullanici_iki='"+str(message_to)+"' OR kullanici_iki='"+str(username)+"');")
		cursor.execute("INSERT INTO mesaj(konusma_id_fk, mesaji_atan, mesaj) VALUES ('"+str(konusma_id_fk[0])+"','"+str(username)+"','"+str(message)+"');")	
		db.commit()
		cursor.execute("SELECT mesaji_atan, mesaj, mesaj_tarihi from mesaj where konusma_id_fk IN (SELECT konusma_id FROM konusma where (kullanici_bir='"+str(username)+"' OR kullanici_bir='"+str(message_to)+"') AND (kullanici_iki='"+str(message_to)+"' OR kullanici_iki='"+str(username)+"'));")
		mesaj_data = cursor.fetchall() 
		return render_template('mesaj.html', data=mesaj_data, len=len(mesaj_data), username=username, message_to=message_to)
		



if __name__ == '__main__':
	app.run()
