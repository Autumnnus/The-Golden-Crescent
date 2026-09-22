# Kart 0 — Ortadoğu ve Balkanlar

**Durum: Rûm çevresi, İran yedi üyeli çekirdeği ve RUS'suz Kuzey Avrasya siyasi katmanı Atlas önizlemesine aktarıldı; henüz etkin dünya siyasi senaryosu değildir.**

Bu kart daha önceki Rûm önizlemelerinin sınır kararlarını korur; onların nüfus, ekonomi, hukuk ve askerî verisini taşımaz. State kimlikleri Atlas kataloglarıyla yeniden doğrulanır ve sonuç tek bir siyasi kaynağa aktarılır.

## Korunmuş state kararı

Bu dosya `08_middle_east`, `09_central_asia`, `14_siberia` ve `15_russia`
bölgelerindeki kartta adı geçmeyen state'lerin de karar merciidir. Bu state'ler,
yazılı atlasın doğrudan yeni bir province sahibi söylemediği yerel düzeni
korudukları için Atlas'ta mevcut sahibiyle tutulur; bu bir boşluk veya vanilla
imparatorluğun geri dönüşü değildir. `political_state_ledger.py` bu saklama
kararını her state için kayda geçirir.

## Kesin siyasi kararlar

| Alan | Doğrudan egemen / statü |
|---|---|
| Rûm çekirdeği | Rûm; Balkan, Anadolu, Halep–Bağdat, ada ve Malta kararları yazılı atlasla sınırlıdır |
| Bosna, Arnavutluk, Tuna, Adana, Erzurum, Trabzon | Rûm'a bağlı altı özerk yönetim |
| Kürdistan, Basra, Şam, Cebel-i Lübnan, Kudüs | Bağımsız |
| Mısır | Nil, Sina ve Dongola koridoru; Hicaz doğrudan eyalet değildir |
| Hicaz | Bağımsız koruma antlaşmalı şeriflik |
| İran | İsfahan, Tebriz, Horasan, Mazenderan, Kirman, Luristan, Huzistan: eşit üyeler; tek ülke/tek overlord değildir |
| Kafkasya | Gürcistan, Erevan, Bakü, Dağıstan ve Çerkes ağları ayrı; Rûm/İran iddiaları sahiplik değildir |
| Bozkır/Orta Asya | Kırım, Tatar, Kalmuk, Moskova, Novgorod, Kazak cüzleri, Buhara, Hive, Hokand, Kaşgar, Kırgız, üç Afgan aktör ve Beluç hanlıkları ayrı |

## İlk doğrulanmış Atlas state adayları

`STATE_BASRA`, `STATE_BAGHDAD`, `STATE_MOSUL`, `STATE_DIYARBAKIR`, `STATE_SYRIA`, `STATE_LEBANON`, `STATE_PALESTINE`, `STATE_TRANSJORDAN`, `STATE_ADANA`, `STATE_ERZURUM`, `STATE_TRABZON`, `STATE_BOSNIA`, `STATE_ALBANIA`, `STATE_BULGARIA`, `STATE_LOWER_EGYPT`, `STATE_MIDDLE_EGYPT`, `STATE_UPPER_EGYPT`, `STATE_SINAI`, `STATE_DONGOLA`, `STATE_HEDJAZ`, `STATE_ISFAHAN`, `STATE_TABRIZ`, `STATE_KHORASAN`, `STATE_MAZANDARAN`, `STATE_KERMAN`, `STATE_LURISTAN`, `STATE_KHUZESTAN`, `STATE_ARMENIA`, `STATE_AZERBAIJAN`, `STATE_GREATER_CAUCASUS`, `STATE_DAGESTAN`, `STATE_CRIMEA`, `STATE_KAZAN`, `STATE_KALMYKIA`, `STATE_MOSCOW`, `STATE_NOVGOROD`, `STATE_KHIVA`, `STATE_FERGANA`, `STATE_TIANSHAN`, `STATE_HERAT`, `STATE_KABUL`, `STATE_KANDAHAR`, `STATE_BALUCHISTAN`.

İran için İsfahan, Tebriz, Horasan, Mazenderan, Kirman, Luristan ve Huzistan artık gerçek state eşlemesiyle `card00.json` içindedir. Kirman'ın Laristan'daki dokuz doğrulanmış İran province'i ona verildi; Umman ve Bahreyn'in aynı state'teki province'leri korunur. Bu, Bender Abbas ticari çıkışını İran birliği içinde tek merkezli Persia'ya bırakmadan temsil eder.

`card04.json` Kafkasya ve Rus çekirdeklerini gerçek state verisiyle ekler: Ermenistan → Erevan, Azerbaycan → Bakü, Büyük Kafkasya → Gürcistan; Kırım, Kazan, Kalmukya, Moskova ve Novgorod da kendi yazılı aktörlerine geçer. Kuzey Kafkasya'da Çeçen ve Çerkes katalog province'leri aynen kalır; onların dışındaki sekiz province Dağıstan imametlerine verilir.

## 0C — RUS'suz Kuzey Avrasya

`card04.json` ile `card12.json`, RUS'un kalan bütün doğrudan province
paylarını kaldırır. Moskova yalnız merkezî Rus çekirdeğini; Novgorod kuzey
ticaret kuşağını; Büyük Tatar Hanlığı Volga–kuzey Karadeniz geçitlerini taşır.
Mari, Mordvin ve Ural yerel yönetimleri orman kuşağında ayrıdır.

Sibirya, Ob, Sibirya Tatar, Yenisey, Buryat, Saha, Ohotsk, Kamçatka, Çukotka ve
Kolıma yerel siyasi birimlerine ayrılır. Lehistan–Litvanya doğu Ruthen hattını,
Boğdan Besarabya'yı, Baltık Dükalığı Riga'yı alır; Kars bütünü Erzurum
Atabeyliği'ne geçer. Birleşik Atlas kataloğu RUS için kara sahibi bulmaz.

Bu state ölçeğinde yapımcı kararı, yerel halkları tek kültür veya tek merkez
saymaz. Kültür/nüfus fazı her ülkenin iç bileşimini ayrıca kuracaktır.

## Kapanan sınır kararları

- İran yedi üyesi için merkezî çekirdek ve kuzeydoğu/dış sınırdaki bütün yerel province sahipleri Kart 0, Kart 6B ve siyasi state karar defteriyle kilitlendi.
- Mısır'ın Nil deltası–Dongola, Sina ve Hicaz'ın doğrudan state sınırları vanilla eşlemesiyle atlasla uyumludur. `card60.json`, Hicaz'ı Mısır'a %5 katkılı ve otomatik savaşa katılmayan `ve_hajj_protection` ile bağlar; bu, Hicaz'ı Mısır eyaleti yapmaz.
- Cebel Şammar ve Necid iki farklı çekirdektir; ortak state içindeki province ayrımı Kart 6B'de tek doğrudan sahip ilkesine göre sabitlendi.
- Basra'nın şehir hubı ve Kuveyt'in port hubı tek `STATE_BASRA` içindedir. Province ayrımı nihai siyasi kayıttır; ikinci fiziksel port yaratılmaz.

## 0D — Yemen ve Basra–Kuveyt kapanışı

`card55.json`, `STATE_YEMEN`deki Hicaz sınır dışı payını Lahic'e geçirir.
Böylece Zeydi yayla imamlığı, Lahic/Aden ticaret kıyısı, Mahra ve Kathîr doğu
ağları ayrı yerel sahiplikte kalır. `card00.json`daki `STATE_BASRA` province
ayrımı da nihai siyasi karardır: Rûm Nasıriye sınır kuşağını, Basra alt delta
ve limanı, Kuveyt ise kendi liman-vaha çekirdeğini tutar.
