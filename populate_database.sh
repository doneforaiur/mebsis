#!/usr/bin/env bash
# Mirza Atli, 2019. Script to populate mebsis database.
function rand_int(){
	NUMBER=$(cat /dev/urandom | tr -dc '0-9' | fold -w 256 | head -n 1 | sed -e 's/^0*//' | head --bytes $1)
}

function rand_str (){
	STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
}

declare -a isimler=("MIRZA" "HALIL" "YUCEL" "DOGUKAN" "AYSE" "HASANABE"
"HAYATİ" "BEDRİYE" "BİRSEN" "SERDAL" "BÜNYAMİN" "ÖZGÜR" "FERDİ" "REYHAN"
"İLHAN" "GÜLŞAH" "NALAN" "SEMİH" "ERGÜN" "FATİH" "ŞENAY" "SERKAN" "EMRE"
"BAHATTİN" "IRAZCA" "HATİCE" "BARIŞ" "REZAN" "FATİH" "FUAT" "GÖKHAN" 
"ORHAN" "MEHMET" "EVREN" "OKTAY" "HARUN" "YAVUZ" "PINAR" "MEHMET"
"UMUT" "MESUDE" "HÜSEYİN" "HAŞİM" "EYYUP" "UFUK" "AHMET" "MEDİHA" 
"HASAN" "KAMİL" "NEBİ" "ÖZCAN" "NAGİHAN" "CEREN" "SERKAN" "HASAN"
"YUSUF" "KENAN" "ÇETİN" "TARKAN" "MERAL" "LEMAN" "ERGÜN" "KENAN"
"AHMET" "URAL" "YAHYA" "BENGÜ" "FATİH" "NAZMİ" "DİLEK" "MEHMET" 
"TUFAN" "MEHMET" "TURGAY" "YILMAZ" "GÜLDEHEN" "GÖKMEN" "BÜLENT" 
"EROL" "BAHRİ" "ÖZEN" "ÖZLEM" "SELMA" "TUĞSEM" "TESLİME" "NAZLI"
"GÜLÇİN" "İSMAİL" "MURAT" "EBRU" "TÜMAY" "AHMET" "EBRU" "HÜSEYİN" 
"YAVUZ" "BAŞAK" "AYŞEGÜL" "EVRİM" "YASER" "ÜLKÜ" "ÖZHAN" "UFUK" "AKSEL")


i="0"
while [ $i -lt 2000 ]
do
	my_array1=()
	my_array=()
	rand_int 6
	i=$[$i+1]
	m="7"
	while [ $m -lt  6 ] 
	do
		rand_int 6
		my_array1+=($NUMBER)
		#echo "${my_array1[@]}"
		m=$[$m+1]
	done
	#firma_query="INSERT INTO firma	(iletisim, adres, eposta, ticari_sicil, unvan, sorumlu_kisi) VALUES (${my_array1[0]},${my_array1[1]},${my_array1[2]}, ${my_array1[3]}, ${my_array1[4]}, ${my_array1[5]});"
	#mysql -u $1 -p$2 mebsis -e "$firma_query"

	rand_int 2
	my_array+=(${isimler[$NUMBER]})
	rand_int 2
	my_array+=(${isimler[$NUMBER]})
	m="2"
	#echo "${my_array[0]}"
	while [ $m -lt  9 ] 
	do
		rand_int 6
		my_array+=($NUMBER)
		m=$[$m+1]
	done
	#echo ${my_array}
	mezun_query="INSERT INTO mezun (ogrenci_no, isim, soyad, fakulte, bolum, program,gpa,firma_no_fk,telefon,eposta) VALUES (${my_array[2]},'${my_array[0]} ','${my_array[1]}', ${my_array[3]}, ${my_array[4]}, ${my_array[5]},3,547063,${my_array[6]},${my_array[7]});"


	mysql -u $1 -p$2 mebsis -e "$mezun_query" 2> /dev/null
done


