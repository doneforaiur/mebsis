#!/usr/bin/python3/
#-*-coding:utf-8-*-


from flask import Flask, request, url_for, send_file,render_template, make_response, redirect
import MySQLdb
import hashlib
import os
app = Flask(__name__)




def get_name(ogrenci_no):
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	cursor.execute("SELECT isim from mezun where ogrenci_no=" +str(ogrenci_no)+";")
	username = cursor.fetchone()
	username = username[0].capitalize().decode('utf8')
	db.close()
	return username


@app.route('/ilan_ekle', methods=['POST'])
def ilan_ekle():
	userno = request.cookies.get('username')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()

	firma_no = request.form['firma_no']
	ilan_text = request.form['ilan_text']
	ilan_tipi = request.form['ilan_tipi']
	if(ilan_tipi == "staj"):
		ilan_tipi = 0
	elif(ilan_tipi == "standart"):
		ilan_tipi = 1
	else:
		print("yanlışlık var...")
	
	print(firma_no, ilan_text, ilan_tipi, userno)
	cursor.execute("insert into ilan(firma_fk, ilani_acan_fk, ilan_tipi, ilan_text) VALUES("+str(firma_no)+","+str(userno)+","+str(ilan_tipi)+", '"+str(ilan_text)+"')")
	db.commit()	
	
	db.close()
	return redirect(url_for('anasayfa'))

@app.route('/anket_atama', methods=['GET'])
def anket_atama():	
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()

	if(request.args.get('low_year') != None and request.args.get('high_year') != None ):
		low_year = str( request.args.get('low_year') )
		high_year = str( request.args.get('high_year') )
		cursor.execute("select ogrenci_no from mezun where bitirme_tarihi BETWEEN '"+low_year+"' and '"+high_year+"';")
		result = cursor.fetchall()

		result = list(map(list, result))
		data = []
		for i in range(0,len(result)):
			data.append(result[i][0],) # İkisini birleştir.
		for i in data:
			cursor.execute("insert IGNORE into anket values (" + i +");")
		db.commit()
		if(request.cookies.get('username') == None):
			username = None
		else:
			username = request.cookies.get('username')
			cursor.execute("SELECT isim from mezun where ogrenci_no=" +str(username)+";")
			username = cursor.fetchone()
			username = username[0].capitalize().decode('utf8')
		db.close()
	return redirect(url_for('admin'))



@app.route('/cv_indir', methods=['GET'])
def cv_indir():
	
	if(request.cookies.get('username') == None):
		return redirect(url_for('index'))
	
	username = request.cookies.get('username')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	os.remove("/var/lib/mysql-files/cv.txt")
	cursor.execute("SELECT * from mezun where ogrenci_no='"+str(username)+"' into outfile '/var/lib/mysql-files/cv.txt';")
	cv = cursor.fetchone()
	db.close()
	return send_file("/var/lib/mysql-files/cv.txt", as_attachment=True)
	

@app.route('/admin')
def admin():
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	
	cursor.execute("SELECT ticari_sicil, unvan from firma")
	data = cursor.fetchall()
	cursor.execute("SELECT count(*) from mezun where firma_no_fk IN(SELECT ticari_sicil from firma) GROUP BY firma_no_fk")
	count = cursor.fetchall()
	cursor.execute("SELECT count(*), ticari_sicil, unvan FROM firma RIGHT JOIN mezun on mezun.firma_no_fk=firma.ticari_sicil GROUP BY ticari_sicil ORDER BY count(*) DESC")
	data = cursor.fetchall()
	data = list(map(list, data))	
	cursor.execute("SELECT ogrenci_no_fk from anket")
	anket_data = cursor.fetchall()
	rows = []
	for row in anket_data:
		rows.append(row)
	cursor.execute("SELECT AVG(YEAR(ise_baslama_tarihi) - bitirme_tarihi) from mezun where ise_baslama_tarihi IS NOT NULL")
	ortalama = cursor.fetchall()
	db.close()	
	return render_template('admin.html', ortalama=int(ortalama[0][0]), anket_len=len(rows),anket_data=rows,data=data, len=len(data))

	#cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE ilan.ilani_acan_fk IN (SELECT following_id from takip where follower_id='"+str(userno)+"');")


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
	db.close()
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
		db.close()	
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
	if(request.args.get('isim') != None):
		aranan_isim = str(request.args.get('isim'))
		cursor.execute("SELECT isim, soyad, ogrenci_no FROM mezun WHERE isim LIKE '%"+str(aranan_isim)+"%';")
		kullanicilar = cursor.fetchall()
		kullanicilar = list(map(list, kullanicilar))
		if(request.cookies.get('username') == None):
			username = None
		else:
			username = request.cookies.get('username')
			cursor.execute("SELECT isim from mezun where ogrenci_no=" +str(username)+";")
			username = cursor.fetchone()
			username = username[0].capitalize().decode('utf8')
	
		return render_template('elements.html', username=username, ogrenci_no=request.cookies.get('username'),data=kullanicilar, len=len(kullanicilar), page_number=0,current_page=0,
											low_limit=0, high_limit=0)

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
	

	
	db.close()
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

	db.close()
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

	username = request.cookies.get('username')
	if(username != None):
		userno = request.cookies.get('username')
		username = get_name(userno)
			
		cursor.execute("SELECT * from anket;")
		anket = cursor.fetchall()
		anket_flag = False
		if userno in str(zip(*anket)):
			anket_flag = True

		
	cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE ilan.ilani_acan_fk IN (SELECT following_id from takip where follower_id='"+str(userno)+"');")
	ilanlar = cursor.fetchall()
	ilanlar = list(map(list, ilanlar))
	
	yorumlar = ()
	for i in range(0,len(ilanlar)):
		yorumlar += (ilanlar[i][3],) # Tuple...
	
	cursor.execute("select yorum_text, ilan_id_fk, yorum_tarihi,ogrenci_id_fk from yorum where ilan_id_fk IN (" + ','.join(map(str, yorumlar)) +")")
	yorumlar = cursor.fetchall()
	db.close()
	ilan_flag = False
	return render_template('anasayfa.html',ilan_flag=ilan_flag,anket_flag=anket_flag,yorumlar=yorumlar, yorum_len=len(yorumlar), aktif=False,ilanlar=ilanlar, len=len(ilanlar), username=username,ogrenci_no=userno)


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
		
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
	cursor = db.cursor()
	
	
	# Tekil ve sabit ilanlar
	

	if(request.args.get('ilan_no') != None and request.args.get('ilan_no') != ""):
		ilan_no = str(request.args.get('ilan_no'))
		cursor.execute("SELECT isim, soyad, ogrenci_no FROM mezun WHERE ogrenci_no LIKE (select ilani_acan_fk from ilan where ilan_id='"+ilan_no+"');")
		
		ilanlar = cursor.fetchall()
		ilanlar = list(map(list, ilanlar))
		ilan_flag = True
		return render_template('anasayfa.html', ilan_flag=ilan_flag,anket_flag=False, yorum_len=0,aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)


	
	if(request.args.get('sehir') != None and request.args.get('sehir') != ""):
		ilan_sehir = str(request.args.get('sehir'))
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE ilan.ilan_text LIKE '%"+ilan_sehir+"%';")
		ilanlar = cursor.fetchall()
		ilanlar = list(map(list, ilanlar))
		ilan_flag = True
		return render_template('anasayfa.html', ilan_flag=ilan_flag,anket_flag=False, yorum_len=0,aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)
		


	if(request.args.get('ogrenci_no') != None and request.args.get('ogrenci_no') != ""):
		ilan_ogrenci_no = str(request.args.get('ogrenci_no'))
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE mezun.ogrenci_no="+ilan_ogrenci_no+";")
		ilanlar = cursor.fetchall()
		ilanlar = list(map(list, ilanlar))
		ilan_flag = True
		return render_template('anasayfa.html', ilan_flag=ilan_flag,anket_flag=False, yorum_len=0,aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)
	
	if(request.args.get('isim') != None and request.args.get('isim') != ""):
		isim = str(request.args.get('isim'))
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE mezun.isim LIKE '%"+isim+"%';")
		ilanlar = cursor.fetchall()
		ilanlar = list(map(list, ilanlar))
		ilan_flag = True
		return render_template('anasayfa.html', ilan_flag=ilan_flag,anket_flag=False, yorum_len=0,aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)
		
	
	if(ilan_turu == None):
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id, acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk;")
	else:
		cursor.execute("SELECT isim, soyad, ogrenci_no, ilan_id,acilma_tarihi FROM mezun RIGHT JOIN ilan ON mezun.ogrenci_no=ilan.ilani_acan_fk WHERE ilan_tipi='"+str(ilan_turu)+"';")

	ilanlar = cursor.fetchall() # Mezunlardaki gibi pagination yap.
	ilanlar = list(map(list, ilanlar))
	
	yorumlar = ()
	for i in range(0,len(ilanlar)):
		yorumlar += (ilanlar[i][3],) # Tuple...
	
	cursor.execute("select yorum_text, ilan_id_fk, yorum_tarihi,ogrenci_id_fk from yorum where ilan_id_fk IN (" + ','.join(map(str, yorumlar)) +")")
	yorumlar = cursor.fetchall()
	db.close()
	ilan_flag = True
	return render_template('anasayfa.html',ilan_flag=ilan_flag,anket_flag=False,yorumlar=yorumlar, yorum_len=len(yorumlar), aktif=True,ilanlar=ilanlar, len=len(ilanlar),username=username,ogrenci_no=userno)



@app.route('/yorum_yaz', methods = ['POST'])
def yorum_yaz():
	if request.method == "POST":  # Bu check çok da gerekli değil.
		yorum = request.form['yorum']
		ilan_no = request.form['ilan_no']
		userno = request.cookies.get('username')
		db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8' )
		cursor = db.cursor()
		cursor.execute("insert into yorum(ilan_id_fk, ogrenci_id_fk, yorum_text) VALUES('"+ilan_no+"','"+userno+"','"+yorum+"')")
		db.commit()
		db.close()
		return redirect(url_for('anasayfa'))


@app.route('/profil', methods=['GET', 'POST'])
def profil():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis" ,charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	cursor.execute("SELECT * from mezun where ogrenci_no=" +str(ogrenci_no)+";")
	ogrenci = cursor.fetchone()

	cursor.execute("SELECT unvan from firma where ticari_sicil='"+str(ogrenci[10])+"';")
	firma = cursor.fetchone() # TODO; Düzeltilmesi gerekiyor.
	firma = firma[0]
	isim = ogrenci[1]
	soyad = ogrenci[2]

	
	if(request.cookies.get('username') == None):
		username = None
		userno = None
	else:
		userno = request.cookies.get('username')
		username = get_name(userno)
		
	cursor.execute("SELECT ogrenci_no from mezun where ogrenci_no IN (SELECT following_id from takip where follower_id='"+str(userno)+"');")
	takip_edilenler = cursor.fetchall()
	db.close()
	return render_template('profil.html',takip_edilenler=str(takip_edilenler), username=username, userno=userno,ogrenci_no=ogrenci_no, isim=isim.capitalize().encode('utf-8'), soyad=soyad.encode('utf-8'), firma=firma)

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
	db.close()
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
	db.close()
	return render_template('elements.html',username=username,ogrenci_no=userno, data=result, len=len(result), low_limit=0, high_limit=0)

@app.route('/takip_et', methods = ['GET'])
def takip_et():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	userno = request.cookies.get('username')
	cursor.execute("INSERT INTO takip(follower_id, following_id) VALUES('"+str(userno)+"','"+str(ogrenci_no)+"')")
	db.commit()
	db.close()
	return redirect(url_for('profil', ogrenci_no=ogrenci_no))
	
@app.route('/takipten_cikar', methods = ['GET'])
def takipten_cikar():
	ogrenci_no = request.args.get('ogrenci_no')
	db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
	cursor = db.cursor()
	userno = request.cookies.get('username')
	cursor.execute("delete from takip where follower_id='"+str(userno)+"' and following_id='"+str(ogrenci_no)+"'")
	db.commit()
	db.close()
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

			db.close()
			return render_template('mesaj.html', data=mesaj_data_list, len=len(mesaj_data),message_to_name=message_to_name, username=username, message_to=message_to)
		
		db = MySQLdb.connect("localhost","misafir","misafir","mebsis",charset='utf8', init_command='SET NAMES UTF8')
		cursor = db.cursor()
		cursor.execute("SELECT mesaji_atan, mesaj, mesaj_tarihi from mesaj where konusma_id_fk IN (SELECT konusma_id FROM konusma where (kullanici_bir='"+str(username)+"' OR kullanici_bir='"+str(message_to)+"') AND (kullanici_iki='"+str(message_to)+"' OR kullanici_iki='"+str(username)+"'));")
		mesaj_data = cursor.fetchall() # Temizlenmesi gerek.
		db.close()
		return render_template('mesaj.html', data=mesaj_data, len=len(mesaj_data), username=username, message_to=message_to)

	if request.method == "POST":
		username = request.cookies.get('username')
		message_to = request.args.get('message_to')
		message = request.form['cevap']
		message = message.encode('utf8')
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
		db.close()
		return render_template('mesaj.html', data=mesaj_data, len=len(mesaj_data), username=username, message_to=message_to)
		



if __name__ == '__main__':
	app.run()
