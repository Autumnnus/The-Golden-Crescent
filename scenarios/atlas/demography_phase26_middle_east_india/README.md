# Demografi 26 — Ortadoğu ve Hindistan kalıntısı

Bu paket [yazılı atlasın](../../../docs/scenario/dunya_atlasi.md) Rûm dışındaki Ortadoğu aktörlerini ve Hindistan'ın son dört payını nüfusa uygular. **25 ülkenin 31 doğrudan payı** etkin Atlas kaynağına işlendi. Ortadoğu ve Hindistan teknik bölgelerinde açık pay kalmadı. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Tranquebar düzeltmesi

Kullanıcı kararıyla (24 Eylül 2026) [siyasi betik](political.py) Madras'taki tek province'lik Danimarka `DEN` Tranquebar payını Tamil Krallıkları (`TAM`) payına katar. Hindistan kartının "Avrupa ticarethaneleri egemenlik değildir" kuralı ve Faz 13'teki Pegu emsali uygulanır. TAM'ın Faz 09 planındaki bütün gruplar aynen korunur; Tranquebar'ın dondurulmuş **34.313** kişisi (201 Danimarkalı tüccar dahil) üstüne eklenir (8.700.000 → 8.734.313). Danimarka'nın Avrupa ve Karayip payları değişmez. Kara sahibi ülke sayısı 555 kalır; toplam pay sayısı 1.046 olur.

## Kararlar

- Rûm bağlısı Adana, Erzurum ve Trabzon atabeylikleri ile Kürdistan, Şam, Cebel-i Lübnan, Kudüs, Basra, Kuveyt, Hicaz, Necid, Cebel Şammar, Yemen ve Körfez yönetimlerinin devralınan yerel ortak kültür–din grupları korunur. Levant ve Mezopotamya payları yazılı tasarımdaki sulama/depolama avantajı nedeniyle %3–4 büyür; Arabistan hemen hemen sabittir.
- **Lübnan:** Devralınan Şii ağırlığı (%54) dağ düzenine göre düzeltildi: Maruni (`mashriqi/catholic`) %33, Dürzi ve Şii topluluklar (`mashriqi/shiite` karşılığı) %25, Sünni %24,5, Rum Ortodoks %13, Ermeni Katolik, Rum ve Yahudi toplulukları.
- **Kölelik:** Hukukta H8 sayılan Rûm bağlıları ve küçük hanedanlar (Adana, Erzurum, Trabzon, Kürdistan, Şam, Lübnan, Kudüs, Kuveyt) devralınan Çerkes/Gürcü/Afrikalı ev kölelerini tutuyordu ama kölelik kanunları yoktu; Sennar emsaliyle `law_debt_slavery` aldılar. H7 Basra tüccar cumhuriyetinin **3.530** kölesi serbest bırakıldı. Arabistan, Yemen, Umman ve Körfez devletlerinin vanilla köle ticareti/borç köleliği kanunları ve köle POP'ları korunur.
- **Faz 09 kalıntısı:** TAM'ın önceki planında **244.323** köle POP'u vardı ama kölelik kanunu yoktu. Tamil krallıkları için H8 varsayılanı ve tarihsel tarımsal bağımlı emek gereği `law_debt_slavery` yazıldı.
- Maskaren Ada Meclisi (`VMB`) birincil kültürü, nüfusuyla uyumlu Fransız kreolü `afro_antillean` oldu. Racputana'daki küçük Indore/Gwalior payları devralınan Racput bileşimiyle kalır.
- Homeland: devralınan yerel homeland'ler bu pakette eşiksiz korunur (Madras'taki Kannada dahil); yalnız Laristan'a `baluchi`, Maskaren'e `afro_antillean, french` eklendi.

| Alan | Önce | Etkin başlangıç |
|---|---:|---:|
| 31 hedef pay (TAM birleşik pay dahil) | 15.878.290 | 16.086.613 |
| Açık köle mesleği | — | 438.586 |
| Dünya nüfusu | 1.079.090.157 | 1.079.264.167 |

[55 yerleşim profili](city-profiles.yml) payın planlı kültür–din gruplarına orantılı tasarım alt kümeleridir (Şam, Beyrut, Kudüs, Musul, Diyarbakır, Erzurum, Trabzon, Basra, Maskat, Mekke, Medine, San'a, Aden, Port Louis...). Petrol çağı kuruluşları (Dammam, Dahran, Abkayk) profillenmedi.

## Doğrulama

Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/middle-east-india-verification.json), etkin Atlas `build/check` (**0 hata; 25 uyarı**), güncellenen siyasi denetim ve 38 araç öz testi geçti. Motor testi yapılmadı. Rûm bağlılarının ve Levant emirliklerinin kalan kanun/teknoloji başlangıcı hukuk aşamasına kalır.

Yeniden üretim: `middle-east-india-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `political.py` → `scenario build --out build/scenarios/middle-east-india-political` → `snapshot.py` → `prepare.py` → `scenario validate/build --out build/scenarios/middle-east-india-candidate` → `verify.py`.
