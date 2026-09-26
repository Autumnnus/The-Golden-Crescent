# B2/B3 — Ekonomi, üretim yöntemleri ve devlet binaları

**26 Eylül 2026 · etkin.** [Denge önerisi](../../../docs/scenario/DENGE_KURULUM_ONERISI.md) üzerine kullanıcı kararları:
- Rûm toplam ekonomide dünya birincisi, İsfahan kişi başında birinci.
- Demiryolu yalnız kanondaki kısa maden ve liman hatları.
- İsfahan, Rûm ve Mısır başrol.

Kurallar [targets.yml](targets.yml) dosyasında (elle yazılır). [plan.py](plan.py), [B0 modelini](../balance_b0_model/README.md) kullanarak bunları [plan.yml](plan.yml) dosyasına çevirir (üretilir). B1 gruplarındaki 183 ülke kapsamdadır; Japonya, Kore, merkezsizler ve "geri kalan dünya" değişmedi.

## Yöntem

Planlayıcı adımları sırayla şöyle:
1. **Üretim yöntemleri:** 1. kademe gruplar (başroller ve İslam çekirdeği), vanilla'nın 1. kademe İngiltere'si gibi ileri yöntemlere geçti: dikiş makinesi veya boya atölyesi, torna, çelikten alet, atmosferik pompa, keresteci bıçkısı, dikey dosya dolabı, felsefe bölümü, demir iskelet. Toplam 1.251 seviye. Diğer gruplar yöntemlerini korudu.
2. **Kanon tabanı:** [Ekonomi belgesindeki](../../../docs/scenario/ekonomi_ve_toplum.md) sanayi havzaları için asgari seviyeler (`canon_minimum`) kuruldu. Hiçbir kesim bu tabanın altına inmez:
   - İsfahan–Kaşan–Şiraz: 12 dokuma, 10 ipek, 10 kâğıt, 8 cam, 3 kimya.
   - Tebriz: 14 alet, 8 demir madeni, 4 silah.
   - Kahire–İskenderiye: 24 dokuma, 24 pamuk, 6 kâğıt, 4 tersane, 6 gıda.
   - Marmara–Bursa ve Ereğli: 30 dokuma, 30 alet, 12 çelik, 36 kömür, 12 tersane.
   - Endülüs, Lehistan, Londra ve İsveç'e de küçük tabanlar verildi.
3. **Katma değer hedefi:** Ülkeler kişi başı hedefe getirildi (fazlası kesildi, eksiği büyüme karışımıyla kuruldu). Kurallar:
   - Hiçbir ülke Rûm'un %90'ını geçemez.
   - Başrol ülkeler hedeflerinin en az %97'sine çıkar.
   - Altyapıya sığmayan başrol ülkesinde, altyapı başına az değer üreten seviyeler çok değer üretenlerle değiştirilir; karışımın oranları korunur.
4. **Pazar kapanışı:** Önce tüketim fazlası kesildi: giyim, mobilya, gıda ve cam pazar talebinin 1,1 katına indi. Dünya genelinde o maldan açık varsa ihracat için 1,8 katına izin verildi. Sonra girdi açıkları, girdi başına en az 0,55'e kapatıldı; kumaşta 0,45, odunda 0,50. Bir seviye ancak üretiminin en az yarısı gerekiyorsa eklendi.
5. **Devlet binaları:** Aşağıdaki tabloda.
6. **Altyapı:** Kapasiteyi aşan state'lere önce liman eklendi; hâlâ aşıyorsa altyapı başına en az değer üreten seviyeler kesildi.

Her seviye eklemede şu sınırlar denetlendi:
- izinli ürün ve kaynak yatağı;
- paylaşılan ekilebilir alan;
- iş sayısı state nüfusunun %26'sını aşmaz;
- altyapı.

## Sonuç

| | Vanilla | Önce (B1) | Sonra |
|---|---:|---:|---:|
| Bina seviyesi | 8.783 | 14.218 | 11.689 |
| Katma değer (M£/hafta) | 4,06 | 7,67 | 4,91 |
| Altyapısı yetmeyen state | 9 | 34 | **0** |
| Bürokrasi açığı olan ülke | 24 | 38 | 10 (kapsam dışı) |
| Üniversite / demiryolu / inşaat puanı | 70 / 18 / 262 | 105 / 39 / 441 | 157 / 19 / 433 |

**Başlıca ekonomiler:**

| Ülke | Katma değer | Pay | Kişi başı | Bina/M | Bürokrasi (üretim/gider) | İnovasyon | İnşaat |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Rûm** | 467k | %9,5 | 16,0 | 28 | 4.845 / 1.578 | 88 | 70 |
| Jiangnan | 413k | %8,4 | 2,8 | 5 | 7.500 / 6.250 | 50 | 4 |
| Endülüs | 211k | %4,3 | 12,1 | 25 | 1.400 / 847 | 65 | 35 |
| Lehistan–Litvanya | 198k | %4,0 | 6,5 | 13 | 1.420 / 1.143 | 54 | 0 |
| Bengal | 198k | %4,0 | 3,9 | 7 | 2.550 / 2.106 | 54 | 2 |
| **Mısır** | 173k | %3,5 | 15,1 | 27 | 1.140 / 565 | 68 | 35 |
| Gurkanî | 160k | %3,3 | 4,0 | 9 | 1.670 / 1.389 | 54 | 4 |
| **İsfahan** | 150k | %3,0 | **18,7** | 31 | 1.075 / 421 | **110** | 30 |
| Londra | 134k | %2,7 | 9,4 | 37 | 860 / 712 | 56 | 40 |
| Tebriz | 80k | %1,6 | 17,8 | 26 | 555 / 219 | 62 | 20 |

Bengal ile Gurkanî'nin bugünkü değeri, hedeflerinin (kişi başı 7) altında kaldı. Bunu kırpma değil, vanilla'nın altyapı kuralı belirledi: 20 milyonluk bir state'in nüfustan gelen altyapısının da bir tavanı vardır. İsfahan hedefin %93'ünde durdu; dört state'ine sığan en yoğun sanayi bu. Yine de bağımsız ülkeler arasında kişi başında birinci.

**Devlet binaları:**

| Bina | Kural | Sonuç |
|---|---|---|
| Üniversite | Listelenen toplamlar | İsfahan 40, Rûm 25 (önce 43), Mısır 12, Endülüs 10, Tebriz 8, Londra 6, Gurkanî 4, Bengal 4, Lehistan 4, İsveç 3, Paris 3. İnovasyon: İsfahan 110 > Rûm 88 > Mısır 68 |
| Demiryolu | Kanondaki hatlar | Rûm 12 (Ereğli ve İzmir kömürü, İstanbul, Bursa), Mısır 3 (Aşağı Mısır), İsfahan 2, Tebriz 2. Başka yerde yok. |
| İnşaat | Listelenen puanlar, demir iskelet | Rûm 190 → 70, Mısır 35, Endülüs 35, İsfahan 30, Tebriz 20 |
| Hükümet idaresi | 1. kademede bürokrasi gideri ×1,5, diğerlerinde ×1,2 (kurum giderleri modelde yok) | +472 seviye; kapsamdaki bütün ülkeler fazla veriyor |
| Liman | Kıyısı olan her ülkeye en az bir; altyapı eksiğinde fazlası | 49 ülkeye ilk liman; altyapı için 33 liman seviyesi |

**Dünya malları** (arz/talep; vanilla parantez içinde):
- kumaş 0,62 (0,40), odun 0,56 (0,44);
- alet 1,48 (1,05), demir 0,69 (0,75), kömür 0,95 (1,19), kâğıt 0,69 (0,83), çelik 1,14 (0,96);
- cephane 0,66 (1,22);
- tahıl 1,00 (0,73), giyim 0,94 (0,64), mobilya 0,82 (0,64), gıda 0,99 (0,64).

Temel tüketim malları vanilla'dan biraz daha bol. Önceki oyun testlerindeki kötü hayat standardına karşı bu bilinçli bir tercih.

## İkinci tur (26 Eylül, oyun testi sonrası)

**Oyun testinden gelen gözlemler:**
- patlayıcı fabrikası hiç yok (Rûm, İsfahan ve başka yerlerde);
- kömür ve alet az üretilmiş;
- Endülüs başta olmak üzere bazı ülkelerde hayat standardı düşük.

**Nedenler:**
- Kapanış tabanı (0,55) oyunda pahalı girdi ve düşük ücret demekti.
- "Seviye ancak üretiminin yarısı gerekiyorsa" kuralı, 20 birimlik patlayıcı talebine 50 birimlik fabrika kurdurmadı. Oysa tamamen eksik girdi, binaya üretiminin %75'ini kaybettirir.
- Kapsam dışı ülkelerde kapanış hiç yapılmıyordu.

**Değişiklikler** (bu tur, birinci turun etkin dünyasına uygulanır; plan.yml farkı ondan hesaplar):
- **Girdi tabanı:** 0,9 oldu; kumaş 0,6, odun 0,8.
- **Tüketim tabanı:** giyim, mobilya ve gıda için 0,7 (hayat standardı).
- **İlk seviye:** Hiç üretilmeyen bir girdiye en az bir seviye kurulur.
- **Kumaş üreticisi:** Seviye başına en az 10 kumaş veren üretici sayılır. Koyun çiftliği olmayan hayvancılık çiftliği 5 kumaş verir ve kumaş için sayılmaz.
- **Yer açma:** Altyapısı dolu pazarda, fazla veren malın (ör. tahıl) en az değerli seviyesi eksik üreticiye yer açar. Başrol ülkeler ve Endülüs bundan muaf; altyapıları ihracat sanayisini taşıyor.
- **Girdi fazlası:** Dünya fazla verirken bir pazar talebinin 2 katından fazlasını tutamaz. Başrol ülkeler ve Endülüs ihracatçı sayılıp muaf tutulur.
- **Dünya kapanışı:** Pazarların kendi içinde kapatamadığı açık (Mısır'ın kömür ve demiri, kanon: "yakıt ithal"), hedef tavanlarını aşmadan ihracatçı gruplarda üretilir: Rûm, Mısır, İslam çekirdeği, Londra, Avrupa üstü.
- **Taban ülkeler:** Endülüs ve Tebriz de hedefin en az %97'sine büyür.
- **Kapsam:** Japonya, Kore, Maratha gibi gruplar dışındaki örgütlü ülkeler yalnız kapanışa katılır; hedefleri ve yöntemleri değişmez.
- **Temizlik:** Teknolojisi olmayan devralınmış bina (Lourenço Marques limanı) kaldırıldı.

**Sonuç** (B0):
- Bina seviyesi 11.689 → 13.353; katma değer 4,91 → 6,18 M£.
- Dünya: kumaş 0,65, odun 0,81, alet 1,65, demir 0,78, kömür 1,04, kâğıt 0,91, çelik 1,24, cephane 0,98; giyim 1,06, mobilya 1,03, gıda 0,94.
- Patlayıcı ve cephane fabrikası: Rûm, Mısır, Endülüs, Tebriz ve İsfahan pazarlarında.
- Endülüs: 217k → 306k katma değer (kişi başı 16,1); 13 kömür madeni, 11 alet atölyesi, 3 çelik tesisi.

| Ülke | Katma değer | Kişi başı |
|---|---:|---:|
| Rûm | 520k (dünya 1.) | 17,8 |
| İsfahan | 151k | **18,8** |
| Mısır | 207k | 18,0 |
| Endülüs | 306k | 16,1 |
| Jiangnan | 426k | 2,8 |
| Lehistan | 245k | 8,1 |
| Londra | 156k | 11,0 |

**Kalan açıklar:** Madeni ya da pamuğu olmayan küçük pazarlarda 84 derin kıtlık kaldı (arz/talep < 0,4). Çoğu demir ve kumaş; dünyada da bu iki mal vanilla düzeyinde kıt olduğundan ithalatla tam kapanmaz.

## Üçüncü tur (26 Eylül, oyun testi sonrası)

**Oyun testinden gelen gözlemler:**
- M4 donanmalarının çoğunda donanma yönetimi binası yok, gemilerin mürettebatı eksik;
- Endülüs ve Rûm başta olmak üzere kalabalık state'lerde pazar erişimi düşük;
- Rûm'un Fas'taki tek şehirlik toprağında (Rif) liman yok.

**Nedenler:**
- Planlayıcı state'leri modeldeki altyapı arzının tam sınırına kadar dolduruyordu (Beira 71,5/73, Yukarı Endülüs 78/79). Model motoru birebir hesaplamadığı için küçük bir sapma pazar erişimini düşürüyordu.
- Modelde kara bağlantısı yoktu. Pazar başkentine de limanlı bir state'e de karadan bağlanmayan state pazardan kopar (`concept_isolated_state`).

**Değişiklikler:**
- **Donanma yönetimi:**
  - Seviye başına 1.000 denizci; fırkateyn 500, hat gemisi 800 mürettebat ister.
  - Her donanmaya M4 filolarının mürettebatının ×1,15'i kadar seviye kuruldu, filonun ana state'lerine: +284 seviye.
  - İhtiyacın 1,6 katından fazlası (vanilla Britanya'nın 136 seviyesi gibi) ×1,15'e indirildi: −219 seviye.
  - M4 artık `admiralty` teknolojisi olmayan ülkeye donanma vermiyor. Buenos Aires ve Panama'nın birer fırkateyni ile iki amiral kalktı.
  - 137 filonun hepsinin mürettebatı karşılanıyor.
- **Kopuk paylar:** 11 kıyı payına liman kuruldu, aralarında Rûm'un Rif'i, Kırım'ın Kuban'ı, Endülüs'ün Nikaragua'sı ve Batı Hint adaları var. 6 pay düzeltilemedi: kıyısızlar (Bavyera'nın Ren bölgesi gibi) ve liman işçisine yetecek nüfusu olmayanlar.
- **Altyapı tamponu:** Kullanım, pazar başkenti eki sayılmadan hesaplanan arzın en çok %85'i. Açık olan yerde sırayla şunlar yapıldı:
  1. Demiryolu teknolojisi olan ülkeye hat (kullanıcı isteği; önceki "az hat" kararının yerine geçti).
  2. Kıyıdaysa en çok 8 seviyeye kadar liman.
  3. Hâlâ açıksa en az değerli seviyelerin kesimi.

  Toplam +35 hat, +151 liman seviyesi, 1.101 kesim. Kesimler çoğunlukla demiryolu teknolojisi olmayan kalabalık devletlerde (Bengal, Gurkanî, Jiangnan) oldu.

**Sonuç:**
- **Dünya:** 13.205 bina seviyesi, 6,05 M£ katma değer; 54 demiryolu, 582 liman, 505 donanma yönetimi seviyesi.
- **Altyapısı yetmeyen state:** 0.

| Ülke | Katma değer | Kişi başı | Demiryolu | Liman | Donanma yönetimi |
|---|---:|---:|---:|---:|---:|
| Rûm | 519k (dünya 1.) | 17,8 | 20 | 59 | 39 |
| Endülüs | 307k | 16,2 | 10 | 13 | 42 |
| Mısır | 208k | 18,1 | 6 | 2 | 19 |
| İsfahan | 178k | **22,3** | 10 | 6 | 6 |
| Tebriz | 100k | 22,2 | 8 | — | — |

## Doğrulama

[verify.py](verify.py) şunları denetler:
- yalnız binalar değişti;
- rapor planla aynı;
- kapsamdaki ülkelerde teknolojiye aykırı bina veya yöntem yok;
- toplamda Rûm, bağımsız ülkeler arasında kişi başında İsfahan birinci;
- başrol ülkeler hedeflerinin en az %90'ında;
- demiryolu ve üniversite toplamları hedefte;
- inovasyon sırası İsfahan > Rûm > Mısır;
- kapsamda altyapı ve bürokrasi açığı yok;
- dünya girdileri 0,5'in üstünde, tüketim malları 1,3'ün altında;
- yeni uyarı yok.

Etkinleştirme sonrası:
- `check`: yalnız bilinen 168 `localization/replace` tekrarı, 0 uyarı;
- siyasi denetim geçti;
- araç testleri 123/123. Oyunda sınanmadı.

**Sınırlar:**
- **Statik model:** B0 fiyat, kâr ve istihdam doluluğunu hesaplamaz; ticaret akışı yalnız "dünya açığı varken ihracat" kuralıyla temsil edildi. Rakamlar oyun açılışında birkaç hafta içinde değişecektir.
- **Bürokrasi:** Modelde kurum giderleri yok; oyundaki gerçek açık biraz daha büyük olabilir.
- **Eski paketler:** M3-lite ve Rûm 1B.2'nin bina seviyeleri bu paketle yeniden ölçeklendi. O paketlerin planları artık etkin dünyayı birebir anlatmaz.

```sh
cp world/scenario.yml build/balance/b2-source.yml; cp build/world-political/active-political-report.json build/balance/b2-source-report.json
python3 scenarios/atlas/balance_b2_economy/plan.py
python3 scenarios/atlas/balance_b2_economy/prepare.py
python3 scripts/tools.py atlas scenario validate build/balance/b2-candidate.yml
python3 scripts/tools.py atlas scenario build build/balance/b2-candidate.yml --out build/scenarios/b2-candidate
python3 scenarios/atlas/balance_b0_model/measure.py --report build/scenarios/b2-candidate/scenario-report.json --name b2
python3 scenarios/atlas/balance_b2_economy/verify.py
# etkinleştirme: cp → atlas build → atlas scenario report → vanilla_overrides.py → d3 build.py → m4 build.py → atlas check
```
