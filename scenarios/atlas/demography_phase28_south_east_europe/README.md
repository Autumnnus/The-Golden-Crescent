# Demografi 28 — Güney ve Doğu Avrupa (son paket)

Bu paket İtalya devletleri, kuzey İberya krallıkları, Balkan emirlikleri ve krallıkları, bağımsız Macaristan ve Erdel, Tuna prenslikleri, Bohemya'nın Silezya'sı, Baltık Prusya Dükalığı ve Kraków'un **28 ülkedeki 61 doğrudan payını** etkin Atlas kaynağına işler. Böylece dünyanın **1.046/1.046 state–ülke payında** açık nüfus planı vardır. Sınır, bağlılık, kanun ve bina değişmedi. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Kararlar

- Devralınan nüfus yazılı tasarımla uyumludur ve ölçeği korunur.
- **Bağımsız Macaristan:** Habsburg'un 18. yüzyıl Tuna Şvabı iskânı bu evrende yoktur (Habsburg kişisel birliği yok). Banat, Bačka, Bekes ve Transdanubia'da `south_german` POP'u **1.034.940 → 380.266** olur; yerini Macar, Sırp, Rumen, Hırvat/Bunyevac ve Slovak nüfus alır. Buda, Pest ve Pressburg'un ortaçağ kent Almanları korunur.
- **Besarabya:** 1812 sonrası Rus/Alman kolonistleri kalkar; Bucak Nogayları (`tatar`) ve küçük Bulgar/Gagauz toplulukları kalır (544 bin → 500 bin).
- **Kuzey İberya:** İspanya'nın toplu sürgünleri yaşanmadığından Kastilya ve Aragon'da Sefarad toplulukları, Valensiya ve Aragon'da Mudéjar Müslümanları (`spanish/sunni`, **101.762**) sürer.
- **İtalyan limanları:** Venedik (Fondaco dei Turchi), Livorno, Napoli ve Sicilya'da küçük Rûm, Rum, Ermeni, Mağribi ve Sefarad tüccar toplulukları vardır.
- **Eflak ve Boğdan:** Kurulu oyunda Roman köleliğinin karşılığı olan `romanian/orthodox/slaves` POP'ları (237.033) vanilla `law_legacy_slavery` ile korunur.
- Okuryazarlık geciken Avrupa ölçeğindedir: Doğu Prusya %38, Kraków %36, Silezya %34, Milano %32, Venedik %30, Macaristan %26, Aragon %24 (Katalonya %28), Kastilya %20, Papalık %18–22, Tuna Emirliği %14, Galiçya %14, Sicilya %12, Sırbistan/Bosna/Arnavutluk/Eflak %10, Sardinya %10, Karadağ %6.
- Homeland: devralınan yerel homeland'ler korunur (Slovenya'nın ortaçağ Almanları dahil); ≥%10 kültürler eklenir.

| Alan | Önce | Etkin başlangıç |
|---|---:|---:|
| 61 hedef pay | 60.834.305 | 60.790.200 |
| Dünya nüfusu | 1.079.263.915 | 1.079.219.810 |

[62 yerleşim profili](city-profiles.yml) 1836 tasarım tahminleridir (Napoli 350 bin, Palermo 170 bin, Roma 150 bin, Madrid Endülüs'ün kuzeyindeki Kastilya krallığının kenti olarak 120 bin). Hepsi state nüfusunun içindedir.

## Doğrulama

Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/south-east-europe-verification.json), etkin Atlas `build/check` (**0 hata; 25 uyarı**), siyasi denetim ve 38 araç öz testi geçti; önizleme 0 sınır değişikliği gösterir. Motor testi yapılmadı.

Yeniden üretim: `south-east-europe-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `snapshot.py` → `prepare.py` → `scenario validate/build --out build/scenarios/south-east-europe-candidate` → `verify.py`.
