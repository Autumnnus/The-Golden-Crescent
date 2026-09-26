# Diplomasi kurulumu ve Amerika yerli statüsü — öneri

**25 Eylül 2026 · kararlar verildi, D1–D3 etkin** ([D1](../../scenarios/atlas/diplomacy_d1_natives/README.md), [D2](../../scenarios/atlas/diplomacy_d2_subjects/README.md), [D3](../../scenarios/atlas/diplomacy_d3_treaties/README.md)). Kararlar: Paris'e beş Fransız devletinin hepsi bağlandı; Tebriz İsfahan'ın müttefiki; Levant ortak garantili tampon; Amerika ve Sibirya yerlileri merkezsiz. Uygulamada öneriden sapmalar: Mombasa ve Makassar antlaşmaları kurulamadı (teknoloji / merkezsiz), Hansa ve Maratha paktları eklendi. Ek karar: tanınma senaryoya göre yeniden kuruldu ([D4](../../scenarios/atlas/diplomacy_d4_recognition/README.md)). Aşağıdaki metin kararlardan önceki önerinin kaydıdır. Kullanıcı iki şey istedi. Birincisi, büyük güçlerin bağlı devletleri olsun: İsfahan Fars devletlerini, Paris Fransız devletlerini, Mısır çevresini tutsun; bunu dünya genelinde düşün. İkincisi, Amerika'da yalnız Aztek ve İnka alanlarında yerli devlet ve koloni devletleri kalsın; geri kalan yerliler koloni kurulabilir olsun. Bu belge etkin dünyanın ölçümünü, kanonla çelişkileri ve somut öneriyi verir. 

## 1. Etkin durum

- 555 ülke. **27 bağlılık kaydı** var: Rûm 6 özerk bağlı + Yeni Bursa; Mısır–Hicaz (hac koruması, oyunda "protectorate"); Gurkanî 3; Sokoto–Gobir; Güneydoğu Asya mandalaları 5; Japonya–Ezo; Lehistan–Boğdan; Endülüs 4; Fas–Fas Brezilyası; Londra 2; Hollanda 1.
- **22 ilişki değeri**, 0 pact. Vanilla'dan kalan 11 antlaşma var (ör. Avusturya'nın Sicilya ve İtalyan düklüklerine bağımsızlık garantisi); bu evrenle ilgileri zayıf.
- Kanondan eksik kalan iki bağ: **Vinland** Kalmar kolonisi olarak yazılı ama bağımsız görünüyor. **Londra Tacı Denizaşırı Bağımlılıkları (`GBR`)** doğrudan taç bağımlılığı olarak yazılı ama bağımsız.
- Kullanılabilir araçlar:
  - bağlılık türleri (vassal, protectorate, tributary, personal_union, dominion, colony, puppet, crown_land);
  - `rivalry` pact;
  - ilişki değeri;
  - 1836 başlangıç **antlaşmaları**: ittifak, savunma paktı, bağımsızlık garantisi, ticaret ayrıcalığı, askerî geçiş, sömürgeleştirmeme anlaşması, transit hakkı.
  - Antlaşmalar Atlas'ın dışında. Mod içinde bir YAML planından üretilen ayrı bir history dosyasıyla yazılır; vanilla override'ları nasıl yazılıyorsa öyle.

## 2. Kanonla çelişkiler (kullanıcı kararıyla değişecek)

| Kanon ([diplomasi.md](diplomasi.md)) | İstek | Öneri |
|---|---|---|
| İran = yedi eşit üyeli konfederasyon; İsfahan toplantı başkanı, üst devlet değil | İsfahan Fars devletlerini vassal tutsun | Horasan, Mazenderan, Kirman, Luristan ve Huzistan İsfahan'a bağlanır. Tebriz ayrı şahlık kalır, İsfahan'la ittifak kurar. Yedi üyeli birlik ileride "İran Birliği" power bloc'u ile özel mekanik olur |
| "Altı Fransız devleti bağlı değil" | Paris vassal tutsun | Karar gerekli (bkz. §6) |
| Şam 1712: Levant, Rûm ve Mısır'ın tanıdığı ayrı taraflar | Mısır çevresini tutsun | Nil ve Libya kuşağı Mısır'a bağlanır. Levant iki gücün ortak garantisinde tampon kalır (Rûm–Mısır rekabetinin konusu) |
| İç Amerika "sahipsiz alan değil" | Yerliler koloni kurulabilir olsun | Oyunda **merkezsiz (decentralized)** statü, toprağı sahipsiz yapmaz: halk, homeland ve ülke yerinde kalır, yalnız kolonileştirilebilir olur. İlke korunur, mekanik değişir |

## 3. Önerilen bağlılıklar (yeni)

Yeni özel türler: `ve_shah_vassal` (vassal tabanlı, savaşa katılır, %8 gelir), `ve_feudal_vassal` (vassal, savaşa katılır, %10), `ve_nile_compact` (vassal, %6), `ve_crown_union` (personal_union tabanı), `ve_tatar_tribute` (tributary, %5). Mevcut 9 tür korunur.

| Üst devlet | Bağlılar | Tür | Gerekçe |
|---|---|---|---|
| **İsfahan** | Horasan, Mazenderan, Kirman, Luristan, Huzistan | şah vassalı | Fars çekirdeği İsfahan'ın başkanlığında toplanır |
| İsfahan | Herat (Farsça, Şii) | haraç | Horasan'ın doğusunda, Afgan devletlerinden ayrı |
| **Tebriz** | Bakü Hanlığı, Erevan Prensliği | koruma | Kafkasya'da Tebriz'in kendi nüfuz alanı |
| **Paris** | Bretonya, Provence, Oksitanya (+ seçeneğe göre Burgonya, Akitanya) | feodal vassal | Avrupa'nın geç feodal düzeni; Paris'in taç üstünlüğü |
| **Mısır** | Hicaz (mevcut) + Sennar, Trablus | Nil/Libya sözleşmesi | Nil ve Libya kıyısı Kahire'ye bağlı |
| Mısır | Fizan, Darfur | haraç | Sahra kervan yolları |
| Rûm | mevcut 7 | — | Değişmez; Kürdistan ve Kırım bağımsız kalır |
| **Umman** | Trucial kıyısı, Mahra, Kathiri | koruma | Körfez ve Hadramut kıyısında deniz koruması |
| **Büyük Tatar Hanlığı** | **Moskova** (haraç), Mari, Mordvin, Kalmuk | Tatar haracı / vassal | Kanondaki "Moskova Tatar baskısı altında" oyunda görünür olur |
| **Lehistan–Litvanya** | Boğdan (mevcut) + Baltık Prusya Dükalığı | vassal | Tarihsel Polonya fief'i; Lehistan'ın Hristiyan dünyasındaki ağırlığı |
| **Danimarka (Kalmar dış kurulu)** | **Vinland** (koloni şartı); Schleswig, Holstein | sömürge şartı / taç birliği | Vinland kanondaki eksik bağı tamamlar |
| **İngiltere–Galler** | İrlanda Tacı (taç birliği), **Londra Tacı Denizaşırı Bağımlılıkları** (taç toprağı) | crown union / crown land | Kanondaki Londra ortak tacı ve doğrudan taç bağımlılıkları |
| **Buhara** | Maimana, Kunduz | haraç | Türkistan hanlıklarının küçük emirlikleri |
| Hokand | Kırgız Birlikleri | haraç | Fergana–Tianşan kuşağı |
| **Haydarabad** | Kurnool (Sünni) | vassal | Deccan'da Nizam düzeni |
| Endülüs | mevcut 4 + San Salvador ve Nikaragua meclisleri | haraç | Kanondaki "bazıları Endülüs ticaret şartında" |

Toplam 27 → yaklaşık **55 bağlılık**. İsveç ve Norveç Kalmar'da eşit taçlar olarak kalır; İskoçya Londra'da eşit taç olarak kalır. Bunlar bağlılık değil, antlaşma ile gösterilir.

## 4. Önerilen antlaşmalar ve rekabetler

**İttifak / savunma paktı**
- İran Birlik Tüzüğü, 1815: İsfahan–Tebriz ittifakı.
- Kalmar: Danimarka–İsveç–Norveç savunma paktları.
- Londra ortak tacı: İngiltere–İskoçya.
- Maratha konseyi: Pune–Gwalior–Indore–Nagpur savunma paktları. Kanonda Pune üyelerin sahibi değil, bu yüzden bağlılık yerine pakt kullanılır.
- Hansa kentleri: Hamburg–Bremen–Lübeck.

**Bağımsızlık garantisi**
- Şam 1712: Rûm ve Mısır birlikte Şam, Cebel-i Lübnan ve Kudüs'e garanti verir.
- Bağdat 1804: Rûm ve İsfahan birlikte Basra ile Kürdistan'a garanti verir.
- Tuna 1827: Rûm ve Lehistan birlikte Eflak'a garanti verir.

**Ticaret ve liman sözleşmeleri**
- Kanondaki Güneydoğu Asya sözleşmeleri ticaret ayrıcalığı ve askerî geçişle yazılır: Mısır–Aceh, Mısır–Makassar, Umman–Johor, Umman–Sulu, Umman–Mombasa.
- Endülüs–Fas: Atlantik sermayesi ortaklığı.

**Rekabet (`rivalry`)**
- Rûm–Mısır (Levant), Rûm–Tebriz (Kafkasya ve Irak), İsfahan–Umman (Körfez).
- Lehistan–Moskova, Tatar Hanlığı–Lehistan.
- Kuzey Çin–Jiangnan (birleşme meşruiyeti), Gurkanî–Maratha, Gurkanî–Bengal.
- Paris–Burgonya (Burgonya bağımsız kalırsa).

**Vanilla antlaşmaları:** Kalan 11 antlaşma (Avusturya'nın İtalyan garantileri vb.) kaldırılır, yerine yukarıdakiler yazılır.

## 5. Amerika: merkezsiz yerli statüsü

**Devlet kalanlar**

| Grup | Ülkeler |
|---|---|
| Aztek/Mezoamerika | Jalisco, Bajío, Oaxaca, Zacatecas, Guerrero, Maya Birliği, Guatemala, San Salvador, Honduras, Nikaragua, Kosta Rika |
| İnka/And | Quito, Cusco, Kuzey ve Güney Peru, La Paz, Charcas, Iquicha, Tucumán, Atacama, Orta Şili; seçeneğe göre Muisca Kent Birliği ve Cauca |
| Koloniler ve koloni kökenli devletler | Yeni Endülüs, Yeni İşbiliye, İnci Adaları, Fas Brezilyası, Virginia, Yeni İngiltere, Yeni Hollanda, Pennsylvania, Potomac, Vinland, Yeni Bursa, Londra bağımlılıkları, Haiti, Leeward ve Windward meclisleri, Kıstak Meclisi, Venezuela, Buenos Aires Kent Birliği |
| Diğer | Hawaii (Polinezya krallığı) |

**Merkezsiz olacaklar (43 ülke, 7,27 milyon kişi)**
- **Kuzey Amerika'nın bütün yerli meclisleri** (Mississippi, Büyük Göller, Cherokee, Haudenosaunee, Muscogee, Choctaw, Anişinabe, Kaliforniya, Wabanaki, Caddo, Cree meclisleri, Dene, Nunavut, Tlingit, Kolombiya Nehri, Indian Territory...).
- **Kuzey Meksika kuşağı:** Sonora, Durango, Rio Grande, Kuzey Plato, Baja.
- **Güney Amerika'nın And dışı ülkeleri:** Amazon, Guaraní, Tupinamba, Pampa ve Güney Nehirleri meclisleri; Orinoco, Grão-Pará, Piratini, Paraguay, Uruguay.

**Teknik etkiler**
- Bu ülkelerin M1 kademesi 7'ye, kanunları vanilla merkezsiz sete iner.
- M2 ile verilen binaları kalkar. Vanilla merkezsiz ülkeler de binasız, yalnız geçimlik üretimle başlar.
- Nüfus, kültür, din, homeland ve okuryazarlık değişmez.
- Merkezsiz ülkeler oyuncu tarafından oynanamaz. Bu toprakları Endülüs, Londra, Hollanda, Danimarka, Fas, Rûm ve koloniler kolonileştirebilir.

**Aynı sorun Sibirya'da da var:** Yenisey, Kolıma, Ob, Saha, Çukotka, Ohotsk, Kamçatka meclisleri (0,34 M) ile Mari ve Mordvin (2,4 M) "tanınmış devlet" statüsünde. Rusya olmadığı için onları kolonileştirecek güç Tatar Hanlığı, Lehistan ve Mançurya olur.

## 6. Kullanıcı kararı gereken noktalar

1. **Fransa:** Paris'e Bretonya, Provence ve Oksitanya mı bağlansın, yoksa Burgonya ve Akitanya krallıkları da mı? Beşi birden bağlanırsa Paris 34 milyonluk bir blok olur.
2. **İran:** Tebriz, İsfahan'a ittifakla mı bağlı olsun, yoksa o da vassal mı?
3. **Mısır'ın çevresi:** Levant (Şam, Lübnan, Kudüs) ortak garantili tampon mu kalsın, yoksa Kudüs Mısır'a mı bağlansın?
4. **Amerika'nın sınırları:** Muisca/Cauca (And ama İnka değil) ve Kuzey Meksika bu sınıflandırmada nereye düşsün? Sibirya yerlileri de merkezsiz olsun mu?

## 7. Uygulama sırası (onaydan sonra)

1. **D1 — Amerika merkezsizleştirme:**
   - ülke türü → decentralized; M1 planı; bina düşürme;
   - validate/build/verify, etkinleştir, siyasi denetimi güncelle.
2. **D2 — Bağlılıklar:** yeni özel türler ve bağlılık kayıtları, `reset_countries`, liberty desire değerleri.
3. **D3 — Antlaşmalar ve rekabetler:**
   - `scenarios/diplomacy/treaties.yml` → üretilmiş `common/history/treaties/` dosyası;
   - vanilla antlaşma override'ı boşaltılır;
   - rivalry pact'ları Atlas `pacts` alanına.
4. Oyun testi: bağlılık panelleri, ittifaklar, liberty desire, açılış logu.
