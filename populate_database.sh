#!/usr/bin/env bash
# Mirza Atli, 2019. Script to populate mebsis database.

create_student="USE mebsis;"


function rand_int(){
	NUMBER=$(cat /dev/urandom | tr -dc '0-9' | fold -w 256 | head -n 1 | sed -e 's/^0*//' | head --bytes $1)
}


function rand_str (){
	STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
}


i="0"
while [ $i -lt 100 ]
do
	my_array1=()
	my_array=()
	rand_int 6
	i=$[$i+1]
	m="0"
	while [ $m -lt  6 ] 
	do
		rand_int 6
		my_array1+=($NUMBER)
		#echo "${my_array1[@]}"
		m=$[$m+1]
	done
	firma_query="INSERT INTO firma	(iletisim, adres, eposta, ticari_sicil, unvan, sorumlu_kisi) VALUES (${my_array1[0]},${my_array1[1]},${my_array1[2]}, ${my_array1[3]}, ${my_array1[4]}, ${my_array1[5]});"
	mysql -u $USER -p$PASSWORD mebsis -e "$firma_query"
	m="0"
	while [ $m -lt  8 ] 
	do
		rand_int 6
		my_array+=($NUMBER)
		#echo "${my_array[@]}"
		m=$[$m+1]
	done
	mezun_query="INSERT INTO mezun (ogrenci_no, isim, soyad, fakulte, bolum, program,gpa,firma_no_fk,telefon,eposta) VALUES (${my_array[0]},${my_array[1]},${my_array[2]}, ${my_array[3]}, ${my_array[4]}, ${my_array[5]},3,${my_array1[3]},${my_array[6]},${my_array[7]});"
	mysql -u $USER -p$PASSWORD mebsis -e "$mezun_query"
done


