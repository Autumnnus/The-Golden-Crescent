# Dünya siyasi inşa planı

**19 Eylül 2026.** Bu belge, The Golden Crescent'ın Atlas üretim sırasının yeni tek planıdır. Önce dünyanın siyasi haritası kurulacak; ülke içi ekonomi, nüfus, hukuk, teknoloji, ordu ve Flavor bundan sonra gelir.

## Hedef ve sınır

İlk teslim, 1 Ocak 1836 için dünya çapında incelenebilir bir siyasi önizlemedir. Her kara state için tek doğrudan sahip; her bağımlı devlet için tek overlord; sömürge, liman imtiyazı ve hak iddiası için ayrı bir tanım bulunur. Harita, bu aşamada etkin `world/` kaynağı veya oynanabilir başlangıç değildir.

Bu aşama bilinçli olarak şunları yapmaz: nüfus toplamı, kültür/din oranı, bina, şirket, kanun, teknoloji, ordu, piyasa, event veya GFX üretmez. Bunlar siyasi sınırlar kilitlendikten sonra aynı dünya kaynağına eklenir.

## Tek kaynak düzeni

| Katman | Konum | Görevi |
|---|---|---|
| Dünya ilkesi ve siyasal karar | `docs/scenario/` | Neden-sonuç, egemenlik, bağlılık ve açık kararlar |
| Siyasi kart | `scenarios/atlas/world_political/regions/` | Bir bölgenin gerçek Atlas state kimlikleriyle sahiplik taslağı |
| Birleşik siyasi önizleme | `build/world-political/partial-political-preview.json` | 65 karttan türeyen, 675 state'i ve yazılı başlangıç bağlılıklarını açıkça kapsayan etkin olmayan Atlas V2 önizlemesi |
| Atlas çıktıları | `build/world-political/` ve `build/maps/` | Geçici HTML/JSON/rapor; kaynak değildir |
| Etkin başlangıç dünyası | `world/scenario.yml` | Ancak siyasi kilit ve temel mekanik katmanı tamamlanınca oluşturulur |

Kart tamamlanmadan birleşik senaryoya eklenmez. Böylece yarı kararlı bir sınır, sonraki ekonomi veya Flavor çalışmasına yanlış gerçekmiş gibi sızmaz.

## Nihai çalışma sırası

1. **Siyasi sözlük ve karar kaydı.** Her yazılı aktör için doğrudan egemen, ortak taç, bağımlı, koruma antlaşması, liman imtiyazı veya hak iddiası ayrılır. Sadece ilk üçü harita sahipliği veya subject ilişkisi doğurur.
2. **State eşleme kartları.** Atlas `catalog`, `find` ve `show` ile her kartın gerçek `STATE_*` kimlikleri doğrulanır. Bir state iki devlete verilecekse gerçek province listesi kullanılır; şehir adıyla varsayım yapılmaz.
3. **Kıtasal siyasi önizleme.** Kart, ayrı V1 Atlas senaryosu olarak validate edilir ve referans/değişiklik haritası incelenir. Burada yeni ülke için yalnız ad, renk, başkent ve asgarî ülke türü tanımlanır.
4. **Dünya birleşimi.** Tamamlanmış kartlar tek önizlemeye birleşir. `card63.json`, önceki büyük kartlar dışındaki yerel state'leri de açık province `split`leriyle taşır; boş, belirsiz veya yalnız devralınmış state kalmaz. Atlas bütün dünya validate, report ve preview üretir.
5. **Siyasi kilit.** Kullanıcı dünya haritasını inceleyip kabul eder. Bu noktadan sonra sınır değişikliği ilgili kart, diplomasi ve komşu kartı birlikte güncellenmeden yapılmaz.
6. **Başlangıç mekanikleri.** Siyasi olarak kilitli ülkeler, altı bölgesel pakette nüfus/toplum → ekonomi/altyapı → hukuk/teknoloji → asker/diplomasi sırasıyla V2'ye geçirilir. Bir ülke sadece haritada bırakılarak etkin dünyaya alınmaz.
7. **Uyumluluk ve motor testi.** Eski vanilla ülkelerin karakter, AI, journal ve on_action kalıntıları; custom subject sözleşmeleri ve seçilen harita bölünmeleri aktif dünya öncesi ayrı düzeltilir ve izole modda sınanır.

## Siyasi kart sırası

| Sıra | Kart | Tamamlanma ölçütü |
|---:|---|---|
| 0 | Ortadoğu–Balkanlar ve Kuzey Avrasya | **0A–0D tamamlandı:** Rûm–İran çekirdeği, Kafkasya ve RUS'suz Kuzey Avrasya eşlendi. Moskova/Novgorod, Tatar/Mari/Mordvin/Ural ve dokuz Sibirya yerel yönetimi haritada; Yemen yerel kıyı düzeni ile Basra–Kuveyt province sınırı kapandı. |
| 1 | Avrupa–Akdeniz | **1A–1O tamamlandı:** önceki çekirdeklere Bohemya, Macaristan/Erdel bağımsızlığı, Hannover, Brabant–Liège, İberya ve Prusya kapanışı eklendi. Londra’nın yalnız Bahamalar, Bermuda, Güney Atlantik ve Batı Hint Adaları’ndaki kalan küçük doğrudan idaresi de açık sınırla kayda geçirildi. |
| 2 | Hindistan | **2A–2D tamamlandı:** BIC'nin tüm doğrudan province payları kaldırıldı; Lahor Gurkanî, Pencap tepeleri Sih çekirdeği olarak eşlendi; Keşmir sözleşmeli bağlı, Jaipur/Mewar sınırlı koruma antlaşmalı ve Kandy egemen ada devleti oldu. |
| 3 | Doğu Asya ve denizler | **3A–3F tamamlandı:** CHI ayrımı, Filipinler yerel üçlüsü ve askerî üst devletsiz Ryukyu önizlemede. Mısır–Aceh/Makassar ile Umman–Johor/Sulu liman sözleşmeleri açıkça kaydedildi; doğrudan kıyı kolonisi eklenmedi. |
| 4 | Afrika | **4A–4G tamamlandı:** Mağrip'te Fransız doğrudan Cezayir payları kaldırıldı; Mavi Nil bağımsız Sennaar'a geçti; Kordofan ve Eritre'deki Mısır payları Darfur/Afar'a, Altın Sahil'deki Avrupa depo payları Aşanti'ye döndü. Omani Mombasa, Abu Dabi ve Makran/Bampur enclave'leri yerel sahiplerine döndü; Zanzibar divanı korunur. Sokoto–Gobir emirlik sözleşmesi ile Massina–Timbuktu kent şartı da açıkça ayrıldı. |
| 5 | Amerika ve Okyanusya | **5A–5X tamamlandı:** Amerika kartlarına Avustralya/Aotearoa yerel egemenlik, Guyana Hollanda yerleşimi, iki ayrı Küçük Antil ada meclisi, Vinland Newfoundland çekirdeği, Panama Kıstağı ve Kolombiya içinin yerel ayrışması eklendi. |
| 6 | Dünya siyasî kilidi | **Tamamlandı:** 65 kart, 675/675 açık state kaydı, 27 denetlenen bağlılık, 19 denetlenen ilişki, sıfır devralınmış pact, sıfır çifte province sahibi ve izole üretilmiş-dünya kontrolü |

## Karar kuralı

- Yazılı atlas doğrudan egemenliği açıkça söylüyorsa, kart buna göre hazırlanır.
- Metin yalnız liman hakkı, ticaret imtiyazı, koruma veya tarihî iddia söylüyorsa state sahipliği değiştirilmez.
- Bir şehir birden çok modern state içinde kaldığında il düzeyinde bölünme, ancak Atlas'ta gerçek province kimlikleri görüldükten sonra eklenir. Siyasi kilit için hiçbir state `unresolved` bırakılamaz.
- Küçük yerel devletler sırf haritayı doldurmak için icat edilmez; mevcut yerel düzen bir senaryo tercihi olarak korunacaksa `card63.json` ve siyasi state karar defterinde açık province sahibiyle yazılır.
- Siyasi kart kabul edilmeden ekonomi veya nüfus sayısı verilmez.

## Siyasi kilit ölçütü

Siyasi aşama, ancak aşağıdaki üç denetim birlikte geçince tamamlanır:

1. `political_state_ledger.py`, 675 state'in her birini bir kart değişikliğine
   veya bağlı bölgesel korunmuş-karar kaydına bağlar; province geometrisi ve
   eski doğrudan büyük güç sahipleri de burada doğrulanır.
2. `political_completion_audit.py`, geçici ülke tanımı ile devralınmış vanilla
   pact bırakmaz ve Londra'nın dört küçük denizaşırı bağımlılığını sabit
   kapsamda tutar.
3. Birleşik Atlas validate/report geçer, etkin moddan ayrı önizleme paketi
   `build/scenarios/world-political-preview` altında üretilmiş-dünya
   denetiminden geçer ve değişiklik haritası incelenebilir biçimde üretilir.

Maratha ortak konseyi ayrı hazinelerle çalışan bir dış müzakere düzenidir;
harita aşaması bunu sahte bir overlord hiyerarşisine dönüştürmez. Ortak sefer
ve altyapı şartı başlangıç mekanikleri/Flavor aşamasında uygulanacaktır.

## İlk somut hedef

İlk kart, Ortadoğu–Balkanlar olacaktır. Rûm çevresinde daha önce doğrulanan devletler tekrar tasarlanmayacak; sadece mekanik yüklerinden ayrılıp dünya siyasi iskeletine aktarılacak. Ardından İran, Mısır, Arabistan, Kafkasya ve Orta Asya'nın yazılı egemenlik kararları gerçek Atlas state kimlikleriyle tamamlanacaktır.

## Uygulama kaydı

Aşağıdaki erken kart notları tarihsel üretim kaydıdır. Bir satırın “sonraki kart” veya “açık” demesi, güncel siyasi karar değildir: nihai durum `card63.json`, `card64.json`, siyasi state karar defteri ve güncel denetim raporlarıdır.

- **Kart 0A:** `card00.json` Rûm, altı Rûm bağlısı, bağımsız Levant/Mezopotamya kuşağı, Kuveyt province ayrımı ve İran'ın yedi üyesini içerir. Atlas validate/report/preview geçti: 20 tanımlı ülke ve 54 state/split kaydı.
- **Kart 1A / 4E–5V:** `card01.json` eski metropolitan `FRA` toprağını Paris, Burgonya, Bretonya, Akitanya, Oksitanya ve Provence arasında dağıtır; Paris'in kuzey çekirdeği French Low Countries state'ini de içerir. `card02.json`, `card44.json` ve `card46.json` Madras, Senegal ve Guyana'daki payları yerel/yazılı sahiplere birleştirir. `card47.json` Fildişi Sahili, Mascarene ve iki Küçük Antil payını kapatır; birleşik önizlemede FRA kara sahibi veya geçici aktör değildir.
- **Kart 2A:** `card02.json`, BIC'nin 21 state içindeki bütün doğrudan province payını yerel ülkelere aktarır ve `reset_countries: [BIC]` ile şirketin başlangıç diplomasi ağını kaldırır. Atlas reportunda BIC ülke kaydı veya pact kalmadığı doğrulandı.
- **Kart 3A:** `card03.json`, CHI'nin 43 state içindeki bütün province payını Kuzey Çin, Jiangnan, Shu, Yue, Mançurya ve komşu İç Asya aktörlerine aktarır. `reset_countries: [CHI]` sonrası Atlas raporunda CHI ülke kaydı veya pact kalmadığı doğrulandı.
- **Kart 0B:** `card04.json`, RUS'un Ermenistan, Bakü, Tiflis, Kırım, Kazan, Kalmukya, Moskova ve Novgorod paylarını yazılı atlasın bağımsız aktörlerine verir. Kuzey Kafkasya'da mevcut Çeçen/Çerkes province'leri korunur; geriye kalan gerçek province'ler Dağıstan'a geçer.
- **Kart 0C:** `card04.json` ve `card12.json`, RUS'un kalan bütün doğrudan province payını Moskova/Novgorod, Volga–Tatar, Mari/Mordvin/Ural, Lehistan–Litvanya, komşu Kazak/Baltık/Boğdan ve dokuz Sibirya yerel yönetime aktarır. Birleşik Atlas kataloğu RUS için kara sahibi bulmaz.
- **Kart 1B–1L:** `card05.json` İber çekirdeklerini eşler; `card42.json` Beira ve Murcia'yı Endülüs'e, Valencia ve Balearları Aragon'a verir; `card43.json` Rif'i Fas'a ve Kanaryaları Endülüs'e geçirerek SPA'yı kaldırır. Portekiz'in çakışmayan denizaşırı payları `card44.json`da, çakışan son dört liman payı ilgili Hindistan, Çin ve Takımada kartlarında tamamlanır.
- **Kart 4A:** `card06.json`, Cezayir, Oran ve Konstantin state'lerindeki tüm FRA province paylarını mevcut yerel Magrip yönetimlerine aktarır. Fas, Tunus ve Trablus'un halihazırda yerel sahipliği değiştirilmez.
- **Kart 1C / 1N:** `card07.json`, Brandenburg, Pomeranya, Ren kent birliği ve Anhalt'ın doğrudan core state/province paylarını PRU'dan çıkarır. `card49.json` Batı Prusya'yı Lehistan-Litvanya Baltık koridoruna, Doğu Prusya'yı bağımsız Baltık Prusya Dükalığına, Silezya'yı Bohemya'ya ve Brunswick payını yerel yönetime verir; PRU birleşik önizlemede topraksız kalır.
- **Kart 1D:** `card08.json`, Lombardiya ve Venetia state'lerindeki AUS paylarını Milano ve Venedik'e aktarır. Savoy–Piyemonte, Ceneviz ve diğer İtalyan küçük devletleri kendi sınır kararıyla sonraki karttadır.
- **Kart 1E:** `card09.json`, Büyük Britanya'nın ana ada state'lerini İngiltere–Galler, İskoçya ve İrlanda taçlarına ayırır. Ortak hükümdarlık/ortak dış kurul siyasi harita değil diplomasi katmanıdır; Guyana, Guatemala, Yukarı Endülüs ve Newfoundland payları yerel kartlarda kapatılmıştır. Bahamalar, Bermuda, Güney Atlantik ve Batı Hint Adaları'ndaki kalan on bir province ise Londra Tacı Denizaşırı Bağımlılıkları'nın sınırlı doğrudan idaresi olarak kesin kayıttadır.
- **Kart 5A:** `regions/05_americas_oceania.md`, Amerika/Okyanusya için state kartı öncesi zorunlu karar defteridir. Kıyı sahibi, antlaşma ve liman hakkını ayırır; kullanıma hazır olmayan büyük vanilla devletleri tek hamlede kaldırmaz.
- **Kart 5B:** `card10.json`, `STATE_MEXICO`/`STATE_VERACRUZ` MEX paylarını Yeni Endülüs'e, `STATE_YUCATAN` ve `STATE_CHIAPAS` MEX paylarını Maya Birliği'ne verir. Chiapas'taki mevcut UCA payı korunur; Meksika'nın diğer alanları sonraki kartlara açıkça kalır.
- **Kart 5C:** `card14.json`, Küba, Jamaika ve Porto Riko'nun doğrudan ada state'lerini İnci Adaları Koloni Meclisi'ne geçirir. Hispanyola'daki farklı yerel düzen karara bağlanmadan Haiti'yi topluca devretmez.
- **Kart 1F:** `card11.json`, FIN'in altı doğrudan state'ini SWE'ye, İzlanda'yı DEN'den NOR'a verir ve `reset_countries: [FIN]` ile ayrı Finlandiya başlangıç ağını kaldırır. Kalmar ortak tacı ile Schleswig–Holstein'ın statüsü state sahibi değil, sonraki diplomasi kararıdır.
- **Kart 1G / 1O:** `card12.json`, Lehistan-Litvanya'nın Varşova, Litvan ve doğu Ruthen yazılı çekirdeğini RUS/PRU province paylarından `VPL`'ye aktarır. `card50.json` Doğu Galiçya'yı VPL'ye, Batı Galiçya'daki Avusturya payını Kraków şehir devletine verir; Kiev de doğu Ruthen halkasındadır. Boğdan koruması V2 diplomasi aşamasındadır.
- **Kart 5D–5E:** `card15.json` ve `card16.json`, ABD'nin tüm doğrudan state paylarını kıyı kolonileri, yerel konfederasyonlar ve Potomac kent bölgesine aktarır. Kıyı–iç çizgisinin state ölçeğindeki sadeleştirmeleri `senaryo_amerika.md` ile birlikte sonraki province/diplomasi kartında daraltılacaktır.
- **Kart 5F–5G:** `card17.json` ve `card18.json`, HBC doğrudan paylarını Vinland, Cree, Dene, Inuit ve mevcut kuzeybatı yerel aktörlerine aktarır; HBC birleşik önizlemede topraksız kalır. Vinland'ın kıyı sözleşmesi ve Kalmar bağı diplomasi kartında kurulacaktır.
- **Kart 5H–5I:** `card19.json` ve `card20.json`, MEX'in tüm doğrudan paylarını Yeni Endülüs/Maya dışındaki yerel meclislere ve mevcut kuzey yerli ağlarına aktarır; MEX birleşik önizlemede topraksız kalır.
- **Kart 5J:** `card21.json`, Fas Brezilyası'nı Pernambuco–Bahia–Rio kıyı çekirdeğiyle sınırlar; BRZ içi sonraki kartlarda yerel aktörlere ayrılacaktır.
- **Kart 5K–5L:** `card22.json` ve `card23.json`, BRZ içini nehir, plato ve yüksekova meclislerine ayırır; BRZ birleşik önizlemede topraksız kalır.
- **Kart 5M–5Q:** `card24.json`–`card28.json`, Charcas/Yukarı Andlar ile Arjantin ve Şili doğrudan sahipliklerini yerel And, Guaraní, Pampa, Mapuçe çevresi ve kent aktörlerine ayırır; BOL, ARG ve CHL birleşik önizlemede topraksız kalır.
- **Kart 3B:** `regions/03_east_asia_seas.md`, Güneydoğu Asya/takımadalar için zorunlu karar defterini ekler. Batılı doğrudan owner payı, yerel egemen çekirdek ve Mısır/Umman liman hakkı aynı şey değildir; liman tarafı açıkça seçilmeden V1 sahibi değiştirilmez.
- **Kart 4B:** `regions/04_africa.md`, Afrika'nın Nil, Sahel, Boynuz, göl havzaları, kıyılar ve güneyi için doğrulanmış state adayları/açık owner kararlarını kaydeder. Yabancı depo veya kira ilişkisi doğrudan kolonileştirme değildir.
- **Kart 4C–4D:** `card13.json`, Mavi Nil'deki bütün EGY province payını bağımsız Sennaar'a aktarır. `card54.json`, yazılı Dongola sınırını Kordofan'daki Mısır payını Darfur'a ve Eritre'deki payı mevcut Afar yönetimine aktararak tamamlar; Altın Sahil'deki Danimarka/Hollanda küçük depo payları Aşanti'ye döner. Mısır'ın Massava/Dahlak sözleşmesi toprak egemenliği değildir.
- **Kısmi dünya önizlemesi:** `prepare_partial_preview.py`, bütün çakışmasız kartları `build/` altında geçici V2 görsel senaryoda birleştirir. Bu çıktı kesin dünya kaynağı değildir ve karar defterlerindeki açık sınırları kapatmaz.
- İki kart `verify_cards.py` ile harita-yalnızlık koşulundan geçer. Birleşik dünya senaryosuna ancak kendi bölgesel karar listesi kapandığında katılacaktır.

- **Kart 5R–5X:** `card29.json`, Quito çekirdeğinin doğrulanmış ECU paylarını birleştirir. `card30.json`, Cusco Krallığını oyun başkenti temsili olarak Arequipa'da kurar ve artık Güney Peru tanımını temizler; Lima kıyısı sözleşmeli ticaret alanıdır. `card52.json` Panama Kıstağı Meclisini, `card53.json` ise Kolombiya'nın Antioquia, Cauca ve Guaviare ayrışmasını tamamlar; birleşik önizlemede geçici Amerika ülkesi kalmaz.

- **Kart 6A–6C ve siyasi denetim:** `card60.json` devralınmış bölgesel pact'ları senaryonun dar sözleşmeleriyle değiştirdi; `card61.json` Britanya'nın son uyumsuz koloni sahipliklerini yerel aktörlere devretti; `card62.json` pay değişimleriyle başkenti kaybolan 12 yerel devletin başkentini güvenli state'e taşıdı. `card63.json` kalan 221 yerel state'i açık province `split`lerine dönüştürdü ve sekiz state'teki 29 eski çifte province iddiasını tek sahibe indirdi. `card64.json`, yazılı başlangıç bağlılıklarını temsil eden 27 overlord ve 19 ilişki kaydını kurdu. `political_state_ledger.py` 675/675 state kart kararını, `diplomacy_contract_audit.py` diplomasi sözleşmesini, `political_completion_audit.py` ise sıfır devralınmış pact ile izole üretilmiş-dünya paketini doğrular.
