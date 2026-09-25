# Demografi 21 — Kuzey Amerika (Endülüs Meksikası hariç)

Bu paket [Amerika tasarımının](../../../docs/scenario/senaryo_amerika.md) kıyı kolonisi / iç kıta ayrımını nüfusa uygular. **62 state'te 45 ülkenin 95 doğrudan state–ülke payı** etkin Atlas kaynağına işlendi. Meksika'nın 15 state'i (Yeni Endülüs, Maya ve yerel meclisler) ayrı Endülüs Amerika'sı paketine bırakıldı. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Siyasi kalıntıların dar düzeltmesi

Kullanıcı kararıyla (24 Eylül 2026) iki vanilla kalıntısı yeni yerel ülkelere geçti. [Siyasi betik](political.py) yalnız sahip etiketini değiştirir, province listeleri aynı kalır:

| State | Eski sahip | Yeni sahip | Province | Gerekçe |
|---|---|---|---:|---|
| `STATE_ALASKA` | `ALK` Rus-Amerikan şirketi | `VTU` Tlingit–Unangan Kıyı Meclisi | 287 | Yazılı kanon Alaska'da Rus egemenliği ve tek Athabaskan devleti varsaymaz |
| `STATE_TEXAS` | `TEX` Dixie Teksas cumhuriyeti | `VCD` Caddo Konfederasyonu | 81 | ABD yerleşim genişlemesinin sonucu olan cumhuriyet bu evrende yoktur |

- `ALK`'nin Sahalin'deki iki province'i (793 kişi) bu pakette değişmedi; başkenti `STATE_SAKHALIN` olarak düzeltildi. Kuril/Sahalin'deki bu küçük Rus şirketi kalıntısı Sibirya paketinde ele alınmalı.
- `TEX` topraksız kaldığı için üretilen katmanlardan çıkar. Kara sahibi ülke sayısı **555 → 556** oldu.
- Yeni meclislerin teknolojisi yoktur. Rus şirketinin limanı ve balina istasyonu (`navigation` ister) ile Teksas'ın mısır çiftliği ve deniz idaresi düşürüldü: **4 bina seviyesi** (3.233 → 3.229). Alaska'daki kereste kampı kaldı. Amerika'daki diğer yerel meclisler gibi bina/teknoloji başlangıcı ekonomi aşamasına kalır.
- Diplomasi değişmedi; iki etiketin başlangıç ilişkisi yoktu.
- **Oyun testi sonrası düzeltme (24 Eylül 2026):** İlk yeni başlangıçta Alaska'daki kereste kampının hâlâ `company_russian_american_company` sahipliğiyle üretildiği ve `create_building` hatası verdiği görüldü. Kamp VTU'nun kendi mülkü (`ownership: self`) olarak yeniden üretildi; nüfus ve sınır değişmedi.

## Nüfus

| Kapsam | Pay | Önce | Etkin başlangıç |
|---|---:|---:|---:|
| Kıyı kolonileri ve taç bağımlılıkları | 20 | 9.866.055 | 9.120.200 |
| İç kıta ve kuzeyin yerel devletleri | 75 | 8.459.581 | 4.840.000 |
| Yerel devletlerdeki yerleşimci/diaspora POP'ları | | 7.239.526 | 417.540 |
| Dünya nüfusu | | 1.093.551.034 | 1.089.185.598 |

- **İç kıta:** Kullanıcının seçtiği ölçülü düzeyde (~4,8 M) devralınmış ABD/Kanada yerleşimci akını kaldırıldı. Haudenosaunee (Ohio 450 bin), Büyük Göller birliği (590 bin), Mississippi nehir birliği (1,07 M), Cherokee (580 bin), Muscogee (270 bin) ve Choctaw (200 bin) kendi halklarıyla başlar. Küçük tüccar, yerleşimci ve özgür Afrikalı-Amerikalı toplulukları kalır. Ova, Büyük Havza, Pasifik ve kuzey paylarının zaten yerel olan nüfusu hafifçe (%0–10) artırıldı. Kaliforniya, misyon sistemi olmadığı için 64 binden 150 bine çıkar.
- **Koloniler:** Yeni İngiltere 2,04 M, Yeni Hollanda 2,43 M (Hollandalı çoğunluk %44 + Yankee, Valon, Huguenot, Sefarad ve Haudenosaunee toplulukları), Pennsylvania 1,54 M, Virginia 2,585 M. Vinland 310 bine iner: devralınan **667.200 Franco-Canadian** yerine Norveç, İsveç, Danimarka, İzlanda ve Fin yerleşimcileri ile Algonquian, Iroquoian, Cree ve Inuit halkları gelir. Yeni Bursa 70 bin kişilik karma Rûm kolonisidir (Türk, Mashriqi, Rum, Ermeni, Sefarad, Mağribi; özgür Afrikalı-Amerikalılar ve Muscogee).
- **Kölelik:** Açık köle mesleği yalnız Virginia ve Potomac'ta korunur (**938.000**). İkisine `law_legacy_slavery` yazıldı; Potomac 1808–1820 ilga listesinde olmadığı için Chesapeake plantasyon düzeninde sayıldı. H7 Pennsylvania, 1820 ilgalı Yeni Bursa ve H9 yerel devletlerdeki **1.092.705** devralınmış köle POP'u serbest bırakıldı ya da yerleşimci akınıyla birlikte kaldırıldı. Yeni İngiltere, Yeni Hollanda ve Vinland'da zaten köle POP'u yoktu.
- **Kimlik düzeltmeleri:** Arapaho (`ARP`) ve Blackfoot (`BLF`) `siouan` yerine `algonquian`; Kaliforniya birliği (`VCL`) `nahua` yerine `hokan`. Trail of Tears bu evrende yaşanmadığından Oklahoma'daki `SEQ`'in 50.800 Cherokee'si yerine Caddo/Wichita ve Osage ağırlığı gelir; birincil kültürleri `caddoan, siouan, cherokee` oldu. `cajun` (58.269) ve Fransız-Kanadalı kimlikler Amerika'dan kalktı. `metis` yalnız küçük Nordik–Cree ticaret aileleri için protestan alt grup olarak kalır.
- **Homeland:** 62 state için kural tabanlı yeniden yazıldı: planlı nüfusun ≥%10'u olan kültürler ile devralınan yerel homeland'ler (≥%1) kalır; yerleşimci/diaspora homeland'leri yalnız ≥%10 ise korunur. Örnek: Ohio `yankee` → `iroquoian, algonquian`; Quebec `franco_canadian` → `algonquian, norwegian, swedish, iroquoian`; Teksas → `comanche, caddoan`. Hesap [denetim dosyasındadır](../../../build/demography/north-america-audit.json).
- Oyun kültürleri geniş karşılıklardır: `athabaskan` Tlingit/Haida'yı, `inuit` Unangan/Alutiiq'i, `muskogean` Natchez ve aşağı Mississippi halklarını, `salish` Chinookan kıyı halklarını, `hokan` Kaliforniya'nın farklı dil ailelerini temsil eder. Yerli inançların oyun karşılığı `animist`'tir. Hıristiyan ve Müslüman dönüşümler cemaat bazında küçük paylardır.

[32 yerleşim profili](city-profiles.yml) state nüfusunun **içindeki** tasarım alt kümeleridir; ek POP veya bina üretmez. Yalnız bu evrende makul adlar profillendi: erken kıyı kolonisi adları (Boston, Providence, Philadelphia, Brooklyn, Richmond, Baltimore, Charleston, Quebec) ve yerel dillerden gelen adlar (Chicago, Milwaukee, Toronto, Mobile, Biloxi, Chattanooga, Tallahassee, Tampa, Omaha, Wichita, Tucson). New York, Washington, St. Louis, New Orleans, Montreal, New Archangel gibi kurulu hub adları anakroniktir; yerelleştirme kararı açık olduğu için profillenmedi ve oyundaki görünen adlar değişmedi.

## Doğrulama

[Bölgesel önizleme](../../../build/maps/north-america-demography.html) yalnız Alaska ve Teksas'ı siyasi değişiklik olarak gösterir ([değişiklik haritası](../../../build/maps/north-america-changes.png)). Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/north-america-verification.json) (siyasi düzeltmenin yalnız iki state'i değiştirdiği, ülke tanımı farklarının plandakilerle sınırlı olduğu, hedef dışı POP ve nüfusların aynı kaldığı, köle POP'larının yalnız kölelik kanunlu ülkelerde bulunduğu, üretilen homeland'lerin ve hub sahiplerinin planla eşleştiği), etkin Atlas `build/check` (**0 hata; önceki 25 uyarı**), güncellenen [siyasi denetim](../world_political/active_political_audit.py) ve 38 araç öz testi geçti. Negatif sınamada bozulan bir denetim kaydı dört hata üretti.

**Açık kalanlar:** Bu sonuçlar statik kaynak testidir; yeni sınırlar ve nüfus oyun motorunda açılarak sınanmadı. `SEQ`'in vanilla `law_legacy_slavery`, `law_racial_segregation` ve cumhuriyet kanunları H9 hukukuyla çelişir; hukuk aşamasında düzeltilmeli. Siyasi haritada `STATE_NEW_YORK`'un tamamı Yeni Hollanda'dadır; yazılı kanondaki iç New York Haudenosaunee alanı yalnız %5,5 Iroquoian nüfus ve homeland ile temsil edilir. Yerel devletlerin bina/teknoloji/kanun başlangıcı yoktur; okuryazarlık oyunun ilk gün hesabında değişebilir.

**Yeniden üretim:** `north-america-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadan dondurulmuştur. Sıra: `political.py` → siyasi adayı `scenario build --out build/scenarios/north-america-political` → `snapshot.py` (dondurulmuş kaydı üzerine yazmaz) → `prepare.py` → `scenario validate/build --out build/scenarios/north-america-candidate` → `verify.py`. Etkin oyun dosyaları yalnız Atlas `build` ile yazılır.
