# Kart 4 — Afrika

**Durum: 4A–4H siyasi sahiplik, kıyı ve emirlik sözleşmesi kapanışı doğrulama için hazır. Avrupa kıta sömürge payları ile dört Omani liman enclave'i yerel sahiplere devredildi; Zanzibar'ın ayrı denizaşırı divanı ve Sokoto–Gobir emirlik sözleşmesi korunur.**

## Korunmuş state kararı

`03_north_africa` ve `04_subsaharan_africa` içindeki kartta adı geçmeyen
state'ler, yazılı atlasın başka bir doğrudan hükümdar tayin etmediği yerel
hanlık, şehir ve kıyı düzenleridir. Avrupa kıta sömürgeciliğini veya Omani
liman hakkını doğrudan sahiplik saymadan mevcut yerel province dağılımı
korunur; state karar defteri her birini bu belgeye bağlar.

## 4A — Mağrip yerel egemenlikleri

Yazılı atlas Cezayir, Tunus ve Trablus'u ayrı denizci yönetimler olarak tutar; Mısır'ın ya da Avrupa'nın uzantısı yapmaz. `card06.json`, Cezayir, Oran ve Konstantin'deki bütün Fransız province paylarını sırasıyla mevcut MAS/CON yerel yönetimlerine döndürür. Devlet mevcut yerel Magrip province'lerini bir araya getirerek tek bir “Cezayir devleti” icat etmez.

Tunus, Trablus ve Fas halihazırdaki yerel sahiplikleriyle uyumludur. İberya'daki ve Afrika dışındaki Fransız toprakları bu kartın konusu değildir. Sahra, Sahel, Nil/Boynuz, doğu kıyısı, Büyük Göller ve güney Afrika kendi karar listeleri ile ayrı eşlenecektir.

## 4B — Kıta içi ve kıyı karar defteri

Afrika için yabancı liman erişimi doğrudan renkli toprak anlamına gelmez. Aşağıdaki state adayları, yerel aktörlerin gerçek sahiplik kartına geçmeden önce doğrulanan kapsamı gösterir; kent adı state kimliğiyle örtüşmüyorsa yeni katalog gereklidir.

| Alan | Doğrulanmış state adayları | Kart öncesi zorunlu karar |
|---|---|---|
| Nil ve Çad geçişi | `STATE_DONGOLA` Mısır'a ait; `STATE_DARFUR`, `STATE_WADDAI` yerel çoklu sahiplik taşır | Sennaar state kimliği, Dongola güneyi ve Mısır'ın yalnız nehir koridoru |
| Sahel/Sahra | `STATE_HAUSALAND`, `STATE_OUTER_HAUSALAND`, `STATE_EAST_HAUSALAND`, `STATE_TIMBUKTU` | Sokoto emirlik sözleşmesi, Massina–Timbuktu ilişkisi ve hareketli Tuareg alanının sabit sınırdan ayrılması |
| Gine ve iç batı | `STATE_DAHOMEY`, `STATE_BENIN`, `STATE_SENEGAL` | Aşanti/Oyo/Segu/Futa aktörleri için state ve province eşlemesi; Rufisque/Whydah yabancı depo hakkının egemenlik olmaması |
| Orta Afrika | `STATE_CONGO`, Kasai ve Luba–Lunda için katalogla doğrulanacak state'ler | Kongo/Loango/Luba/Lunda ayrı ağları ve Fas tacirlerinin kıyı ambar hakkı |
| Büyük Göller | `STATE_UGANDA` | Buganda/Bunyoro/Ruanda/Burundi yerel province eşlemesi; tek göl devleti yaratılmaması |
| Boynuz ve Svahili kıyı | `STATE_SOMALILAND`, `STATE_ZANZIBAR`; Habeş yaylası state'leri katalogla doğrulanacak | Begemder/Şewa/Tigray/Harar ayrımı; Umman–Zanzibar ortak tacı ve Mısır'ın Massava/Dahlak kira hakkı |
| Güney ve adalar | `STATE_ZULULAND`, `STATE_BOTSWANA`, `STATE_NORTH_MADAGASCAR`, `STATE_SOUTH_MADAGASCAR` | Zulu/Basotho/Xhosa/Tswana ve güneybatı otlak ağları; Britanya/Hollanda kıyı ikametinin Cape kolonisi olmaması |

Bu defter tamamlanmadan Avrupa liman province'leri yerel olmayan başka bir metropole aktarılmaz. Her V1 kartı, yerel doğrudan owner listesini kapatmalı; depo, tamir, kira, konsolosluk ve gemi yatırımı ilişkileri V2 diplomasi/Flavor kaydına gitmelidir.

## 4C — Sennaar ve Mısır'ın Nil sınırı

`card13.json`, Mısır'ın doğrudan Nil yönetiminin Dongola'da bittiği yazılı
kararını `STATE_BLUE_NILE` için uygular. Mavi Nil state'indeki bütün EGY
province'leri bağımsız `VSN` Sennaar Sultanlığı'na geçer. Bu, Mısır'ı Nil
deltası–Dongola ve Sina koridorundan çıkarmadan Sudan'ın tamamını Mısır'a
yazmama kuralını haritada görünür kılar.

Kordofan ve Eritre'nin doğrudan sahibi `4D` ile kesinleşir. Massava/Dahlak'taki
Mısır kira ve ikmal hakkı state egemenliği değildir; bu nedenle kart, Eritre'yi
tek uydurma devlet altında birleştirmez.

## 4D — Kordofan, Eritre ve Altın Sahil kapanışı

`card54.json`, yazılı Nil sınırını tamamlar: `STATE_KORDOFAN`daki bütün Mısır
payı Darfur'a, `STATE_ERITREA`daki Mısır payı mevcut Afar yönetimine döner. Bu,
Massava/Dahlak ikmal sözleşmesini toprak egemenliği saymaz.
`STATE_GOLD_COAST`taki Danimarka ve Hollanda depo province'leri de Aşanti'ye
katılır. Böylece kıta üzerinde yabancı küçük liman payı kalmaz; depo ve ticaret
hakkı yalnız diplomasi/Flavor katmanında temsil edilir.

## 4E–4F — Umman liman enclave'leri ve sözleşme iklimi

`card57.json`, Omani devletin Mombasa, Abu Dabi ve Makran/Bampur'daki vanilla
liman province'lerini sırasıyla Mombasa, Abu Dabi ve Makran yerel sahiplerine
iade eder. Maskat–Umman çekirdeği, Laristan kıyısı ve Zanzibar divanı bu kararın
dışındadır. `card58.json` yalnız Mombasa–Umman liman sözleşmesinin başlangıç
ilişki değerini kurar; Svahili kıyısının tamamını Umman'a bağlı veya doğrudan
Omani saymaz. Kaynak state'te iki kez yazılmış `x5C1ADA` kıyı province'i Witu
yerel yönetiminde tutulur; harita tek sahip kuralını bu açık tercihle uygular.

## 4G — Sokoto, Gobir ve Timbuktu'nun ayrı statüleri

`card59.json`, doğrulanmış Gobir (`HAU`) devletini Sokoto'ya %5 katkı ve
otomatik savaşa katılım olmadan `ve_emirate_compact` ile bağlar. Sokoto'nun
doğrudan Hausa state payları ortak makamın kendi alanıdır; Bornu ve Borgu bu
emirlik değildir. Timbuktu oyun ölçeğinde Massina'nın payı ile Kel Adagh, Kel
Ataram, Adrar, Tagant ve Reguibat yerel paylarına bölünür. Massina–Timbuktu
ilmî/ticari şartı şehir hukuku olduğundan ikinci bir ülke veya sahte subject
yaratmaz.

## 4H — Güneyde kalan iki Boer siyasi payı

[Demografi 20 siyasi düzeltmesi](../../demography_phase20_rest_africa/README.md), yazılı atlasın “Boer cumhuriyetleri yok” kararına rağmen `STATE_VRYSTAAT` ve `STATE_TRANSVAAL` içinde kalmış `ORA`/`TRN` doğrudan paylarını sırasıyla `BST` ve `MTB` yerel yönetimlerine aktarır. Nüfus ile diplomasi korunur; dört state'teki Boer homeland kaydı kaldırılır. Önizleme kartı eskidir; etkin denetim bu dar son aktarımı ayrıca doğrular.
