# Faz 1B.4B — Bağımsız Ortadoğu ara kuşağı

**13 Eylül 2026. Statik ve kümülatif Atlas önizlemesi; etkin veya oynanabilir sürüm değildir.**

Bu paket Faz 1B.4A'yı korur; Kürdistan, Basra, Şam, Cebel-i Lübnan, Kudüs ve Kuveyt'i nüfus, okuryazarlık, hukuk, kurum, hükümet, ekonomi ve askerî kapasite bakımından doldurur. Altı ülke bağımsız kalır. Kaynak [scenario.json](scenario.json), karar kaydı [belt-plan.json](belt-plan.json), vanilla scriptlerinden hesaplanan kapasite [capacity-audit.json](capacity-audit.json), kabul sonucu [verification.json](verification.json).

## Başlangıç profilleri

| Ülke | Nüfus | Bina | Kara / deniz | Ekonomik ve siyasî rol |
|---|---:|---:|---:|---|
| Kürdistan Emirliği | 1.700.000 | 68 | 22 / 0 | Musul–Diyarbakır geçitleri, kömür/kükürt, tarım ve sınır ordusu |
| Basra Cumhuriyeti | 320.000 | 20 | 8 / 3 | H7 tüccar meclisi, kâğıt, alet, tersane ve Şattülarap ticareti |
| Şam Emirliği | 1.170.000 | 62 | 16 / 0 | Kervan–kent üretimi, tahıl, dokuma, kâğıt ve güney geçitleri |
| Cebel-i Lübnan Emirliği | 560.000 | 41 | 8 / 3 | Dağ meclisi, Beyrut limanı, ipek, kömür ve palanga |
| Kudüs Emirliği | 650.000 | 42 | 10 / 3 | Çok cemaatli vakıf düzeni, demir/kükürt, alet ve Akka kıyısı |
| Kuveyt Emirliği | 120.000 | 9 | 4 / 4 | Küçük Körfez limanı, balıkçılık, tersane ve ticaret filosu |

Toplam **4.520.000 kişi, 242 bina seviyesi, 68 tabur ve 13 fırkateyn** vardır. 447 diğer ülke Faz 1B.4A ile aynıdır. Fazın bütün yeni kimlikleri ve teknoloji önkoşulları kurulu vanilla kaynaklarından doğrulandı; önceki 77 nota yeni statik uyarı eklenmedi.

## Hukuk ve kurumlar

Basra yazılı H7 profilinin oyun karşılığıdır: başkanlık cumhuriyeti, oligarşi, seçilmiş bürokratlar, vicdan özgürlüğü, profesyonel ordu, serbest ticaret, laissez-faire, özel okullar, hayır sağlık sistemi, kadınların mülkiyet hakkı ve kölelik yasağı. Tüccar/imalatçı ile kent küçük mülk sahipleri başlangıç koalisyonundadır. Bu temsil genel oy veya demokratik kitle siyaseti değildir.

Diğer beş ülke H8 bölgesel hanedan temelini kullanır: monarşi, yerel/hanedan idaresi, köylü levazımı, gelenekçilik, merkantilizm, toprak vergisi, kiracı çiftçilik, dinî okullar ve dar siyasî alan. Ülke farkları korunur:

- Lübnan ve Kuveyt, mutlak otokrasi yerine ileri gelenler oligarşisine sahiptir.
- Lübnan ve Kudüs atanmış bürokrasi kullanır.
- Kudüs'ün çok cemaatli vakıf sözleşmesi devlet dini yerine vicdan özgürlüğüyle temsil edilir.
- H8 başlangıcında borç/ev içi kölelik yasaldır; bu ülkeler Basra'nın ilgasını otomatik miras almaz.

Basra'da devralınmış **3.530 köle statüsü** kültür ve din korunarak köylüye çevrildi. Beş H8 ülkesinde devralınan 29.047 kişilik köle statüsü oranlarla birlikte korundu; yeni nüfus toplamlarına ölçeklenince oyun çıktısında 46.267 kişi olur. Bu, kurucu dünyanın ahlaken olumlanan bir unsuru değil, yazılı H8 hukukunun başlangıç çatışmasıdır.

## Ekonomi ve karşılıklı bağımlılık

Altı ülkenin tam istihdamlı açık üretim yöntemleri birlikte değerlendirildiğinde tahıl, kömür, balık, cam, gıda, kâğıt, küçük silah, kükürt, alet, dokuma ve palanga üretimi pozitiftir. Bölgesel kuşak top, kumaş, sert kereste, demir ve büyük miktarda odun ithal eder. Bu, Rûm, Mısır ve İran arasındaki transit/borç/tarife siyasetini ekonomik olarak anlamlı tutar.

[capacity-audit.json](capacity-audit.json) her ülkenin sanayi girdisi, çıktısı ve birlik bakımını ayrı hesaplar. Piyasa fiyatı, kâr, ücret, gerçek istihdam, altyapı, tarife, ticaret rotası ve konvoy davranışı statik raporun kapsamında değildir.

## Basra–Kuveyt liman sınırı

Vanilla `STATE_BASRA` yalnız bir şehir ve bir liman hubına sahiptir. Doğrulanmış `x807060` şehir hubı Basra Cumhuriyeti'nde, `x00F060` liman hubı Kuveyt Emirliği'ndedir. Bu yüzden Basra şehir idaresi, kâğıt, alet ve tersaneyle; Kuveyt ise gerçek port/fishing binalarıyla temsil edildi. Aynı state-region içinde ikinci bir Basra limanı uydurulmadı.

Basra'nın Şattülarap nehir limanını ve Kuveyt'in Körfez limanını aynı anda ayrı hub olarak göstermek için ileride yeni state-region/province harita bölünmesi gerekir. Bu değişiklik geniş harita uyumluluğu ve motor testi olmadan bu faza sokulmadı.

## Diplomasi sınırı

Altı ülkenin hiçbirine overlord atanmadı. 1712 Şam ve 1804 Bağdat antlaşmaları bağımsızlığı tanır; bunlar otomatik vergi, asker veya sonsuz savaş garantisi değildir. Atlas'ta bunları vassallığa çevirmenin yazılı diplomasiye aykırı olacağı doğrulama ile sabitlendi. Antlaşma krizleri ileride Flavor diyagramı ve açık onay gerektirir.

## Yeniden üretme ve doğrulama

Mod kökünde:

```sh
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b4b_independent_belt/prepare.py
python3 scripts/tools.py atlas scenario validate scenarios/atlas/phase01b4b_independent_belt/scenario.json
python3 scripts/tools.py atlas scenario report scenarios/atlas/phase01b4b_independent_belt/scenario.json --out build/phase01b4b/report.json
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b4b_independent_belt/audit.py
python3 scripts/tools.py atlas scenario build scenarios/atlas/phase01b4b_independent_belt/scenario.json --out build/phase01b4b/generated
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b4b_independent_belt/verify.py
python3 scripts/tools.py atlas preview --scenario scenarios/atlas/phase01b4b_independent_belt/scenario.json --region RUM,BOS,ALB,BUL,ADA,ERZ,TRB,KUR,BSR,SYR,LEB,PAL,KUW --out build/maps/phase01b4b-independent-belt.html
```

Doğrulama; parent hashlerini, nüfus ve bina toplamlarını, kültür–din POP birleşimlerini, köle statülerini, 24'er kanunu, kurumları, hükümetleri, derlenmiş birlikleri, ekonomik bağımlılıkları, Basra/Kuveyt hub sahipliğini, bağımsızlıkları ve 447 başka ülkenin değişmezliğini kontrol eder. Oyun motoru çalıştırılmadı ve `world/` etkinleştirilmedi.

## Sonraki iş — Faz 1B.5

Rûm bölgesinin kümülatif bütünlük denetimi yapılacak: kaldırılan TUR/GRE/ION scope'ları, vanilla başlangıç karakterleri ve journal/on_action referansları, Nizam subject prototipi, Basra/Kuveyt harita bölünmesi kararı ve ilk kontrollü motor testinin kapsamı ayrı kapılar halinde incelenecek. Bu denetim yeni bölge açmadan önce Faz 1B'yi kapatmaya hazırlanır.
