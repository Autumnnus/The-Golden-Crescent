# Kart 1 — Avrupa ve Akdeniz

**Durum: Avrupa siyasi sahipliği kilitli. Altı Fransız devleti, İberya, Alman çekirdekleri, Prusya kapanışı, Milano/Venedik, Britanya, Kalmar iç taçları ve Lehistan-Litvanya çekirdeği haritadadır; küçük Alman/İtalyan alanların doğrudan province sahipleri de Kart 6B ile siyasi state karar defterinde açıkça sabittir.**

## Korunmuş state kararı

`00_west_europe`, `01_south_europe` ve `02_east_europe` içindeki kartta
yeniden yazılmayan state'ler bu dosyanın bilinçli koruma kararındadır. Yazılı
atlas yeni egemen söylemediğinde yerel krallık, şehir devleti veya küçük taç
mevcut province sahipliğiyle kalır; bu karar Fransa, Prusya veya eski büyük
devletlerin toprak iddiasını geri getirmez. Tam liste makinece state karar
defterinde tutulur.

## 1G — Lehistan-Litvanya çekirdeği

`card12.json`, Varşova merkezli seçimli birliği doğrudan yazılı kaynakta
belirtilen üç coğrafi halka üzerinden kurar: Leh çekirdeği (`STATE_GREATER_POLAND`,
`STATE_LESSER_POLAND`, Posen), Litvan bölgesi (`STATE_KAUNAS`) ve doğu Ruthen
hattı (`STATE_BREST`, `STATE_MINSK`, `STATE_VOLHYNIA`). Bu, RUS ve PRU'nun ilgili
province paylarının tamamını `VPL`'ye geçirir; her state'te vanilla nüfus/bina
verisi bilinçli olarak düşürülür.

Kraków ile Batı/Güney Galiçya bu ilk kararda yoktur; Kiev ise VPL doğu Ruthen halkasına dahildir. Nihai düzen `card50.json` ile Batı Galiçya'nın Avusturya payını Kraków'a, Doğu Galiçya'yı VPL'ye verir. Boğdan (`MOL`) için VPL koruma/bağlılık ilişkisi `card64.json`daki `ve_tributary_compact` ile ayrıca kuruludur; sınır ile diplomasi birbirine karıştırılmaz.

## 1F — Kalmar iç düzenleri

`card11.json`, Finlandiya'nın altı state'ini İsveç tacına ve İzlanda'yı Norveç tacına geçirir. Finlandiya ayrı ülke başlangıç kaydı `reset_countries: [FIN]` ile kaldırılır. `card60.json`, vanilla Danimarka–Norveç ve Schleswig–Holstein kişisel birliklerini kaldırır; üç Kalmar tacı arasındaki +50 ilişki ortak dış kurulun oyun ölçeğindeki başlangıç göstergesidir. Kalmar ortak tacı, İsveç'i Danimarka'nın subject'i yapan sahte bir hiyerarşiye çevrilmez; Schleswig/Holstein ayrı diyetli devletlerdir.

## 1E — Britanya ortak taçları

`card09.json`, İngiltere–Galler, İskoçya ve İrlanda'nın ana ada state'lerini ayrı taçlar olarak eşler. Ortak hükümdar ve Londra dış kurulu state sahipliği değildir; `card64.json`daki üç karşılıklı +50 ilişki bu siyasi önizlemedeki diplomasi temsilidir. Guyana, Guatemala, Yukarı Endülüs, Malaya ve Newfoundland payları ilgili yerel kartlarda kapatıldı. Bahamalar, Bermuda, Güney Atlantik ve `STATE_WEST_INDIES` içindeki kalan on bir province, Londra Tacı Denizaşırı Bağımlılıkları'nın sınırlı doğrudan idaresidir; bu idare başka kıtasal alan veya liman hakkı iddia etmez.

## 1D — Milano ve Venedik

`card08.json`, Lombardiya ve Venetia'daki AUS paylarını Milano ve Venedik'e verir. Bu iki bütün state, yazılı atlasın ayrı aktörleri ile doğrudan eşleşir. Savoy–Piyemonte, Ceneviz ve merkezî/güney İtalya'nın diğer mevcut yerel devletleri bu kartta değiştirilmez.

## 1C — Alman çekirdekleri

`card07.json`, Brandenburg, Pomeranya, Ren kent birliği ve Anhalt'ın mevcut PRU province paylarını ayrı devletlere aktarır. Ren kartı North Rhine, Rhineland, Ruhr ve Westphalia'daki yalnız PRU payını alır; Bavyera, Lippe ve diğer yerel mevcut sahipler korunur. Posen, 1G'nin yazılı Lehistan-Litvanya çekirdeğidir. Doğu/Batı Prusya ve Silezya, `card49.json`da sırasıyla Lehistan-Litvanya, Baltık Prusya Dükalığı ve Bohemya'ya geçtiği için PRU geçici sahibi kalmaz.

## 1B — İberya'nın kesin çekirdekleri

`card05.json`, Endülüs'ü aşağı/yukarı Endülüs, Extremadura ve Lizbon çevresindeki Estremadura; Kastilya'yı Yeni/Eski Kastilya ile León; Aragon'u Aragon ve Katalonya'daki kendi province'leri; Galiçya'yı Galiçya, Asturias ve Entre Douro e Minho; Navarra'yı Bask state'i üzerinden eşler. Aragon/Katalonya'daki mevcut SPC province'leri korunur. Beira ve Murcia Endülüs Federasyonu'na, Valencia ve Balearlar Aragon'a devredilir. Rif Fas'a ve Kanaryalar Endülüs'e geçer; böylece SPA'nın geçici kara varlığı kapanır. POR'un İber dışı payları ayrıca denizci ağının yerel/kurumsal sahiplerine aktarılır.

## 1A — Altı Fransız devleti

Paris, Burgonya, Bretonya, Akitanya, Oksitanya ve Provence birbirinden bağımsızdır. Paris'in unvanı diğer beşinin tabiiyeti değildir. Atlas'ın 1836 `FRA` state'leri eksiksiz dağıtılmıştır:

| Devlet | State'ler | Sınır kararı |
|---|---|---|
| Paris | Île-de-France, Picardy, Normandy, Champagne, Orléanais-Berry, Maine-Anjou | Seine–Loire merkez/kuzey çekirdeği |
| Burgonya | Burgundy, Franche-Comté, Lorraine, Alsace-Lorraine, Rhône | Lyon/Rhône tarifesi Burgonya–Provence anlaşmazlığıdır; doğrudan sahip Burgonya |
| Bretonya | Brittany | Yarımada çekirdeği |
| Akitanya | Aquitaine, Guyenne, Poitou-Saintonge | Bordeaux–Garonne/Gaskonya ve kuzey bağlantısı |
| Oksitanya | Languedoc, Auvergne-Limousin | Toulouse–Languedoc çekirdeği |
| Provence | Provence'taki eski FRA province'leri ve Corsica | Marseille/Rhône ağzı; Piedmont'a ait tek Provence province'i korunur |

Bu karar, yazılı atlasın açık bıraktığı Lyon/Rhône sahibi için yapımcı varsayımıdır. Ticaret krizi bu yüzden iki devlet arasında kalır; state iki ülkeye çift egemen olarak yazılmaz.

`prepare_card01.py` çıktısı `card01.json` yalnız siyasi önizlemedir. `pops: drop` ve `buildings: drop` bütün kartta zorunludur.

Vanilla `FRA` şirket merkezi Alsace-Lorraine'deydi. Altı devlet oluşturulduğunda merkezinin sahibi kalmadığından kart bu eski şirket listesini açıkça boşaltır. Bu bir ekonomik karar değildir; geçersiz başlangıç referansını önizlemeden kaldıran dar uyumluluk işlemidir.

`FRA`'nın denizaşırı vanilla payları Afrika ve Atlantik kartlarıyla tamamen kapatıldı. Bu, altı Fransız devletine yedinci bir metropol çekirdeği eklemez; tüm eski paylar yerel/yazılı sahiplere döner.

## Avrupa alt kartlarının kapanışı

İberya, Alman İmparatorluğu çevresi, İtalya, Britanya ortak tacı, Kalmar, Lehistan–Moskova–Tatar hattı ve Balkan dışı Orta Avrupa ayrı kartlarla tamamlandı. Küçük devlet/province kararları Kart 6B ve siyasi state karar defterinde açıkça sabittir.

## 1H–1J — Orta Avrupa ve Alçak Ülkeler tamamlamaları

`card35.json`, Bohemya ve Moravya'daki Avusturya payını Bohemya Krallığına
aktarır. `card36.json`, Macaristan ile Erdel'in Avusturya `crown_land`
bağlarını kaldırır; bu iki devlet yazılı atlasın gerektirdiği gibi bağımsızdır.
`card37.json` Hannover'in Büyük Britanya kişisel birliğini kaldırır ve
Belçika'nın Flanders/Gelre payını Brabant Kent Birliği ile Wallonia payını
Liège arasında state ölçeğinde ayırır. Hollanda ve Lüksemburg province'leri
korunur. Küçük Alman/İtalyan devletlerinin sınırları Kart 6B ve siyasi state
karar defterinde ayrı açık province sahipliğiyle kilitlidir.


## 1N — Prusya kalıntısının kapanışı

`card49.json`, Batı Prusya'yı Lehistan-Litvanya Baltık koridoruna, Doğu Prusya'yı bağımsız Baltık Prusya Dükalığına ve iki Silezya state'ini Bohemya'ya verir. Böylece geçici PRU sahibi kalmaz; bu, kullanıcı kararındaki güçlü Lehistan ve birleşmemiş Alman düzeniyle uyumludur.


## 1O — Kraków ve Galiçya

`card50.json`, Batı Galiçya'daki Avusturya payını mevcut Kraków şehir devletine, Doğu Galiçya'yı Lehistan-Litvanya'ya verir. Bu, güçlü Lehistanın teknik ve Baltık ağıyla uyumlu doğu kuşağını büyütürken Krakówun ayrı kent siyasetini korur.
