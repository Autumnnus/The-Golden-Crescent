# Demografi 12 — Himalaya ve kuzey bozkır kuşağı

Bu dilim [yazılı dünya atlasındaki](../../../docs/scenario/dunya_atlasi.md) bağımsız Tibet, Cungarya, Moğol hanlıkları, Nepal, Bhutan ve Sikkim'in **13 doğrudan state payını** etkin Atlas kaynağına işler. Kaşgar yalnız Tianshan'da, Tibet Çin yönetimlerinden ayrı, Nepal/Bhutan/Sikkim kendi paylarında kalır. Sınır, ülke tanımı ve diplomasi değişmez. [Plan](plan.yml) kesin nüfus ve okuryazarlık girdilerini, [dondurulmuş POP kaynağı](source-pops.json) önceki oyun dağılımını gösterir.

| Ülke | Doğrudan nüfus | Ağırlıklı okuryazarlık girdisi | State payı |
|---|---:|---:|---:|
| Tibet `TIB` | 2.950.000 | %18,64 | 3 |
| Cungarya `DZH` | 320.000 | %21,31 | 2 |
| Moğol hanlıkları `MGL` | 2.900.000 | %17,21 | 5 |
| Nepal `NEP` | 4.300.000 | %17,00 | 1 |
| Bhutan `BHU` | 125.000 | %14,00 | 1 |
| Sikkim `SIK` | 85.000 | %15,00 | 1 |

Önceki 10.468.388 kişilik toplam **10.680.000** oldu; artış 211.612 kişidir. Bu, nüfusu keyfî olarak büyütme değil, devralınan state ağırlığını ve yayla/otlak sınırlamasını koruyan ölçülü bir başlangıç tercihidir. Tibet'in Lhasa ve Ngari payları toplamın çoğunu taşır. Moğol ülkesi içindeki Hıngan'ın Han ve Moğol karma nüfusu ile Tuva'nın Tuvan çoğunluğu silinmedi.

Kurulu oyundan devralınan bazı ortak kültür–din çiftleri yazılı siyasi bağlama uymuyordu. Cungarya state'inde Moğol/Gelugpa nüfusu yalnızca yaklaşık 14 bin, Han nüfusu yaklaşık 181 bindi; [planda](plan.yml) hanlığın otlak çekirdeği çoğul hâle getirilirken Kazak, Uygur, Han ve Mançu toplulukları korunur. Altay'da Moğol/Gelugpa ve yerel animist gelenekler birlikte temsil edilir; Tatar ve Rus azınlıklar kalır. Lhasa/Ngari'deki büyük `han/animist` blokları daha küçük Han/Mahayana azınlıkları ve Tibetli inanç grupları olarak tasarlandı. Nepal'in büyük `bihari/animist` bloğu Bihari/Hindu ve küçük Nepalli/animist grup olarak ayrıldı. Bu oranlar alternatif evren **tasarım girdisidir**; ayrı tarihsel nüfus sayımı iddiası değildir. Diğer yedi payın devralınan ortak kültür–din oranları korunur.

[14 hub yerleşim profili](city-profiles.yml) toplam **915.000** kişiyi state POP'larının içinde yaklaşık alt küme olarak gösterir; yeni oyun nüfusu, bina veya meslek değildir. Atlas adayında şehir isimleri kurulu Türkçe hub adlarıyla, hub province sahibi ve kültür–din alt toplamları gerçek POP'larla doğrulandı. `STATE_EASTERN_HIMALAYAS` için oyun bütün hub türlerini Bhutan'a ait tek province'e bağlar: bu nedenle Sikkim ve Tibet'in aynı state'teki payına yanlış konumlu şehir profili uydurulmadı. Gangktok adı kurulu oyunda mine hub olarak geçse de mevcut siyasi payda o hub Bhutan'dadır; ayrı yerleşim/harita düğümü işi açık kalır.

`prepare.py` etkin kaynaktan bağımsız aday üretir; `verify.py` 13 payı, şehir alt kümelerini, diğer dünya POP'larını, bütün siyasi sınırları ve diplomasiyi karşılaştırır. [Atlas önizlemesi](../../../build/maps/himalaya-steppe-demography.html) sınırda değişiklik göstermez. Aday validate/build, etkin build/check ve siyasi denetim geçti: **0 hata, önceki 25 uyarı**. Dünya nüfusu **1.089.843.424** oldu. Atlas raporunda `DZH` ve `MGL` başlangıç bina seviyesi **0**; nüfusun iş/ordu kapasitesi varmış gibi yorumlanmamalıdır. Binalar, kanunlar, teknoloji, ordu ve motor içinde POP yerleşimi sonraki aşamalardır. Bu revizyon oyun motorunda ayrıca açılıp test edilmedi.
