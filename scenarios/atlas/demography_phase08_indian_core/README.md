# Demografi 8 — Hint çekirdeği

**Etkin kaynak:** `world/scenario.yml`. [Plan](plan.yml), altı ülke etiketinin 10 doğrudan state payına nüfus, ortak kültür–din grupları ve okuryazarlık girdisi atar. [Önceki Hint kimlik düzeltmesi](../demography_phase07_india_cleanup/README.md) temel alındı; Bengal'de köle POP geri gelmedi ve bağımsız Hint devletlerine sömürgeci idari POP geri eklenmedi.

| Ülke | Doğrudan nüfus | Ağırlıklı okuryazarlık girdisi | Toplumsal ağırlık |
|---|---:|---:|---|
| Gurkanî `MUG` | 36.000.000 | %24,44 | Hindu çoğunluk; Delhi/Agra'da Hintustani, Lahor/Pencap'ta Pencaplı Müslüman, Hindu ve Sih topluluklar |
| Bengal `BGL` | 50.000.000 | %24,98 | Bihar dahil; ülke genelinde Hindu çoğunluk, doğu deltada Sünni çoğunluk |
| Maratha/Pune `MAR` | 15.000.000 | %20,00 | Bombay–Pune kıyısı ve Dekkan'ın kendi hazinesi |
| Gwalior `GWA` | 1.800.000 | yaklaşık %18 | Malwa ve değişmeden kalan küçük Rajputana payı |
| Indore `IND` | 700.000 | yaklaşık %17 | Malwa ve değişmeden kalan küçük Rajputana payı |
| Nagpur `NAG` | 5.000.000 | %18,00 | Marathi, Chhattisgarhi ve Gondi bölgeler |

**Maratha dört üyesi toplamı 22.500.000 kişidir.** Bu siyasi/askerî ortaklık, Pune'ye ikinci kez eklenen bir nüfus veya gelir değildir. Gurkanî rakamı Keşmir ve Racput bağlılarını içermez. Bengal'in önceki 25–31 milyonluk tasarım hedefi, Bihar'ın da doğrudan sınırları içinde olduğu kesin haritayla uyuşmadığından [ekonomi hedefinde](../../../docs/scenario/ekonomi_ve_toplum.md) 46–53 milyona düzeltildi. Gurkanî ve Maratha aralıkları da harita ile başlangıç taşıma kapasitesine uygun ölçüye çekildi. Seçilen sayılar önceki vanilla aktarımından ölçülü farklar üretir; büyük nüfus çarpanları veya kolonilerden gizli transfer kullanılmadı.

[26 şehir/hub tahmini](city-profiles.yml) toplam **10.590.000** kişiyi state POP'larının içinde gösterir: Gurkanî 3,51 milyon, Bengal 4,93 milyon, dört Maratha üyesi 2,15 milyon. Kalan kasabalarla yazılı kentleşme aralıklarına yer vardır. Bu profiller ayrı oyun POP'u üretmez veya iş/konut ekonomisini simüle etmez. Hub adları kurulu oyunun Türkçe yerelleştirmesinde kontrol edildi. Bu dilim hazırlanırken Malwa'daki “İndore” wood hub'ı Gwalior payındaydı; bu nedenle şehir profili Indore'nin zaten sahip olduğu Ujjain'i kullanmıştı. [Sonraki şehir merkezi düzeltmesi](../city_anchor_corrections/README.md) İndore hub province'ini Indore devletine taşıdı; eski şehir tahmini ek nüfus olarak sayılmaz.

`prepare.py` [dondurulmuş POP anlık görüntüsü](legacy-population-snapshot.json) üzerinden küçük cemaatleri, eski meslekli POP'ları ve faz 7'deki serbest statüyü koruyarak aday üretir. `verify.py` nüfus/okuryazarlık, ortak kültür–din/meslek adetleri, diğer POP bloklarının korunması ve şehir alt kümesi sınırlarını denetler. Atlas aday doğrulama/rapor/build/önizleme ile etkin `build/check`, siyasi denetim ve aday–etkin POP eşitliği geçti: **0 hata, önceki 25 ordu/state uyarısı**. Oyun motorunda açılış/ekonomi testi ve gerçek 1 Ocak okuryazarlığı ölçümü yapılmadı. Jain gibi bu oyun sürümünde ayrı din kimliği bulunmayan küçük topluluklar anlatıda korunur; mevcut Hindu oyun kategorisinden sayısal olarak ayrışmaz.

**Açık ekonomi kapısı:** Atlas raporunda Bengal `BGL` ile Pune `MAR` için başlangıç bina seviyesi hâlâ **0** görünüyor; siyasi kurulum eski sömürge binalarını bilinçli olarak devralmamıştı. Bu nüfus fazı yeni sanayi/bina veya oyun kanunu eklemez. Bu iki ülkenin üretim, istihdam ve vergi dengesi ancak ayrı bir ekonomi fazı ve motor testiyle oynanabilir sayılabilir.
