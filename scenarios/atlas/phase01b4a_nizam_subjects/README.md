# Faz 1B.4A — Altı Nizam bağlısı

**13 Eylül 2026. Statik ve kümülatif Atlas önizlemesi; etkin veya oynanabilir sürüm değildir.**

Bu paket Faz 1B.3 Rûm dünyasını korur; Bosna, Arnavutluk, Tuna, Adana, Erzurum ve Trabzon bağlılarını nüfus, okuryazarlık, hukuk, kurum, hükümet, ekonomi ve askerî kapasite bakımından doldurur. Kaynak [scenario.json](scenario.json), okunabilir girdiler [nizam-plan.json](nizam-plan.json), vanilla scriptlerinden hesaplanan kapasite [capacity-audit.json](capacity-audit.json), kabul sonucu [verification.json](verification.json).

## Başlangıç profilleri

| Ülke | Nüfus | Bina | Kara / deniz | Başlangıç rolü |
|---|---:|---:|---:|---|
| Bosna Emirliği | 950.000 | 35 | 10 / 0 | Metal, silah ve sınır muhafızları |
| Arnavutluk Emirliği | 1.450.000 | 52 | 12 / 3 | Adriyatik limanı, maden ve hafif sanayi |
| Tuna Emirliği | 2.100.000 | 82 | 18 / 4 | En büyük bağlı tarım–imalat tabanı ve Tuna kuvveti |
| Adana Atabegliği | 550.000 | 35 | 8 / 3 | Çukurova pamuğu, kömür, dokuma ve Mersin limanı |
| Erzurum Atabegliği | 800.000 | 28 | 10 / 0 | Doğu serhaddi, demir–kurşun ve kara ordusu |
| Trabzon Atabegliği | 700.000 | 26 | 8 / 4 | Karadeniz limanı, tersane ve kıyı savunması |

Toplam **6.550.000 kişi, 258 bina seviyesi, 66 profesyonel tabur ve 14 fırkateyn** vardır. Her ülke teknoloji seviyesi 4 temeline, hat piyadesi ve atmosferik motor öncüllerine sahiptir. Hükümetleri iki üyeli yerel koalisyonlardır; yapay clout yüzdesi verilmedi.

Altı ülkede 24 kanunluk ortak H1 profili kullanılır: monarşi, servet esaslı oy, atanmış bürokrasi, profesyonel ordu, tarımcılık, merkantilizm, kiracı çiftçilik, din özgürlüğü, dinî okullar, hayır sağlık sistemi ve kölelik yasağı omurgayı oluşturur. Okul ve polis kurumu birinci düzeydedir. Kanunların gereken teknoloji kimlikleri vanilla kaynaklarından doğrulandı.

## Nüfus ve kimlik

Faz 1A/1B.3'te derlenmiş her kültür–din birleşimi aynen korunup yeni ülke/eyalet toplamına oransal olarak ölçeklendi. Böylece kültür ve mezhep ayrı marjinaller halinde yeniden eşleştirilmedi. Devralınmış **17.806 köle statüsü**, kültür ve dini silinmeden köylüye çevrildi. Bu sayılar başlangıç tasarımıdır; göç, asimilasyon ve işgücü dağılımı motor sonucudur.

Trabzon'un yazılı başkent kararına uymayan eski coğrafya hatası düzeltildi. Vanilla state-region tanımından doğrulanan `x146DD9` şehir merkezi Rûm'dan Trabzon Atabegliği'ne geçti. Şehir merkezini kaybeden Rûm parçasındaki iki şehir binası sıfırlandı; Rûm'un nüfusu ve 160/48 kuvveti değişmedi.

## Ekonomik bağlar

Ekonomiler birbirini tamamlayacak biçimde tasarlandı. Bosna silah ve top üretebilir fakat kömüre; Arnavutluk maden ve tarıma rağmen alet ve topa; Tuna kömüre; Adana demir, alet ve tahıla; Erzurum alet, kömür ve topa; Trabzon tahıl, kömür, alet ve topa ihtiyaç duyar. Kâğıt bütün küçük idarelerin ortak dış girdisidir. Donanmalar yerel fırkateyn bakımında palangaya, yeni gemi inşasında daha geniş mal ağına dayanır.

[capacity-audit.json](capacity-audit.json) açık üretim yöntemlerinin tam istihdamlı script değerlerini birlik bakım girdileriyle karşılaştırır. Negatif bakiye gerçek açlık veya piyasa çöküşü tahmini değildir; Nizam içi ticaret ve Rûm pazarına bağımlılık işaretidir. Fiyat, pazar erişimi, gümrük, konvoy, ücret, yeterlilik ve gerçek istihdam Atlas tarafından simüle edilmez.

## Nizam sözleşmesinin sınırı

Bu faz Fransa benzeri özel bir vassallık kurgulamaz. Altı ülke için mevcut `ve_nizam_dependency` prototipi korunur: vanilla vassal tabanından türeyen savaş katılımı ve yüzde 8 gelir aktarımı vardır. Yazılı **sabit katkı**, sınırlı askerî kota ve indirimli fakat tam birleşmemiş gümrük ilişkisi henüz gerçek mekanik değildir. Subject type, pazar üyeliği ve emancipasyon başlangıç etkisi motor testi yapılmadan tamamlanmış sayılmaz.

Kosova planı Atlas'ın yüzde 30 işgücü tarama eşiğinin altında tutuldu. Yeterlilik ve gerçek istihdam yine motor sonucudur; bu faz önceki paketin uyarılarına yenisini eklemez.

## Yeniden üretme ve doğrulama

Mod kökünde:

```sh
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b4a_nizam_subjects/prepare.py
python3 scripts/tools.py atlas scenario validate scenarios/atlas/phase01b4a_nizam_subjects/scenario.json
python3 scripts/tools.py atlas scenario report scenarios/atlas/phase01b4a_nizam_subjects/scenario.json --out build/phase01b4a/report.json
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b4a_nizam_subjects/audit.py
python3 scripts/tools.py atlas scenario build scenarios/atlas/phase01b4a_nizam_subjects/scenario.json --out build/phase01b4a/generated
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b4a_nizam_subjects/verify.py
python3 scripts/tools.py atlas preview --scenario scenarios/atlas/phase01b4a_nizam_subjects/scenario.json --region RUM,BOS,ALB,BUL,ADA,ERZ,TRB,KUR,BSR,SYR,LEB,PAL,KUW --out build/maps/phase01b4a-nizam.html
```

Doğrulama; parent hashlerini, altı ülkenin toplamlarını, kanun/kurum/IG scriptlerini, derlenmiş birlikleri, POP statülerini, Trabzon şehir hexini, üretim girdilerini ve diğer ülkelerin değişmezliğini kontrol eder. Oyun motoru çalıştırılmadı ve `world/` etkinleştirilmedi.

## Sonraki iş — Faz 1B.4B

Bağımsız Kürdistan, Basra, Suriye, Lübnan, Filistin ve Kuveyt kuşağı aynı derinlikte hazırlanacak. Basra şehir-hub sahipliği o fazda doğrulanacak. Ardından 1B bölgesel artık-scope denetimi ve Nizam mekanik kapısı ayrı kabul noktaları olarak ele alınacak.
