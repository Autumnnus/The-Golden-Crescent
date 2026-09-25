# Demografi 5 — Britanya'nın üç ayrı tacı

**Etkin kaynak:** `world/scenario.yml`. Ortak hükümdar nüfusları birleştirmez: İngiltere–Galler `VEL`, İskoçya `VSC`, İrlanda `VIR` ayrı devletlerdir. On üç state/ülke payı [plan.yml](plan.yml) ile düzenlendi; [dondurulmuş vanilla POP'ları](legacy-population-snapshot.json) küçük ve meslekli toplulukların korunmasını sağlar.

| Taç | Doğrudan nüfus | Ağırlıklı okuryazarlık girdisi | Başlangıç çoğulluğu |
|---|---:|---:|---|
| İngiltere–Galler | 14.200.000 | %36,51 | Katolik kurumlar; güçlü reform cemaatleri; Galler ayrı dil/kültür |
| İskoçya | 2.400.000 | %45,60 | Lowlands reform ağı; Highlands Gaelic ve Katolik topluluklar |
| İrlanda | 5.200.000 | %25,65 | İrlandalı Katolik çoğunluk; Ulster'de ayrı İskoç/İngiliz yerleşimciler |

Üçü de yazılı nüfus ve okuryazarlık hedeflerindedir. İngiltere–Galler'de yaklaşık 8,02 milyon Katolik ve 6,12 milyon Protestan; İskoçya'da 1,61 milyon Protestan ve 795 bin Katolik; İrlanda'da 3,86 milyon Katolik, 1,30 milyon Protestan bulunur. Bunlar alt state'lere aynı oranda dağıtılmaz. İrlanda'nın eski 8,02 milyonluk vanilla devri 5,2 milyona indirildi; Ulster'in mevcut mülk sahibi, asker ve subay POP türleri sayı ve kimlikleriyle korundu. Denizaşırı `GBR` ve Yeni İngiltere `VNI` nüfusu üç taç toplamına eklenmez.

[Şehir profilleri](city-profiles.yml) Londra, Manchester, Liverpool, Cardiff, Birmingham, York, Leeds, Cambridge, Bristol, Plymouth, Edinburgh, Glasgow, Inverness, Dublin, Belfast, Cork ve Galway için toplam **3.305.000** kişilik tahmin içerir. England–Wales şehirleri 2,44 milyon (%17,18), İskoç şehirleri 380 bin (%15,83), İrlanda şehirleri 485 bin (%9,33) kişidir; diğer kasabalar için yazılı kentleşme aralıklarında yer kalır. Bu tahminler oyun motoruna ayrı şehir POP'u olarak yazılmaz; state nüfusunun alt kümeleridir. Hub adları kurulu oyun yerelleştirmesinde doğrulandı.

Atlas `build/check` sıfır hata verdi; siyasi denetim ile bu paketin `verify.py` denetimi geçti. Önceki 25 ordu/state uyarısı sürüyor. `verify.py`, üç taç hedeflerini, eski meslekli POP'ları, diğer ülkelerin POP bloklarının değişmediğini ve şehir gruplarının state'i aşmadığını denetler. Yeni demografiyle oyun motorunda başlangıç/zaman ilerletme testi henüz yapılmadı; nüfus ve okuryazarlık girdileri ekonomik bina istihdamının veya gerçek 1 Ocak okuryazarlığının simülasyonu değildir.
