# P3 — Beşinci inceleme sınır revizyonu

**25 Eylül 2026 · etkin.** Kullanıcının beşinci oyun içi harita incelemesinden sonra altı bölgede yapılan sınır, bağlılık ve demografi değişiklikleri. Kararlar [plan.yml](plan.yml) dosyasındadır; [prepare.py](prepare.py) uygular, [verify.py](verify.py) denetler. Toplam 4 province bölmesi, 97 pay aktarımı ve 5 yeni ülke vardır. Toprağı kalmayan 51 ülke rapordan düşer; ülke sayısı 551'den 505'e iner. Dünya nüfusu değişmez.

## Kullanıcı kararları

- **Rûm'un Batı Akdeniz üsleri:** Batı Sicilya, Güney Sardinya ve Septe (Ceuta). Malta zaten Rûm'daydı.
- **Tatar bağlıları:** vanilla `protectorate` türü. Vanilla `tributary` yalnız tanınmamış üst devletlere açık; Tatar Hanlığı tanınmış olduğu için haraç bağının vanilla karşılığı protectorate'tir.
- **Çin'deki Müslüman kent:** Zeytun (Quanzhou). Fujian'da Yue egemenliği altında yaklaşık 796 bin kişilik Sünni cemaat var; Çin'de Müslüman devlet yoktur.
- **Karayipler:** Haiti İnci Adaları'na (Endülüs) geçer. Leeward ve Windward ada meclisleri yeni **Fas Antilleri** kolonisinde birleşir.
- **Eflak ve Erdel:** kullanıcı senaryoyu bana bıraktı; aşağıdaki Doğu Avrupa bölümünde anlatılıyor.

## Değişiklikler

### İtalya

- **Napoli ile Sicilya'nın ayrılması:** `SIC` artık Napoli Krallığı; anakara güneyini tutar ve oyunda vanilla dinamik adıyla "Napoli" olarak görünür. Yeni **Sicilya–Sardinya Tacı** (`VSD`) Palermo ile doğu Sicilya'yı ve Sardinya'nın kuzeyini alır. Bu, kanondaki "Sicilya–Sardinya ortak tacı" düzenidir.
- **Rûm'un Sicilya ve Sardinya üsleri:** Rûm Batı Sicilya'yı (Val di Mazara: Trapani, Marsala, Mazara, Sciacca; 330 bin kişi, %38 Müslüman) ve Güney Sardinya'yı (Cagliari, Sulcis; 210 bin, %27 Müslüman) alır. İkisinde liman ve deniz idaresi vardır.
- **Septe (Ceuta):** Fas'ın kuzey ucundaki bu province Rûm'a geçer. 26 bin kişi, %92 Müslüman, deniz idaresi var; Yeni Bursa (Florida) rotasının boğaz üssüdür.
- **Ceneviz Cumhuriyeti (`VCN`):** Liguria kıyısı (600 bin) ve Korsika. Piyemonte'nin kıyıdaki limanı, tersanesi, balıkçılığı ve deniz idaresi Cenova'ya geçer; Savoy–Piyemonte karaya kapanır ama Nice kıyısı ondadır.
- **Venedik:** İstirya ile Güney Tirol'ü (Trento) Avusturya'dan alır; nüfusu 1,9 milyondan 3,0 milyona çıkar.
- **Küçük devletler:** Lucca Toskana'ya, Parma Milano'ya katılır.

### Almanya (küçük devletlerin birleşmesi)

- **Hansa Kent Birliği** (`HAM`): Hamburg, Bremen ve Lübeck.
- **Thüringen Birliği** (`WEI`): Weimar, Meiningen, Coburg ve Schwarzburg.
- **Hessen** (`HES`): Darmstadt, Kassel, Nassau ve Waldeck. Frankfurt serbest kent olarak kalır.
- Oldenburg ve Brunswick Hannover'e, Strelitz Mecklenburg'a, Hohenzollern Württemberg'e, Lippe ve Schaumburg Ren Kent Birliği'ne katılır.

### Doğu Avrupa (1818–1827 savaşı)

Rûm Taht Savaşı'na müdahale eden Lehistan–Litvanya, Rûm'u ve onun yanında savaşan Avusturya'yı büyük bir zaferle yendi.

- **Lehistan:** Bukovina'yı ve Besarabya'yı doğrudan alır.
- **Eflak:** Dobruca'yı alır; Tuna ağzı Rûm'un Tuna Emirliği'nden çıkar. Eflak, Boğdan gibi Lehistan koruması (`protectorate`) olur ve 1827 Tuna garantileri kalkar.
- **Macaristan ve Erdel:** savaşta birlikte serbest kalan iki bağımsız devlettir ve Karpat Ahdi (1827) ile savunma paktı kurar.
- **Hırvatistan:** Macaristan'ın kuklasıdır (`puppet`); Dalmaçya'yı Avusturya'dan alır.
- **Avusturya:** Avusturya, Stirya, Tirol ve Slovenya'ya çekilir (5,8 → 3,8 M). İstirya, Güney Tirol, Dalmaçya ve Bukovina'ya hak iddia eder; Lehistan ve Macaristan'la ilişkisi kötüdür. Karadağ'daki payını Karadağ'a bırakır.
- **Livonya Konfederasyonu** (`UBD`): bağımsızdır. İsveç ve Lehistan dört Livonya state'inin hepsine hak iddia eder. İki devlet karşılıklı rakiptir ve ilişkileri −50'dir.

### Tatar Hanlığı ve Orta Asya

- **Tatar Hanlığı:** Ural Konfederasyonu (Perm, Başkurt Urali), Çuvaşya, Samara'nın ve Çelyabinsk'in Kazak/Başkurt payları doğrudan Tatar Hanlığı'na geçer (4,2 → 5,75 M). Mari ve Mordvin kuklaları ile Kalmuk koruması aynen kalır.
- **Kazak Hanlığı** (`KZH`): üç cüz tek bir Kazak Hanlığı'nda birleşir. Uralsk, Aktöbe, Akmolinsk, Semey ve Sırderya'yı tutar; başkenti Türkistan kentinin bulunduğu Sırderya'dır. Tatar Hanlığı'nın korumasıdır; Sibirya Tatar Birliği de Tatar koruması olur.
- **Harezm (Hive):** Türkmen çölünü alır.
- **Buhara:** Merv'i, Maymana'yı ve Kunduz'u doğrudan alır; bu ikisinin koruma bağları kalkar.
- **Hokand:** Kırgız birliklerini katar.

### Uygur Hanlığı

`KSG` artık **Uygur Hanlığı**; Kaşgar'a Cungarya, Altay, Yedisu ve Gansu eklenir (0,85 → 7,8 M).

- **Gansu:** Hexi koridoru, Kuzey Çin'den alınmış ve Çinli çoğunluklu bir sınır eyaletidir. Uygur garnizonu ve Hui cemaati nüfusun %12'sidir.
- **Kuzey Çin'e karşı:** Uygur Hanlığı Ningxia ile Çinghay'a hak iddia eder, Kuzey Çin de Gansu'yu geri ister. İki devlet rakiptir ve ilişkileri −60'tır.

### Amerika

- **Venezuela:** Bolívar ve Batı Hint payı Yeni İşbiliye'ye katılır.
- **Hispanyola:** Haiti İnci Adaları'na geçer; ada bütünüyle Endülüs'ündür.
- **Fas Antilleri** (`VFA`, Fas kolonisi): Leeward ve Windward ada meclisleri birleşir; kölelik yasağı korunur.
- **Endülüs Amerikası'nda din:** VPI, VFA, VSI, VNE, VGZ ile Endülüs'e bağlı Orta Amerika meclislerinde Hristiyan payının %85'i Sünniliğe geçer. Kalan Katolik azınlık, Endülüs'ün kendi Hristiyan azınlığının karşılığıdır.
  - Adalarda Müslüman payı %78–86'dır.
  - Kıyıda: Maracaibo %62, Caracas %68, Antioquia %63, iç Bolívar %40.
  - Meksika havzasında %69, Veracruz'da %55.
  - Sınır bölgelerinde yerel inançlar çoğunlukta kalır.

### Kuzey Afrika, Sahra ve Batı Afrika

Bölgedeki devlet sayısı yaklaşık 25'ten 7'ye iner: Fas, Cezayir, Tunus, Trablus, Fizan, Tuareg ve Mısır.

- **Cezayir:** Konstantin, Kabiliye, Tuğurt, Mzab ve Şaamba'yı alır (2,25 → 4,18 M).
- **Fas:** Tuat'ı, Batı Sahra'yı ve Moritanya'yı alır. Futa Toro kendi payını tutar.
- **Timbuktu Paşalığı** (`VTB`, Fas kolonisi): 1591 Fas fethinin paşalığıdır; Timbuktu state'indeki Songay ve Bidan paylarını tutar. Massina kenti geri ister.
- **Tuareg Konfederasyonu** (`AHG`, merkezsiz): Ahaggar, Ajjer, Adagh, Ansar, Aïr ve Dinnik meclisleri birleşir.
- **Fizan (Mısır koruması):** Tibesti, Ghat ve Zuwaya'yı alır. Zuwaya'nın Trablus ve Kirenayka payları Trablus'a geçer.
- **Endülüs Ginesi** (`VAG`, Endülüs kolonisi): Sierra Leone, Kazamans ve Kaabu (Bissau kıyısı).

## Teknik ayrıntılar

- **Yeni ülkeler:** her biri bir M1 ülkesinin teknoloji kademesini, kanunlarını ve kurumlarını kopyalar.
  - Sicilya–Sardinya: Venedik şablonu, monarşi kanunuyla.
  - Ceneviz: Venedik şablonu.
  - Timbuktu ve Fas Antilleri: Fas Brezilyası şablonu; Antiller'de kölelik yasağıyla.
  - Endülüs Ginesi: Yeni İşbiliye şablonu.
- **Pay birleştirme:** alıcının zaten payı olan state'lerde iki pay birleşir. Province, kişi ve bileşim toplanır, okuryazarlık ağırlıklı ortalamayla hesaplanır. Binalar kaynak derlemenin kayıtlarından toplanarak yazılır; alıcının kullanamayacağı yöntemler değiştirilir. Merkezsiz alıcının binası olmaz.
- **Okuryazarlık soy kaydı:** [lineage.yml](lineage.yml) her P3 payının kişilerinin hangi P3 öncesi paydan geldiğini kaydeder (üretilen dosya). [M1b hazırlayıcısı](../mechanics_m1b_literacy/prepare.py) bunu okur. M1b P3 dünyasında yeniden çalıştırıldığında bütün paylar birebir aynı okuryazarlıkla üretilir; bu sınandı.
- **Diplomasi:**
  - 3 bağlılık kalktı (Maymana, Kunduz, Kırgız), 7 bağlılık eklendi; toplam 70.
  - D3 planında Hansa paktları ve Tuna garantileri kalktı; Karpat Ahdi eklendi. Antlaşma sayısı 23, rekabet sayısı 10.
  - 7 ilişki değeri eklendi.
- **Hak iddiaları:** 16 state'e eklendi; iddiaların listesi planda.

## Doğrulama

[verify.py](verify.py) şunları denetler:
- state nüfusları değişmemiş;
- soy kaydı her payın kişi sayısına ve ağırlıklı okuryazarlığına eşit;
- bölmeler ve aktarımlar raporda doğru sahipte;
- beklenmeyen topraksız ülke yok;
- din hedefleri tutmuş, cemaatler eklenmiş;
- P3 paylarında kölelik yasağı altında köle POP'u yok;
- iddialar yazılmış, bağlılık ağı ve rekabetler planla aynı;
- dokunulmayan ülkelerin içeriği aynı;
- yeni uyarı yok. İzin verilen tek istisna kaybedilen state'lerdeki vanilla birliklerinin kaldırılması notu (Avusturya Bukovina, Sardinya, Sicilya).

Etkinleştirme sonrası: `check` 0 hata, 16 uyarı; [siyasi denetim](../world_political/active_political_audit.py) P3 katmanıyla geçti; araç testleri 123/123. Oyunda sınanmadı.

**Açık konular:**
- Vanilla rütbe kısıtları (Eflak, Kazak Hanlığı, Hırvatistan) oyunda denetlenmeli.
- Yeni ülkelerin ordusu yok.
- Önceki fazlardan kalan bir tutarsızlık var: İran üyeleri, Rûm'un Diyarbakır payı, Seylan ve Yeşil Burun köle POP'u taşıdığı halde `law_slavery_banned` kanununa sahip. P3 bunlara dokunmadı.

```sh
cp world/scenario.yml build/political/p3-source.yml; cp build/world-political/active-political-report.json build/political/p3-source-report.json
python3 scripts/tools.py atlas scenario build build/political/p3-source.yml --out build/scenarios/p3-source
python3 scenarios/atlas/political_p3_borders/prepare.py
python3 scripts/tools.py atlas scenario validate build/political/p3-candidate.yml
python3 scripts/tools.py atlas scenario build build/political/p3-candidate.yml --out build/scenarios/p3-candidate
python3 scenarios/atlas/political_p3_borders/verify.py
```
