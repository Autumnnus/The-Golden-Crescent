# Kart 2 — Hindistan

**Durum: 2A–2D siyasi sahiplik ve yazılı bağlılık kapanışı doğrulama için hazır. BIC'nin bütün doğrudan payları yerel devletlere dağıtıldı; Lahor Gurkanî, Pencap tepeleri Sih çekirdeği, Keşmir sözleşmeli bağlı, Jaipur/Mewar sınırlı koruma antlaşmalı ve Kandy egemen ada devletidir.**

Bu kartın ilk kabul ölçütü yalnız şudur: Doğu Hindistan Şirketi'nin bütün doğrudan province payları kaldırılacak; başka bir yerel devletin aynı state içindeki payı korunacak. `reset_countries: [BIC]`, şirketin devralınan subject/pact ağını sıfırlar. Bu, İngiltere'nin dünya çapındaki bütün sömürgelerini veya gelecekteki event/on_action etkilerini çözmez.

## Korunmuş state kararı

`10_india` bölgesinde kartta adı geçmeyen state'ler, BIC payı taşımayan ve
yazılı atlasın yeni doğrudan sahibi belirlemediği yerel siyasî düzenlerdir.
Bunlar mevcut province sahibiyle tutulur; her biri state karar defterinde bu
dosyaya bağlı bir korunmuş karar olarak görünür.

| BIC'nin bulunduğu alan | Yeni doğrudan sahip | Yazılı dayanak |
|---|---|---|
| Delhi, Agra | Gurkanî | Delhi–Yukarı Ganj–Yamuna çekirdeği |
| Bihar, Doğu/Batı Bengal | Bengal Sultanlığı | Dakka, aşağı Ganj/Brahmaputra ve Kalküta limanı |
| Bombay | Maratha Konfederasyonu | Pune odaklı batı Dekkan ortaklığı |
| Central Provinces | Nagpur | Maratha ortak üyesi; Pune'nin doğrudan eyaleti değil |
| Awadh, Assam, Mysore, Travankor | Mevcut yerel devletler | Bağımsız nehir/dağ/güney siyaseti |
| Circars, Kurnool | Haydarabad | Merkez/doğu Dekkan |
| Gujarat | Gujarat Liman Birliği | Surat–Kathiawar tüccar düzeni |
| Punjab Hills | Sih Devleti | Kuzey/doğu Pencap ve dağ etekleri; Lahor Gurkanî çekirdeği Kart 2E ile ayrı province sınırı olarak kilitlendi |
| Madras | Tamil krallıkları | Tamil ovaları; Avrupa ticarethaneleri egemenlik değildir. Tek province'lik Danimarka Tranquebar payı [demografi 26'da](../../demography_phase26_middle_east_india/README.md) Tamil krallığına katıldı |
| Orissa | Orissa Krallığı | Yerel kıyı/nehir yönetimi |
| Arakan, Pegu, Tenasserim | Burma | BIC'nin Güneydoğu Asya payı kaldırılır; Pegu'daki tek province Danimarka kalıntısı daha sonra 13. demografi diliminde Burma'ya devredilir |
| Rajputana'daki tek BIC payı | Jaipur | Jaipur–Udaipur koruma düzeninin ilk temsilcisi |

Şirketin state içinde paylaşmadığı bütün province'ler gerçek Atlas katalogundan korunur. Kart bu nedenle BIC'nin tek bir bölgeyi “bütün state” olarak sahiplenmiş sayılmasına izin vermez.

## 2B–2C — Sözleşmeli Keşmir ve Kandy

`card39.json`, Keşmir'in vanilla Pencap vasallığını kaldırır ve Gurkanî ile
sözleşmeli bağlılık kurar. Kullanılan `ve_contractual_vassal` türü %10 gelir
aktarımı ve %35 liberty desire ile dar, başlangıçta doğrulanmış bir pact'tır.
Jaipur ile Mewar (Udaipur), ayrı `ve_limited_protection` türüyle Gurkanî'nin
koruma/katkı antlaşmasına girer: %3 gelir katkısı, ortak savaşa otomatik katılım
yoktur. Jodhpur ve Maratha ortakları bu hiyerarşiye sokulmaz.

`card56.json`, `STATE_PUNJAB`daki doğrulanmış eski PAN province bloğunu
Gurkanî'ye verir; Bahavalpur'un alt-Pencap payı korunur. Aynı kart, Peşaver'de
kalan PAN payını Kabil'e verir; yazılı atlasın üç bağımsız Afgan aktörüne
dördüncü bir Punjab/Sih batı devleti eklemez. `card02.json` yalnız
`STATE_HILL_PUNJAB`daki PAN payını Sih Devleti'ne aktardığı için Lahor ile
Amritsar/dağ çekirdeği iki bağımsız state yazımıyla çakışmaz.

`card40.json`, Ceylon state'indeki BCE, GBR ve MLD province paylarını Kandy
Krallığına verir. Bu, liman sözleşmesini toprak devri saymama kuralıyla
uyumludur: ada üzerinde yabancı doğrudan owner kalmaz.
