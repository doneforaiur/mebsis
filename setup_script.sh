#!/usr/bin/env bash
# Mirza Atli, 2019. Script to setup "mebsis"

fresh_start="CREATE DATABASE mebsis;
            USE mebsis;"
firma_query="CREATE TABLE firma (
        iletisim VARCHAR(10) NOT NULL,
        adres VARCHAR(30) NOT NULL,
        eposta VARCHAR(30) NOT NULL,
        ticari_sicil VARCHAR(15) NOT NULL PRIMARY KEY,
        unvan VARCHAR(50) NOT NULL,
        sorumlu_kisi VARCHAR(40) NOT NULL,
        kurulma_tarihi DATE
)ENGINE=INNODB;"

mezun_query="CREATE TABLE mezun (
        ogrenci_no VARCHAR(7) PRIMARY KEY,
        isim VARCHAR(30) NOT NULL,
        soyad VARCHAR(20) NOT NULL,
        fakulte VARCHAR(15) NOT NULL,
        bolum VARCHAR  (15) NOT NULL,
        program VARCHAR (7) NOT NULL,
        baslama_tarihi YEAR,
        bitirme_tarihi YEAR,
        katilma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        gpa TINYINT,
        firma_no_fk VARCHAR(15) NOT NULL,
        pozisyon VARCHAR(20),ise_baslama_tarihi DATE,
        telefon VARCHAR(10) NOT NULL,
        eposta VARCHAR(30) NOT NULL,
        linkedin VARCHAR(30), 
        yabanci_diller VARCHAR(40),
        sertifikalar VARCHAR(40),
        onceki_isler VARCHAR(40),
        FOREIGN KEY (firma_no_fk) REFERENCES firma (ticari_sicil),
        CONSTRAINT CHECK (gpa BETWEEN 2 AND 4)
)ENGINE=INNODB;"

takip_query="CREATE TABLE IF NOT EXISTS takip (
        follower_id VARCHAR (7) NOT NULL,
        takip_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        following_id VARCHAR(7) NOT NULL,
        PRIMARY KEY (follower_id, following_id),
        FOREIGN KEY (follower_id) REFERENCES mezun (ogrenci_no),
        FOREIGN KEY (following_id) REFERENCES mezun (ogrenci_no)
)ENGINE=INNODB;"

konusma_query="CREATE TABLE IF NOT EXISTS konusma (
        konusma_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        kullanici_bir VARCHAR(7) NOT NULL,
        kullanici_iki VARCHAR(7) NOT NULL,
        FOREIGN KEY (kullanici_bir) REFERENCES mezun(ogrenci_no),
        FOREIGN KEY (kullanici_iki) REFERENCES mezun(ogrenci_no)
)ENGINE=INNODB;"
mesaj_query="CREATE TABLE IF NOT EXISTS mesaj (
        mesaj_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        konusma_id_fk INT UNSIGNED,
        mesaji_atan VARCHAR(7) NOT NULL,
        mesaj TEXT NOT NULL,
        mesaj_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (mesaj_id, konusma_id_fk),
        FOREIGN KEY (konusma_id_fk) REFERENCES konusma (konusma_id)
)ENGINE=INNODB;"

ilan_query="CREATE TABLE IF NOT EXISTS ilan (
        ilan_id INT(7) NOT NULL AUTO_INCREMENT,
        firma_fk VARCHAR(15),
        ilani_acan_fk VARCHAR(7),
        acilma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ilan_tipi BIT NOT NULL DEFAULT 1,
        PRIMARY KEY (ilan_id),
        FOREIGN KEY (firma_fk) REFERENCES firma (ticari_sicil),
        FOREIGN KEY (ilani_acan_fk) REFERENCES mezun (ogrenci_no)
)ENGINE=INNODB;"


yorum_query="CREATE TABLE IF NOT EXISTS yorum (
        ilan_id_fk INT(7),
        yorum_id INT(7) NOT NULL AUTO_INCREMENT,
        ogrenci_id_fk VARCHAR(7) NOT NULL,
        yorum_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        yorum_text TEXT NOT NULL,
        PRIMARY KEY (yorum_id),
        FOREIGN KEY (ilan_id_fk) REFERENCES ilan (ilan_id),
        FOREIGN KEY (ogrenci_id_fk) REFERENCES mezun (ogrenci_no)
)ENGINE=INNODB;"

/usr/bin/mysql -u $USER -p$PASSWORD << EOF
$fresh_start
$firma_query
$mezun_query
$takip_query
$konusma_query
$mesaj_query
$ilan_query
$yorum_query
EOF
