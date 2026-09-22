# Faz 1B.3 — Rûm silahlı devleti

**13 Eylül 2026. Statik ve kümülatif Atlas önizlemesi; etkin veya oynanabilir sürüm değildir.**

Bu paket Faz 1A sınırlarını, Faz 1B.1'in 27 milyonluk nüfus/hukuk katmanını ve Faz 1B.2'nin özgürleşme/ekonomi omurgasını aynen taşır. Yeni kapsam yalnız Rûm'un hükümet koalisyonu, profesyonel ordu ve donanması ile bunların ilk askerî sanayi zinciridir. Kaynak [scenario.json](scenario.json), okunabilir karar kaydı [military-plan.json](military-plan.json), gerçek oyun tanımlarından hesaplanan tedarik denetimi [military-capacity-audit.json](military-capacity-audit.json), kabul sonucu [verification.json](verification.json).

## Başlangıç hükümeti

Rûm kabinesi üç vanilla çıkar grubundan oluşur:

- `ig_landowners`: hanedan sarayı ve merkezle uzlaşmış mülk sahibi seçkinlerin en yakın oyun karşılığıdır.
- `ig_armed_forces`: ücretli merkez ordusunu temsil eder.
- `ig_intelligentsia`: meslek bürokrasisi, hukukçu ve teknik reform kadrolarını temsil eder.

Kent sanayicileri gümrük koruması karşılığında koalisyonu dışarıdan destekler; başlangıç kabinesinde değildir. Kalıcı siyasi güç çarpanı verilmedi. Atlas POP serveti, bina sahipliği, liderler ve mutlak clout sonucunu simüle etmediği için yapay bir yüzde üretmek yerine motor ölçümü bırakıldı.

## Ordu ve donanma

| Kuvvet | Bileşim | Toplam |
|---|---:|---:|
| Balkan Ordusu | 50 avcı piyade, 8 hüssar, 8 seyyar topçu | 66 tabur |
| Anadolu Ordusu | 44 avcı piyade, 7 hüssar, 7 seyyar topçu | 58 tabur |
| Irak ve Levant Ordusu | 26 avcı piyade, 5 hüssar, 5 seyyar topçu | 36 tabur |
| Marmara Donanması | 12 hat gemisi, 14 fırkateyn | 26 gemi |
| Ege ve Levant Donanması | 8 hat gemisi, 14 fırkateyn | 22 gemi |

Toplam **160 profesyonel tabur** ve **48 gemi** vardır. Bu, aynı vanilya kaynağından türeyen Faz 1B.2 raporundaki Avusturya'nın 129 ve Prusya'nın 128 taburundan büyük, Fransa'nın 187 taburundan küçüktür. Donanma Mısır'ın 14 gemisini aşar; Fransa'nın 74 ve Britanya'nın 196 gemilik ağından küçüktür. Böylece “Akdeniz'de ciddi güç, küresel okyanus ağı değil” hedefi sayısal karşılık bulur.

Ordu 120 `combat_unit_type_skirmish_infantry`, 20 `combat_unit_type_hussars` ve 20 `combat_unit_type_mobile_artillery` kullanır. Atlas teknoloji öncüllerini tamamlayarak `general_staff` ve `napoleonic_warfare` tanımlarını doğruladı. Yeni nesil zırhlı, makineli veya geç oyun birlikleri eklenmedi.

## Askerî tedarik ve mali baskı

Konstantiniyye havzasına 3 top dökümhanesi, 5 mühimmat fabrikası, 3 patlayıcı fabrikası ve 2 ek gübre/kimya seviyesi eklendi; Skopia demiri 30'dan 32 seviyeye çıktı. Mevcut Rûm bina toplamı **1.246 seviye** oldu.

Tam istihdamlı açık üretim yöntemleri, oluşumların tanımlı mal girdileri çıkarıldıktan sonra 360 küçük silah, 130 mühimmat, 35 top, 3.472 tahıl ve 135,2 sert kereste yönsel kapasitesi bırakır. Patlayıcı +50, demir +25, kükürt +30 ve alet +15 ile zincirin dar payları özellikle korunmuştur. Bunlar stok, fiyat, kârlılık veya gerçek işe alım garantisi değildir. Boya, kumaş, et, ipek ve odun dış bağımlılıkları Faz 1B.2 ile aynı kalır.

160.000 azami kara personeli ve 30.000 azami gemi mürettebatı, oyun motorunda maaş ve mal gideri yaratacaktır. Atlas V2 ülke şemasında başlangıç hazinesi, borç, faiz veya güvenli ham etki alanı yoktur. Bu nedenle yazılı savaş borcu sahte bir değişkenle kodlanmadı. Başlangıç borç anaparası, Atlas'a doğrulanmış bir sözleşme eklenmesi veya ayrı güvenli başlangıç mekaniği kararı bekler.

## Yeniden üretme ve doğrulama

Mod kökünde:

```sh
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b3_rum_military/prepare.py
python3 scripts/tools.py atlas scenario validate scenarios/atlas/phase01b3_rum_military/scenario.json
python3 scripts/tools.py atlas scenario report scenarios/atlas/phase01b3_rum_military/scenario.json --out build/phase01b3/report.json
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b3_rum_military/audit.py
python3 scripts/tools.py atlas scenario build scenarios/atlas/phase01b3_rum_military/scenario.json --out build/phase01b3/generated
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b3_rum_military/verify.py
python3 scripts/tools.py atlas preview --scenario scenarios/atlas/phase01b3_rum_military/scenario.json --region RUM,BOS,ALB,BUL,ADA,ERZ,TRB,KUR,BSR,SYR,LEB,PAL,KUW --out build/maps/phase01b3-rum.html
```

Doğrulama; gerçek birlik/gemi/IG/teknoloji/PM/karargâh kimliklerini, kıyı ve eyalet sahipliğini, kaynak sınırlarını, oluşumların derlenmiş sayısını, hükümet scriptini, askerî mal kapasitesini ve 452 başka ülkenin değişmemesini kontrol eder. Önceki uyarı listesine yeni uyarı eklenmedi. Oyun motoru çalıştırılmadı ve `world/` etkinleştirilmedi.

## Sonraki iş — Faz 1B.4

Rûm çekirdeği için motor kapıları açık bırakılarak bölgenin diğer 12 ülkesine geçilecek. Nüfus, ekonomi, hukuk/kurum, hükümet ve askerî ölçek ülke kümeleri halinde hazırlanacak. Öncelik altı Nizam bağlısının kendi ekonomik/askerî kapasitesidir; sonra bağımsız Kürdistan–Basra–Suriye–Lübnan–Filistin–Kuveyt kuşağı gelir. Aynı fazda Basra/Trabzon/Tırnova şehir-hub sorunları ve Nizam bağlılık prototipi ayrı kabul kapıları olarak korunur.
