# Denge kurulumu önerisi — teknoloji, kanunlar, binalar ve devlet altyapısı

**26 Eylül 2026 · kararlar verildi; B1 ([teknoloji ve kanunlar](../../scenarios/atlas/balance_b1_tech_laws/README.md)) ile B2/B3 ([ekonomi ve devlet binaları](../../scenarios/atlas/balance_b2_economy/README.md)) etkin.** Kullanıcı dört karar noktasında da önerilen seçeneği seçti. Aşağıdaki metin kararlardan önceki önerinin kaydıdır; uygulamadaki sapmalar paket README'lerindedir: başlangıç serveti değiştirilmedi; güney/doğu Avrupa ve Çin'e hat piyadesi eklendi; Bengal ile Gurkanî altyapı tavanı yüzünden hedefin altında kaldı; bina sayısı ~10.000 yerine 11.689 oldu (kumaş zinciri). Kullanıcı isteği özetle:
- Ordu ve sınır değişikliklerinden sonra pazar ve ekonomi dengesi bozuldu. Denge senaryoya uygun kurulmalı; ana öncelik vanilla'nın dengeyi nasıl tasarladığını anlamak.
- Sıra: kanun ve teknoloji → binalar ve üretim yöntemleri → devlet binaları, üniversite, liman ve demiryolu.
- İslam dünyası önde olacak, ilim merkezi İsfahan en iyisi olacak, Rûm ve diğer Müslüman devletler onu izleyecek.
- Avrupa geride kalacak; İskandinavlar ve Lehistan Avrupa'nın bir adım önünde olacak.
- Bir bina teknolojisi olmayan ülkeye verilmeyecek; girdisi üretilmeyen veya alınamayan bina kurulmayacak.
- Hiçbir devlet gereksiz yere çok güçlü olmayacak.
- İsfahan, Rûm ve Mısır modun başrolleridir; onlara açık bir üstünlük tanınacak, en çok da İsfahan'a.

Ölçümler [B0 ölçüm aracıyla](../../scenarios/atlas/balance_b0_model/README.md) yapıldı: vanilla 1836 ile etkin mod aynı statik modelde. Rakamlar motor sonucu değil, kıyas içindir. Vanilla'nın tasarım kaynakları aracın README'sindedir.

## 1. Vanilla dengeyi nasıl kuruyor?

**Teknoloji kademeleri** (kurulu oyunun `00_starting_inventions.txt` paketleri):

| Kademe | Teknoloji | Neyi açar, neyi kapatır | Vanilla'da kim |
|---|---:|---|---|
| 1 | 52 | Bütün 1. çağ + demiryolu, mekanik alet, atmosferik makine, merkez arşivi (65 bürokrasi/seviye) | İngiltere, Fransa, Prusya, ABD |
| 2 | 44 | 1. çağ + mekanik alet, atmosferik makine | Avusturya, İsveç, Bavyera |
| 3 | 31 | Torna, bankacılık, borsa yok | Rusya, İspanya, Mısır |
| 4 | 20 | Akademi (üniversite) ve kent planlaması (demir iskeletli inşaat) yok | Osmanlı, İran, Çin, Japonya |
| 5 | 10 | Merkezileşme yok: hükümet idaresi 10 bürokrasi/seviyede kalır | Küçük tanınmamışlar |
| 6–7 | 3–0 | Bürokrasi ve imalat yok | Yerel topluluklar |

- **Vanilla, İslam dünyasını bilerek geride başlatır.** Bu senaryo o sırayı tersine çevirmelidir.
- **Bina yoğunluğu** (milyon kişi başına seviye):
  - İngiltere 27,6, ABD 29, İsveç 33;
  - Fransa 18, Prusya 15, Osmanlı 13,5, Mısır 15,8;
  - İran 10,9, Rusya 10,5, Çin 2,8, Japonya 4,3.
- **Önde olmak ileri üretim yöntemi demektir.** İngiltere, Fransa ve Prusya şu yöntemlerle başlar:
  - dikey dosya dolabı: 65 bürokrasi, 20 kâğıt;
  - demir iskeletli inşaat: 5 inşaat puanı;
  - boya atölyeli dokuma;
  - atmosferik pompalı madenler;
  - çelikten alet.
  
  Geri ülkeler ahşap inşaat, elle dikim ve kazma-kürekle başlar. İleri yöntemler kâğıt, çelik, alet ve kömür talebi yaratır; bu talebi aynı pazar karşılar.
- **Devlet binaları:**
  - İngiltere'de 35 hükümet idaresi, 13 üniversite, 40 liman, 13 demiryolu, 9 inşaat sektörü ve 46 ticaret merkezi var.
  - Osmanlı, İran ve Mısır'da hiç üniversite yok.
  - Büyük güçlerin bürokrasisi fazla verir: İngiltere 2.375 üretip 1.355 harcar.
- **Pazar hafif kıtlıkla açılır.** Temel tüketim mallarında dünya arz/talebi 0,6–0,8, kumaşta 0,4, odunda 0,44'tür. Fiyatlar tabanın biraz üstünde başlar ve yatırımı çeker. Aşırı bolluk kârı öldürür, derin kıtlık ise hayat standardını çökertir.

## 2. Modun şu anki durumu

| Ölçü | Vanilla | Mod |
|---|---:|---:|
| Nüfus | 1.022 M | 1.079 M |
| Bina seviyesi | 8.783 | **14.226** |
| Katma değer (M£/hafta) | 4,06 | **7,70** |
| Bürokrasi açığı olan ülke | 24 | 38 |
| Altyapısı yetmeyen state | 12 / 859 | **64 / 679** |
| Üniversite seviyesi | 70 | 105 (43'ü Rûm'da) |
| İnşaat puanı | 262 | 441 (190'ı Rûm'da) |

**Teknoloji istenen sıranın tersinde.** Nüfus ağırlıklı ortalama kademe (1 en ileri):
- İslam çekirdeği 1,4;
- **Avrupa üstü 2,1, Avrupa 2,6;**
- orta düzey İslam 3,05, diğer İslam 4,07.

Mısır 3. kademede; Fas, Gurkanî, Tatar ve Haydarabad 4. kademede. Londra, Bavyera, Avusturya ve Macaristan 2. kademede. İsfahan, Rûm ve Endülüs'le aynı kademede, üstünlüğü yok.

**Güç sırası bozuk.** Katma değere göre ilk sıralar:

| Sıra | Ülke | Payı | Kişi başı | Not |
|---:|---|---:|---:|---|
| 1 | Bengal | %10,4 | 15,9 | M3-lite yoğunlaştırması |
| 2 | Rûm | %10,2 | 26,8 | |
| 3 | Jiangnan | %9,9 | 5,1 | |
| 4 | Gurkanî | %7,7 | 14,8 | 4. kademe teknolojiyle |
| 9 | Haydarabad | %2,9 | 14,4 | Mısır'ın önünde |
| 10 | Mısır | %2,6 | 17,3 | |
| 14 | **İsfahan** | %1,8 | 17,0 | |

Hint Müslüman devletlerine M3-lite'ta Mısır'la aynı yoğunluk verildi. Karşılaştırma için vanilla Hindistan'da kişi başı katma değer 2,5.

**Başrol ülkeler en ilkel yapıda:**
- **İsfahan:** inşaat sektörü, üniversite, alet atölyesi, maden ve kâğıt fabrikası yok; tek limanı var. Dokuma tezgâhlarının hepsi elle dikim, tarlaları basit tarımda, hükümet idaresi 10 bürokrasilik yöntemde. Bürokrasisi 250 üretip 375 harcıyor; 4 state'inin 3'ünde altyapı yetmiyor.
- **Mısır:** ahşap inşaat, elle dikim ve basit tarım; üniversitesi yok.
- **Karşılaştırma:** Londra vanilla İngiltere'nin yöntemlerini kullanıyor.

**Pazarlarda iki tür bozukluk var** (arz/talep; vanilla'da bu mallar 0,6–1,0 arasında):

| Pazar | Kumaş | Odun | Giyim | Mobilya | Alet/demir/kömür | Cephane |
|---|---:|---:|---:|---:|---|---:|
| İsfahan | **0,08** | 0,38 | **3,23** | 2,18 | yok | 0 |
| Mısır | 0,19 | **0,12** | **4,02** | 1,73 | yok | — |
| Rûm | 0,46 | 0,66 | 2,75 | 1,17 | dengede | 0 |
| Endülüs | 0,18 | 0,28 | 1,75 | 1,67 | yok | 0 |
| Bengal | 0,12 | 0,15 | 0,89 | 1,65 | yok | — |

- **Aşırı bolluk:** giyim, gıda ve mobilyada arz talebin 2–4 katı. Fiyatlar tabana iner, fabrikalar kârsızlaşır, işçi çıkarır ve bütçe erir.
- **Derin kıtlık:** kumaş, odun ve ipek bu fabrikaların girdisi. İsfahan'da kumaş talebinin yalnız %8'i üretiliyor; girdi kıtlığı üretimi %50'ye kadar düşürür.
- **Cephane:** dünyada hiç cephane üretilmiyor, M4 ordularının haftalık 339 birimlik ihtiyacı karşılıksız.

**Teknoloji uyumu şu an temiz.** 14.226 seviyede teknolojiye aykırı yalnız bir liman (Lourenço Marques) var, üretim yöntemlerinde ihlal yok. Teknoloji değişince bu denetim yeniden yapılacak.

## 3. Hedef güç hiyerarşisi

Kişi başı katma değer, B0'ın ölçüsüyle. Vanilla'da İngiltere 13,2, Fransa 8,9, Osmanlı 7,3, Çin 1,6.

| Grup | Teknoloji | Kişi başı KD | Bina/M | Not |
|---|---|---:|---:|---|
| **İsfahan** | Kademe 1 + 11 bilim, toplum ve kimya teknolojisi (63) | **20** | 30–35 | Dünyanın en yüksek kişi başı değeri, en güçlü üniversite ağı |
| **Rûm** | Kademe 1 + 7 ağır sanayi ve askerî teknoloji (59) | 15–16 | 30–32 | Toplam ekonomide İslam dünyasının birincisi |
| **Mısır** | Kademe 1 + 5 dokuma, gıda ve denizcilik teknolojisi (57) | 15–16 | 28–30 | Pamuk ve dokuma havzası |
| Tebriz, Endülüs, Basra | Kademe 1 (52–53) | 13–15 | 25–28 | |
| Orta İslam (Gurkanî, Bengal, Levant, Mağrip, İran üyeleri, Tatar, Uygur...) | Kademe 2 (44) | 6–8 | 12–16 | |
| Az gelişmiş İslam | Kademe 3 (31) | 3–5 | 8–12 | |
| **Avrupa üstü** (Lehistan, Kalmar taçları, İskoçya) | Kademe 3 + torna, bankacılık, borsa, deneycilik, Napolyon savaşı (36) | 7–9 | 15–20 | |
| Londra | Kademe 3 + torna, atmosferik makine (33) | 9–10 | 20–25 | Kömürlü sanayi başlıyor; demiryolu yok |
| Diğer batı ve orta Avrupa | Kademe 3 (31) | 5–6 | 12–15 | |
| Güney ve doğu Avrupa, Moskova | Kademe 4 (20–25) | 3–4 | 8–10 | |
| Doğu Asya | **Karar 2** | 2–4 | 4–7 | |
| Diğerleri | Mevcut kademeler | 1–3 | vanilla | |

Bu hedeflerle dünyanın toplam katma değeri yaklaşık 5,1 M£ olur: vanilla'nın %25 üstü, bugünün %34 altı. Seviye sayısı 14.200'den yaklaşık 10.000'e iner.

## 4. Fazlar

### B0 — Ölçüm aracı (hazır)
[measure.py](../../scenarios/atlas/balance_b0_model/measure.py) her fazın adayını vanilla ile karşılaştırır ve kabul ölçütlerini denetler. Bu önerideki bütün sayılar ondan geldi.

### B1 — Teknoloji ve kanunlar
- **Teknoloji paketleri:** bölüm 3'teki tablo.
  - **İsfahan'ın ek teknolojileri:**
    - toplum: anonim şirketler, psikiyatri, eczacılık, modern kanalizasyon, posta tasarrufu, realizm;
    - üretim: kristal cam, kimyasal ağartma, damıtma, konserve, makineli atölye.
  - **Rûm:** mevcut eklere (konserve, makineli atölye, yivli namlu) su borulu kazan, Bessemer, lojistik ve mermi topu eklenir.
  - **Mısır:** konserve, makineli atölye, damıtma, hidrolik vinç ve mermi topu alır.
  - Kanondaki sektör tablosu korunur: Rûm kömür ve makinede, Mısır dokuma ve denizcilikte, İsfahan kimya ve eğitimde öncüdür.
- **Geri alınan teknolojiler:** Avrupa'da teknoloji düşünce, artık kullanılamayan üretim yöntemleri aynı gruptaki en iyi izinli yönteme iner (Londra'nın torna mobilyası, çelik aleti gibi). Kanunlar da denetlenir; örneğin korumacılık borsa ister.
- **Kanunlar:** Kanondaki H1–H10 profilleri korunur. Üç düzeltme yapılır:
  1. Mısır'ın vanilla'dan kalan kanunları H2'ye çevrilir: tarımcılık yerine müdahalecilik, köle ticareti yerine mevcut köleliğin sürmesi (kanon: "dış ticaret kısıtlı"), atanmış memurlar ve yerel polis.
  2. Teknolojisi düşen ülkelerde artık geçersiz kalan kanunlar düzeltilir.
  3. Başlangıç serveti ayarlanır: İsfahan çok yüksek; Rûm, Mısır, Tebriz, Endülüs ve Basra yüksek; orta İslam ve Avrupa üstü orta; diğerleri düşük. Bugün başrol ülkelerde bu ayar hiç yok.
- **Kabul:**
  - teknoloji, üretim yöntemi ve kanun uyumunda sıfır ihlal;
  - kademe ortalaması istenen sırada: İsfahan > Rûm > Mısır > İslam çekirdeği > orta İslam > Avrupa üstü > Avrupa.

### B2 — Üretim binaları ve üretim yöntemleri
- **Yoğunluk:** ülkeler bölüm 3'teki kişi başı hedefe getirilir.
  - Bengal, Gurkanî, Haydarabad ve Avadh'ın M3-lite fazlası kırpılır.
  - Rûm'un 1B.2 sanayi havzaları korunur; tüketim fazlası azaltılır.
  - İsfahan, Mısır ve Tebriz'e kanondaki havzalar kurulur: İsfahan–Kaşan'da eğitim, ipek, kâğıt ve kimya; Kahire–İskenderiye'de pamuklu, kâğıt, tersane ve gıda; Tebriz'de alet ve metal.
- **Üretim yöntemi:** her bina, sahibinin teknolojisinin izin verdiği ve girdisi pazarda bulunan en iyi yöntemi alır. Başrol ülkeler vanilla İngiltere gibi ileri yöntemlerle başlar.
- **Pazar kapanışı:** her pazarda
  - girdi mallarının arz/talebi en az 0,6;
  - tüketim mallarınınki 0,7–1,3 arasında olur.
  
  Açık önce yerel üretimle kapatılır: pamuk ve ipek plantasyonu, koyun çiftliği, kereste, maden ve alet zinciri. Kalanı pazarın ticaret merkezi kapasitesiyle ithal edilebilir olmalıdır.
- **Ordu ikmali:**
  - Avcı piyadesi olan büyük ordulara cephane fabrikası kurulur; bunun için yazılı teknoloji paketlerinde zaten bulunan `percussion_cap` gerekir.
  - Cephane üretemeyen ülkelerde M4 avcı piyadesi hat piyadesine çevrilir.
  - Silah ve top açığı olan pazarlara silah sanayisi eklenir.
- **Kabul:** B0'da vanilla bandında arz/talep, hedef katma değer tablosu ve sıfır ihlal.

### B3 — Devlet binaları ve altyapı
| Bina | Kural | Başrol hedefi |
|---|---|---|
| Hükümet idaresi | Bürokrasi, kurum giderleri dahil, gideri %20–40 aşar (vanilla büyük güçleri %50–90 aşar); izinli en iyi dolap yöntemi, kâğıdı pazarda | İsfahan, Rûm ve Mısır'da dikey dosya dolabı |
| Üniversite | İnovasyon sırası İsfahan > Rûm > Mısır > Tebriz ve Endülüs > diğerleri. Tavan 50 + 150 × okuryazarlık. | İsfahan ~40 seviye felsefe bölümü (~110 inovasyon), Rûm ~25 (~87), Mısır ~12. Avrupa'da Londra 6, Lehistan 4, İsveç 3, diğerleri 0–2 |
| İnşaat sektörü | Vanilla oranı: güçlü ülkede milyon kişi başı 0,3–0,4 seviye; demir iskelet kent planlaması ister | Rûm 190 → ~70 puan, Mısır ~35, İsfahan ~30 |
| Liman | Her kıyı pazarında dünya pazarına bağlanmak için en az bir liman; denizaşırı ülkelere ve donanma sahiplerine fazlası | Endülüs, Umman, Mısır, Rûm |
| Demiryolu | Kanon: yalnız maden ve liman hatları, kıtalararası ağ yok. Demiryolu teknolojisi yalnız kademe 1'de. | **Karar 4** |
| Ticaret merkezi | Kapasite, B2'de kalan yapısal ithalatı taşıyacak kadar | İsfahan'ın kumaş ve ipek ithalatı |
| Altyapı | Altyapısı yetmeyen 64 state liman ve demiryolu ile ya da yoğunluk düşürülerek kapatılır | Hedef: vanilla gibi 15'in altında |

### B4 — Kalibrasyon ve oyun testi
Her faz aday → `scenario validate/build/report` → B0 → etkinleştirme → `build/check` → siyasi denetim zincirinden geçer. Oyunda yeni başlangıçta bakılacaklar:
- 10 ülkenin GDP sıralaması;
- kumaş, giyim ve tahıl fiyatları;
- hayat standardı;
- bürokrasi;
- inovasyon;
- `error.log`.

Statik model fiyatı ve kârı hesaplamaz; oyun sonucuyla bir tur düzeltme beklenir.

## 5. Karar noktaları

1. **Avrupa'nın teknoloji seviyesi:** Önerim, Avrupa 3. kademe, Avrupa üstü 3+, güney ve doğu 4. kademe (vanilla'da Rusya ve İspanya 3. kademededir). Daha yumuşak seçenek: Avrupa 2. kademe, İslam çekirdeği 1+.
2. **Doğu Asya:** Jiangnan bugün Rûm'la aynı, 1. kademede. Önerim, Jiangnan 2, Yue 3, diğer Çin devletleri ile Japonya ve Kore 4. kademe.
3. **Toplam ekonomide birincilik:** Önerim, Rûm toplam katma değerde dünya birincisi, İsfahan kişi başında birinci olsun. Bu, kalabalık Jiangnan ve Bengal'in toplamının Rûm'u geçmemesi demektir. Alternatif vanilla gibidir: kalabalık Çin ve Hindistan toplamda önde kalır, başrol ülkeler kişi başında önde olur.
4. **Demiryolu:** Önerim kanondaki gibi az hat. Rûm'da 38 seviyeden ~12'ye (Marmara ve Ereğli kömürü), Mısır'da İskenderiye–Kahire 3, İsfahan ve Tebriz 2'şer, başka hat yok. Alternatifler: hiç demiryolu yok ya da bugünkü gibi.
