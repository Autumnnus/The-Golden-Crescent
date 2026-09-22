# Kart 5 — Amerika ve Okyanusya

**Durum: 5A–5X siyasi sahiplik kapanışı doğrulama için hazır. Amerika'nın eski büyük devletleri yerel ağlara ayrıldı; Panama ve Kolombiya içi dahil geçici ülke kaydı kalmadı. Avustralya/Aotearoa doğrudan yerel sahipliktedir.**

Amerika için yazılı dünya atlası doğrudan çekirdek ile ticaret/antlaşma alanını özellikle ayırır. Bu nedenle bir şehir adı tek başına sınır üretmez. Aşağıdaki erken karar tablolarındaki “kapanacak/açık” dili tarihsel hazırlık kaydıdır: bütün satırların kesin province sahibi artık Kart 5, Kart 6B ve [siyasi state karar defterinde](../../../docs/scenario/SIYASI_STATE_KARAR_DEFTERI.md) kilitlidir.

## Kesin yerel state kararı

`05_north_america`, `06_central_america`, `07_south_america` ve
`13_australasia` içindeki bütün state'ler artık Kart 5 veya Kart 6B'de açık
province `split`i taşır. Yerel düzen koloni etiketi ya da tarihî ticaret hakkı
üzerinden yeniden dağıtılmaz; karar defterindeki sahiplik nihai siyasi kayıttır.

## Kuzey ve doğu kıyıları

| Aktör | Erken tasarım çekirdeği | Tarihsel hazırlık notu |
|---|---|---|
| Vinland | `STATE_QUEBEC` içindeki aşağı Saint Lawrence/Quebec kıyısı; `STATE_NEWFOUNDLAND` kıyı istasyonları | Quebec'in içi, Labrador, HBC ve yerli sahiplerin province ayrımı; Nya Norrland ayrı ülke değildir |
| Yeni İngiltere | `STATE_MASSACHUSETTS`, `STATE_NEW_HAMPSHIRE` ve kuzeydoğu kıyı kentleri | Kıyı kentleri ile iç yerli alanların province çizgisi |
| Yeni Hollanda | `STATE_NEW_YORK` Hudson ağzı, `STATE_NEW_JERSEY` kıyısı | Hudson vadisinin bütün state olmadığı; Haudenosaunee ile sınır province'leri |
| Pennsylvania | `STATE_PENNSYLVANIA` Philadelphia–Delaware kuşağı | Lenape alanları ve batı iç bölge ayrımı |
| Virginia | `STATE_VIRGINIA`, `STATE_MARYLAND`, `STATE_NORTH_CAROLINA`, `STATE_SOUTH_CAROLINA` kıyı plantasyon alanları | İç Carolina/Appalachia'nın yerli aktörlerden ayrılması |
| Yeni Bursa | `STATE_FLORIDA` kıyı limanı | Florida'nın içiyle doğrudan koloni çekirdeğini ayıran province listesi |

## Endülüs, Fas ve Karayip çekirdekleri

| Aktör | Erken tasarım çekirdeği | Tarihsel hazırlık notu |
|---|---|---|
| Yeni Endülüs | `STATE_MEXICO`, bağlantılı `STATE_VERACRUZ` kıyı koridoru | Merkezî plato, Pasifik/golf bağlantısı ve yerel şehirlerin province paylaşımı |
| Maya Birliği | `STATE_YUCATAN`, `STATE_CHIAPAS` yerel payları | Chiapas'taki mevcut çoklu sahiplik ve haraç alanının egemenlikten ayrılması |
| Yeni İşbiliye | Cartagena/aşağı Magdalena için Kolombiya state adları sonraki katalogda doğrulanacak | Muisca/Bogotá alanı, Orinoco kıyı noktaları ve iç bölgenin ayrılması |
| İnci Adaları | `STATE_WESTERN_CUBA`, `STATE_CENTRAL_CUBA`, `STATE_EASTERN_CUBA`, `STATE_PUERTO_RICO`, `STATE_JAMAICA` | Hispanyola ve ada başına ayrı yerel yönetim; küçük Karayiplerin tek kolonide toplanmaması |
| Fas Brezilyası | `STATE_PERNAMBUCO`, `STATE_BAHIA`, sınırlı `STATE_RIO_DE_JANEIRO` liman payı | Kıyı yerleşimlerinin province listesi; Amazon, iç yayla ve güneyin yerel egemenliği |

## Güney Amerika ve Okyanusya

| Aktör | Erken tasarım state adayı | Tarihsel hazırlık notu |
|---|---|---|
| Quito / Cusco / Charcas | Oyun state adları şehir adlarıyla örtüşmez; ayrı katalogla doğrulanacak | And yüksek havzaları, Lima ticaret hakkı ve Potosí çevresinin province eşlemesi |
| Muisca | Bogotá adı Atlas state kimliği değildir; katalogla doğrulanacak | Yeni İşbiliye'nin kıyı alanından bağımsız yüksek havza |
| Guaraní | `STATE_ALTO_PARAGUAY`, `STATE_BAJO_PARAGUAY` | Paraná havzalarının yerel birlikleri; Fas'ın Plata liman hakları toprak sahibi değildir |
| Mapuçe / Orta Şili | `STATE_ARAUCANIA`, `STATE_SANTIAGO` | Mapuçe'nin bütün Şili/Patagonya olmadığı; mevcut yerel province payları |
| Avustralya/Aotearoa/Pasifik | Önce yerel siyasi temsil birimi belirlenecek | Mevsimlik Mısır/Makassar iskeleleri egemen koloni değildir; devlet kartı ancak doğrudan toprak kararıyla açılır |

## Uygulama sırası ve güvenlik kuralı

1. Önce her koloni ya da yerli aktör için **doğrudan owner**, **subject/antlaşma statüsü** ve **ticari hak** ayrı satırda onaylanır.
2. Ardından `atlas catalog` ile aday state'in tüm province sahipleri okunur. Kıyı çekirdeği bütün state değilse yalnız gerçek province listesi aktarılır.
3. ABD, Meksika, Brezilya ve Arjantin gibi vanilla bütünleşik ülkeler ancak tüm doğrudan sahipleri atanıp başkent/şirket uyumluluğu denetlendiğinde kaldırılır.
4. V1 siyasi kart sadece bu üç kontrolün geçtiği küçük coğrafi dilimden üretilir. Koloni şartı, haraç veya ortak taç ise V2 diplomasi katmanına kalır.

Bu defterin hazırlık tabloları, tamamlanan sınır kartlarının nedenini korur. Kesin harita sahibi Kart 5, Kart 6B ve siyasi state karar defteridir.

## 5B — Yeni Endülüs ve Maya çekirdekleri

`card10.json`, bütün `STATE_MEXICO` ve `STATE_VERACRUZ` MEX paylarını Yeni Endülüs'e verir. Yucatán bütünü ve Chiapas'taki yalnız MEX payı Maya Birliği'ne geçer; Chiapas'ın mevcut UCA province'leri korunur. Endülüs'ün ilgili denizaşırı bağımlılıkları `card64.json`da ayrı subject sözleşmeleriyle temsil edilir; Maya'nın iç haraç düzeni siyasi önizlemenin mekanik kapsamı dışındadır.

## 5C — İnci Adaları çekirdeği

`card14.json`, Küba'nın üç state'ini, Jamaika'yı ve Porto Riko'yu İnci
Adaları Koloni Meclisi'nde (`VPI`) birleştirir. Yazılı kaynak bunların
Endülüs koloni sisteminin doğrudan ada çekirdekleri olduğunu açıkça belirtir.
Bu siyasi temsil, ada meclislerini tek yönetime indirmez; `VPI`nin Yeni Endülüs'e bağlı sömürge şartı `card64.json`da `ve_colonial_charter` olarak ayrıca tanımlıdır. Ekonomi ve kurum kuralları sonraki mekanik katmana aittir.

Santo Domingo/Haiti bu karta alınmaz. Kaynak, Hispanyola'nın farklı yerel
idarelerini ayrı tutar; hangi province'lerin İnci Adaları düzeninde olduğu
kararlaştırılmadan Haiti devletinin tamamını devretmek doğru değildir.

## 5D — Kuzey Amerika'nın ABD Sonrası İskeleti

`card15.json` ABD'nin doğrudan sahip olduğu 38 state payını Yeni İngiltere, Yeni
Hollanda, Pennsylvania, Virginia ve Yeni Bursa ile Haudenosaunee, Büyük Göller,
Güneydoğu, Mississippi, Lakota, Pawnee ve Ute aktörlerine aktarır. Yazılı atlasın
kıyı ile iç bölge ayrımının ilk state ölçekli taslağıydı. Nihai province sahipleri Kart 6B ve siyasi state karar defterinde açıkça sabittir. `card16.json`,
son District of Columbia payını Potomac kent bölgesine verir. Bu iki kartın birleşiminde
ABD'nin doğrudan toprağı ve geçici country tanımı kalmaz.

## 5F–5G — Kuzey Kanada'da Şirket Egemenliğinin Sonu

`card17.json` ile `card18.json`, Hudson Körfezi Şirketi'nin bütün doğrudan
province paylarını Vinland, Cree konseyleri, Dene ve Nunavut kıyı meclisleriyle
mevcut Salish/Athabaskan aktörlerine dağıtır. Vinland yalnız Quebec'teki HBC
ticaret payının state ölçekli karşılığıdır; Newfoundland ve Labrador'daki nihai province sahipleri Kart 5/Kart 6B'dedir. Vinland'ın Kalmar tacıyla bağını tek overlord'a çevirmeyen üç karşılıklı ilişki `card64.json`da tanımlıdır. Ontario'da HBC ve yerel sahibin aynı province'i yazdığı vanilla
kesişim, yerel Ontario payı korunarak temizlenmiştir. Birleşik önizlemede HBC
topraksızdır.

## 5H–5I — Meksika Cumhuriyeti Sonrası Yerel Kuşak

`card19.json` ve `card20.json`, Yeni Endülüs/Maya çekirdekleri dışındaki bütün
doğrudan Meksika paylarını Baja, Kaliforniya, Sonora, kuzey plato, Durango,
Oaxaca, Jalisco, Zacatecas ve Rio Grande yerel meclislerine; çok-sahipli
kuzey state'lerde ise mevcut Apache, Comanche, Ute ve Bannock paylarına aktarır.
Colorado'nun ABD ve Meksika payları tek kartta birleştirilmiştir; bu nedenle
önizleme kart sırasına bağımlı değildir. Bajío kent birliği son MEX payını
aldığında birleşik önizlemede MEX topraksız kalır.

## 5J — Fas Brezilyası Kıyı Şartı

`card21.json`, Fas Brezilyası'nı yalnız Pernambuco, Bahia ve Rio de Janeiro
kıyı state'leriyle başlatır. BRZ'nin Amazon, iç yayla ve güneydeki doğrudan
alanları bu kararda **Fas'a aktarılmaz**; BRZ iç yönetimi sonraki yerel
kartlarla parçalanmış, nihai province sahipleri Kart 6B'de sabitlenmiştir. Böylece kıyı yerleşimi anlatısı bir kıta egemenliği
olarak yanlış uygulanmaz.

## 5K–5L — Brezilya İç Havzalarının Ayrıştırılması

`card22.json` BRZ'nin Fas Brezilyası çekirdeği dışındaki kuzeydoğu, São Vicente,
güney plato, Minas ve Mato Grosso paylarını ayrı yerel aktörlere verir.
`card23.json` Goiás merkez payını devrederek BRZ'yi birleşik önizlemede
topraksız bırakır. Amazon/Pará'nın mevcut yerel sahipliği korunmuştur; bu
kart onları tek bir Amazon devleti altında birleştirmez.

## 5M–5Q — Andlar ve Güney Konisi

`card24.json` Charcas/Potosí, La Paz, Atacama, Santa Cruz ve Yukarı Amazon
meclislerini kurar; Mato Grosso'daki ortak BOL payı Brezilya iç kartıyla tek
state işleminde birleştirildiğinden BOL topraksız kalır. `card25.json`–`card26.json`
Arjantin'in doğrudan paylarını Guaraní, Pampa, Tucumán ve Buenos Aires kent
yönetimine; `card27.json`–`card28.json` Şili'nin doğrudan paylarını Mapuçe
çevresi, Güney Nehirleri ve Orta Şili yönetimlerine aktarır. Mapuçe için
vanilla'da ayrı kültür anahtarı bulunmadığından geçici `patagonian` kültür
anahtarı kullanılmıştır; özel kültür tanımı sonraki kültür aşamasına kaydedilir.

## 5R — Quito Krallığı

`card29.json`, `STATE_ECUADOR` ile Pastaza'daki ECU payını Quito Krallığına
aktarır; Pastaza'nın NPU payı korunur ve ECU birleşik önizlemede topraksız
kalır. Cusco için doğrulanmış bir Atlas state kimliği bulunmadığından Peru
çekirdeği bu siyasi kartın kapsamına alınmamıştır.

## 5S — Avustralya ve Aotearoa'da yerel egemenlik

`card41.json`, NSW, WAS, SAS ve TAS'nin bütün doğrudan province paylarını
aynı state'te mevcut yerel aktörlere verir: Karnic, Mara, Kulin, Yolngu,
Kaurna ve Noongar. Tasmania için Palawa Meclisi kurulur. NSW'nin Kuzey Ada
payı Māori NTO'ya döner; Kaurna ve United Tribes'ın Britanya koruma pact'ları
kaldırılır. Mevsimlik Makassar/Mısır ticaret iskeleleri bu harita kartında
ülke sahibi değildir.


## 5T — Guyana'da Hollanda yerleşimi

`card46.json`, `STATE_GUAYANA`daki Fransız ve Britanya province paylarını Hollanda'ya verir. Bu, diplomasi defterindeki Guyana yerleşimleri kararını uygular; yerleşimlerin şirket/bağlılık statüsünü ve iç sınırları değiştirmez.


## 5V — Vinland Newfoundland çekirdeği

`card48.json`, Newfoundland'daki doğrudan Britanya payını Vinland'a verir. Labrador'un kıyı istasyonları ile yerli hinterlandı bu state kararının dışında kalır.


## 5W — Panama Kıstağı Meclisi

`card52.json`, Panama’daki CLM payını yerel Kıstak Meclisi’ne verir. Kanal/liman yatırım hakkı bu siyasi kartta yabancı egemenlik sayılmaz.


## 5X — Kolombiya içinin yerel ayrışması

`card53.json`, Antioquia’yı Yeni İşbiliye çekirdeğine, Cauca ile Guaviare’yi yerel meclislere verir; Amazonas’taki yalnız CLM payı mevcut Amazon sahibine döner. Böylece Muisca, Panama, kıyı ve nehir havzaları tek bir Kolombiya devleti altında birleştirilmez.
