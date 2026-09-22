# Kart 3 — Doğu Asya ve denizler

**Durum: 3A–3F siyasi sahiplik ve deniz sözleşmesi kapanışı doğrulama için hazır. Çin ayrımı, Filipinler, Ryukyu, Batılı Malaya payları ve Mısır/Umman'ın beş liman sözleşmesi ayrı kayıtlardadır.**

Çing sonrası `CHI` sahibi olan her province, beş Çin yönetiminden birine veya yazılı atlasın ayrı İç Asya aktörüne aktarılır. Bir state içindeki başka ülke payı değişmez.

## Korunmuş state kararı

`11_east_asia` ve `12_indonesia` içinde kartta yeniden yazılmayan state'ler,
senaryonun özellikle büyük dönüşüm öngörmediği Japonya, Kore ve yerel deniz
düzenleridir. Yeni bir dış egemen veya misyoner sömürgesi varsayılmaz; mevcut
yerel province sahipliği bilinçle korunur ve state karar defterinde bu dosyaya
bağlanır.

| Siyasi aktör | Karttaki state çekirdeği |
|---|---|
| Kuzey Çin | Beijing, Hebei, Shandong, Shanxi, Henan, Xi'an, Gansu, Ningxia, Qinghai |
| Jiangnan | Nanjing, aşağı Yangtze, Anhui, Hunan–Hubei, Jiangsu/Jiangxi/Zhejiang |
| Shu | Sichuan, Chongqing, Guizhou, Yunnan |
| Yue | Guangdong/Guangxi, Fujian, Formosa |
| Mançurya | Shengjing ile kuzey/güney/outer Mançurya ve Amur |
| Moğol hanlıkları | Hinggan, Urga, Uliastai, Tuva |
| Cungar / Kaşgar / Kazak / Kırgız | Altay–Cungarya / Tarım / Jetisy / Kırgızya |

Yunnan–Guizhou, Hunan–Hubei ve Gansu, yazılı atlasın tarif ettiği geniş özerk sınır kuşaklarıdır. Bu kart onları önce doğrudan dış çatı sahibine verir; yerel özerklik mekanizması siyasi sınırlar kilitlendikten sonra tasarlanacaktır.

## 3B — Güneydoğu Asya ve takımadalar karar defteri

Yazılı atlas Batılı Hristiyan sömürge baskısının ana etken olmadığını, ama Mısır/Umman güdümlü her ticari bağlantının da doğrudan egemenlik olmadığını söyler. Bu nedenle bir vanilla Avrupa province'i doğrudan Mısır veya Umman'a aktarılmayacaktır. Her liman için dış taraf, ev sahibi, hak türü ve tarih önce kayda geçer.

| Alan | Doğrulanmış Atlas state adayları | Kilitli siyasi karar |
|---|---|---|
| Anakara hanedanları | `STATE_CAMBODIA`, `STATE_LAOS` ve Vietnam/Burma/Siam state'leri | Yerel hanedan/Şan/Lao/Khmer paylaşımı ile dış ticaret ayrı tutulur |
| Malay boğazı | `STATE_ACEH`, `STATE_MALAYA` | Aceh, Johor ve Minangkabau ayrı egemendir. Aceh–Mısır ikmal/ambar sözleşmesi 1824; Johor–Umman seçilmiş tarife/konvoy sözleşmesi 1828'dir. |
| Java | `STATE_WEST_JAVA`, `STATE_CENTRAL_JAVA`, `STATE_EAST_JAVA` | DEI payları yerel saraylara gerçek province'leriyle döner; Yogyakarta/Surakarta payları korunur |
| Borneo | `STATE_NORTH_BORNEO`, `STATE_WEST_BORNEO`, `STATE_EAST_BORNEO` | Kıyı sultanlıkları ile ada içi toplumların sınırı; tek bir Borneo devleti kurulmaz |
| Filipinler | `STATE_LUZON`, `STATE_VISAYAS`, `STATE_MINDANAO` | Tondo, Visaya liman birlikleri ve Sulu ayrı dinî-siyasi alanlardır; Sulu–Umman silah/geçiş sözleşmesi 1829'dur, tabiiyet değildir. |
| Bali–Makassar–Maluku | `STATE_CELEBES`, `STATE_MOLUCCAS`, `STATE_SUNDA_ISLANDS` | Makassar (SLW)–Mısır tamir/ambar sözleşmesi 1821'dir; yerel ada çekirdekleri ile sınırlı dış üs/şirket hakkı birbirinden ayrılır. |
| Avustralya/Aotearoa | Yerli siyasi temsil birimleri Kart 5S/6B'de seçildi | Mevsimlik Makassar/Mısır iskelesi toprak devri değildir; doğrudan sahiplik karar defterinde yerel aktörlerdedir |

Bu defter, Avrupa kolonisini kaldırmakla aynı anda yeni bir denizaşırı Müslüman imparatorluk yaratılmasını önler. Doğrudan owner değişikliği ilgili kart ve siyasi state karar defterinde kilitlidir; koruma, tekel, kira veya ziyaret hakkı V2 diplomasi/Flavor bağlamına kalır.

## 3C–3D — Filipinler ve Ryukyu

`card38.json`, PHI'nin Luzon payını Tondo Birliği'ne, Visayas'ı Visaya Liman
Birliği'ne, Mindanao payını Sulu'ya ve Batı Mikronezya payını MCR'ye verir.
Mevcut Mindanao yerel sahipleri korunur. Vanilla kaynakta iki kez atanmış
`xE90347` province'i MGD'de bırakılarak Atlas'ın tek-sahip kuralı sağlanır.

`card40.json` Ryukyu'nun Japon haraç pact'ını kaldırır. Japon/Yue ile yazılı
çifte törensel ve ticari ilişki, askerî tabiiyet yaratmayan ayrı bir diplomasi
ve Flavor bağlamı olarak kalır.


## 3E — Malay Boğazında yerel egemenlik

`card51.json`, Malaya’daki Britanya doğrudan province’lerini Johor’a verir. Bu, Batılı Hristiyan doğrudan sömürge etkisini haritadan çıkarır. `card58.json`, liman sözleşmeleri için yalnız başlangıç ilişki iklimini kaydeder; ACE, JOH, SLW ve SUL üzerinde Mısır/Umman state sahibi veya subject kaydı yaratmaz.

## 3G — Anakara mandala düzeni ve Ezo

`card60.json`, vanilla vassallıkları olduğu gibi taşımak yerine Burma–Şan,
Vietnam–Kamboçya ve Siam–Champasak/Chiang Mai/Luang Prabang ilişkilerini %4
katkılı, otomatik savaşa katılmayan `ve_mandala_autonomy` ile yeniden kurar.
Siam–Vietnam rekabeti -25 ilişkiyle açıktır; devletlerin iç egemenliği korunur.
Japonya'nın iç düzeni büyük ölçüde korunduğundan Ezo, ayrı Ainu/Japon yerel
alanıyla `ve_japanese_domain` olur; bu dış sömürge ilişkisi değildir.
