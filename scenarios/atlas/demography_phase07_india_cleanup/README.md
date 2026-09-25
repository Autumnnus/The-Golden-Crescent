# Hindistan demografisi: hukuki ve kimlik düzeltmesi

**Etkin kaynak:** `world/scenario.yml`. Bu paket, büyük Hint devletlerinin son nüfus tasarımı değildir. Siyasi haritadaki altı state/ülke payında, vanilla nüfus devrinden kalan iki belirgin senaryo çelişkisini [plan](plan.yml) ve dondurulmuş [POP anlık görüntüsü](legacy-population-snapshot.json) üzerinden düzeltir.

- Bengal'in H7 yazılı hukuku insan mülkiyetini yasaklar. Bihar, Doğu Bengal ve Batı Bengal'deki toplam **2.426.580** `slaves` POP'u aynı kültür, din ve kişi sayısıyla serbest POP'a çevrildi. Bu, kırsal borç bağımlılığını veya kira eşitsizliğini sona erdirmez.
- Bağımsız Gurkanî, Bengal ve Maratha/Nagpur topraklarındaki toplam **55.754** Britanyalı/İskoç memur, subay ve aristokrat, aynı meslek ve kişi sayısıyla ilgili bölgenin yerel kültür–din kadrosuna çevrildi. Az sayıdaki yabancı kapitalist özel tüccar olarak kalabilir; yeni bir Britanya hükümeti yaratılmaz.

Atlas aday doğrulama/rapor/build/önizleme, `prepare.py`/`verify.py`, etkin `atlas build/check`, siyasi denetim ve aday–etkin POP eşitliği geçti. Bu fazın sonunda dünya nüfusu **1.073.677.323** idi; sınırlar ve diplomasi değişmedi. Daha sonraki [Hint çekirdeği nüfus fazı](../demography_phase08_indian_core/README.md) toplamı değiştirdi. Statik kontrolde 0 hata, önceki 25 ordu/state uyarısı var. Oyun motorunda açılış testi ve Bengal'in H7'ye uygun **oyun kanunu** henüz yapılmadı; bu paket yalnızca POP statüsünü düzeltir.

## Sonraki sayısal tasarımda çözülmesi gereken fark

Siyasi harita kilitlendikten sonra ilk ekonomi hedefleri ile Atlas aktarımı uyuşmaz hale geldi. Aşağıdaki sayılar **faz 7 sonundaki doğrudan ülke nüfusudur**; bağlıları ve Maratha ortaklarını iki kez saymaz. Hedefler faz 8'de düzeltildi.

| Birim | Etkin nüfus | Önceki yazılı hedef | Toprak kapsamı / yorum |
|---|---:|---:|---|
| Gurkanî `MUG` | 29.816.697 | 48–58 milyon | Agra, Delhi ve Lahor/Pencap payları; hedef bu sınıra göre yüksek kalıyor |
| Bengal `BGL` | 51.067.260 | 25–31 milyon | Bihar **da** Bengal'de; eski hedef yalnız Bengal çekirdeğini varsaymış olabilir |
| Maratha `MAR+GWA+IND+NAG` | 18.331.769 | 30–38 milyon | Pune/Bombay, Gwalior, Indore ve Nagpur ayrı hazineler; `MAR` tek başına 12.248.856 |

[İzleyen faz](../demography_phase08_indian_core/README.md), bu farkları toprak ve taşıma kapasitesiyle uzlaştırıp bölge başına nüfus/okuryazarlık ve kent profili seçti. Sih `PNJ`, Keşmir `KAS`, Racput, Awadh, Haydarabad ve güney devletleri ayrı nüfus kartları gerektirir. `SIK` etiketi Sih Devleti değil Sikkim'dir.
