# M4 — Ordu ve donanma kurulum önerisi

**26 Eylül 2026 · karara bağlandı ve etkin ([M4](../../scenarios/atlas/mechanics_m4_military/README.md)).** Kullanıcı kararları: orta ölçek (yaklaşık 2.700 tabur), bütün dünya tek pakette, komutanlar dahil, en büyük donanma Endülüs'te (koloni imparatorluğu). Aşağıdaki metin öneri kaydıdır; gerçek sayılar paket README'sindedir.

## 1. Tespit: dünyanın büyük kısmı ordusuz

Etkin raporda (468 ülke) toplam **964 tabur ve 98 gemi** var. Vanilla 1836 başlangıcında yaklaşık 3.900 birlik vardır (Çin 486, Rusya 350, Britanya 317, Fransa 261, Osmanlı 190). Var olan birlikler de çoğunlukla sahibi değişmiş vanilla kalıntılarıdır: Japonya 58, Mısır 68, Awadh 49, Haydarabad 34, Burma 34.

**Sıfır taburla başlayan başlıca ülkeler:**

| Grup | Ülkeler |
|---|---|
| İslam dünyasının büyükleri | Rûm, İsfahan ve bütün İran üyeleri, Tebriz, Endülüs, Fas, Tatar Hanlığı, Uygur Hanlığı, Buhara, Hokand, Sokoto |
| Avrupa | Lehistan–Litvanya, Paris ve beş Fransız devleti, Londra, İskoçya, İrlanda, Bohemya, Kastilya, Aragon, Galiçya, Venedik, Milano, Ren, Moskova, Novgorod, İsviçre |
| Asya | Beş Çin devleti (Jiangnan 150 M, Kuzey Çin 94 M...), Bengal (50 M), Maratha, Tamil, Kore, Mançurya, Dai Nam, Siam |
| Koloniler | Yeni Endülüs, İnci Adaları, Virginia, Yeni İngiltere, Yeni Hollanda |

Rûm için hazırlanmış 1B.3 ordu paketi (160 tabur, 48 gemi, [README](../../scenarios/atlas/phase01b3_rum_military/README.md)) hiç etkinleşmedi. Endülüs'ün sömürge imparatorluğu, Umman ve Mısır'ın Hint Okyanusu filoları ve Kalmar'ın Baltık gücü denizde temsil edilmiyor. Oyunda bu durum, AI'ın başlangıçta savunmasız büyük güçlere savaş açmasına ve sömürge rotalarının anlamsızlaşmasına yol açar.

## 2. İlkeler

1. **Büyüklük nüfus, kademe ve role göre.** Taban kural her 100 bin kişiye yaklaşık 0,4–1 tabur. Profesyonel ordulu İslam çekirdeği üst uçta; yerel levent/milis düzeni alt uçta. Çin devletleri kalabalık ama düzensizdir.
2. **Birlik türü teknolojiyle uyumlu.** Atlas birlik/teknoloji uyumunu zaten denetliyor. İleri ülkelerde avcı piyade (`skirmish_infantry`), hüssar ve seyyar topçu; orta kademede hat piyadesi ve topçu; geri kademede düzensiz piyade ve süvari.
3. **Ordu yerleşimi senaryoya göre.** Kuvvetler sınırlara ve rakiplerin karşısına konur: Rûm'un Balkan ordusu Lehistan'a, İsfahan'ın doğu ordusu Horasan–Afgan geçitlerine, Uygur'un Gansu garnizonu Kuzey Çin'e karşı.
4. **Donanma rotaları hikâyeyi taşır.**
   - Rûm Akdeniz'de (Sicilya, Sardinya ve Septe üsleri).
   - Endülüs Atlantik ve Karayipler'de.
   - Fas Atlantik ve Brezilya hattında.
   - Mısır ile Umman Kızıldeniz, Hint Okyanusu ve Malay boğazlarında.
   - Kalmar Baltık'ta; Londra Manş'ta ve kolonilerinde.
   - Venedik ve Ceneviz Adriyatik'te ve Tiren'de; Yue ile Japonya Doğu Asya kıyılarında.
5. **Ekonomiyle tutarlılık.** Kışla, deniz idaresi, silah, top ve mühimmat sanayisi ile ordu kanunları (profesyonel ordu, köylü milisi, zorunlu askerlik) ordu büyüklüğüyle çelişmemeli. 1B.3'teki tedarik denetimi yöntemi bütün paketlere genişletilir.
6. **Kalıntı temizliği.** Avusturya ve Mısır'daki bozuk formasyonlar düzeltilir. Sahibi değişen topraklarda yanlış bayraklı kalan vanilla birlikleri yeniden yazılır.

## 3. Önerilen büyüklükler (tartışma taslağı)

| Güç | Kara (tabur) | Deniz (gemi) | Not |
|---|---:|---:|---|
| Rûm | 160 | 48 | 1B.3 paketi yeniden kullanılır; Sicilya–Septe filosu eklenebilir |
| İsfahan + İran kuklaları | 90 + 60 | 10 | Tebriz topçu ve hassas imalat ağırlıklı |
| Mısır | 80 (68'den) | 25 | Kızıldeniz ve Hint Okyanusu filosu |
| Endülüs + koloniler | 90 + 40 | 45 | Atlantik–Karayip filosu, Yeni Endülüs garnizonu |
| Fas + koloniler | 45 + 15 | 15 | |
| Tatar Hanlığı | 60 | — | Süvari ağırlıklı |
| Uygur Hanlığı | 45 | — | Gansu ve Cungarya garnizonları |
| Gurkanî | 90 | 5 | |
| Umman | 15 | 20 | Zanzibar ve Maskat filoları |
| Lehistan–Litvanya | 150 | 8 | Avrupa'nın en büyük kara ordusu |
| Paris + Fransız devletleri | 70 + 60 | 25 | |
| Londra–İskoçya–İrlanda | 60 | 80 | Kıta sömürge ağı olmadan |
| Kalmar (İsveç, Danimarka, Norveç) | 30 + 20 + 15 | 20 + 15 + 10 | |
| Çin'in beş devleti | 60–150 arası (düzensiz) | 5–20 | Jiangnan ve Yue kıyı filoları |

Tablodaki güçler yaklaşık 1.700 tabur ve 400 gemi eder; dünyanın kalanıyla toplam hedef vanilla ölçeğine yakın, yaklaşık 3.500 tabur olur.

## 4. Uygulama sırası (her dilim ayrı aday, doğrulama, etkinleştirme)

- **M4a — İslam çekirdeği ve rakipleri:** Rûm, İran, Mısır, Endülüs, Fas, Umman, Tatar, Uygur, Gurkanî ve bunların kolonileri.
- **M4b — Avrupa:** Lehistan, Fransız devletleri, Britanya tacı, Kalmar, Almanya ve İtalya, Macaristan, Moskova.
- **M4c — Asya ve Afrika:** Çin devletleri, Kore, Güneydoğu Asya, Hindistan'ın kalanı, Sahel ve Etiyopya.
- **M4d — Tedarik ve kanun denetimi:** kışla, deniz idaresi ve askerî sanayi seviyeleri; ordu kanunları; bozuk formasyon temizliği.

Komutan ve amiral karakterleri ayrı bir iştir (karakter geçmişi Atlas dışında). İstenirse M4e olarak eklenebilir.

## 5. Kullanıcı kararı gereken sorular

1. **Genel ölçek:** vanilla'ya yakın mı (~3.500 tabur), daha küçük mü (~2.000), yoksa İslam güçleri belirgin üstün mü?
2. **Başlangıç kapsamı:** önce M4a mı, yoksa bütün dünya tek pakette mi?
3. **Komutan/amiral karakterleri:** bu aşamada eklensin mi?
4. **Donanma dengesi:** Endülüs mü, Rûm mu dünyanın en büyük İslam donanması?
