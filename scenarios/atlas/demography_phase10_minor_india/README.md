# Demografi 10 — küçük Hint devletleri

Bu dilim, [yazılı Hindistan atlasındaki](../../../docs/scenario/dunya_atlasi.md) **37 küçük ülkenin 40 doğrudan state payını** etkin Atlas senaryosuna çevirir. Chitral'ın Keşmir ve Orta Asya'daki Pashtunistan payları birlikte sayılır. Hindistan çekirdeği ve önceki 15 büyük ülkenin rakamları, sınırlar ve diplomasi korunur. Hedefler ayrıntısıyla [planda](plan.yml), önceki ortak POP'lar [dondurulmuş kaynakta](source-pops.json) bulunur.

| Bölgesel küme | Ülkeler | Doğrudan nüfus toplamı | Okuryazarlık girdisi |
|---|---:|---:|---:|
| Gujarat–Kathiawar (`BER BHV DHA IDA JUN KUT NAW PLP`) | 8 | 2.650.000 | %16–20 |
| Bundelkhand–Malwa–plato (`BAG BUN JHN SUR BAS JEY BHO`) | 7 | 3.615.000 | %14–19 |
| Pencap–Himalaya–Racput (`PTA GAR CHT LAD BHW ALW BIK JAS KOT`) | 9 | 3.200.000 | %14–20 |
| Odişa–Bengal çevresi–güney (`MYB NAR ORI PTN COO SAT KHP KNO PUD`) | 9 | 3.460.000 | %15–21 |
| Assam–Manipur sınırı (`MNP NGA MGH TIP`) | 4 | 630.000 | %12–16 |
| **Toplam** | **37** | **13.555.000** | Ülke ayrı girdileri planda |

Bu hedefler önceki 13.436.274 kişilik aynı doğrudan ülke toplamından **118.726 kişi** yüksektir. Yeni dünya toplamı **1.083.888.492** kişidir. Ülke hedefi iki state'e ayrıldığında eski state nüfus ağırlıkları kullanılır; hiçbir bağlı ülke üst devlet nüfusuna ikinci kez eklenmez. Bölgesel kültür–din çiftleri korunur. Tek kasıtlı yeniden ağırlıklandırma Chitral'ın ana payındadır: oyundan devralınan Pashtun çoğunluğu, ülkenin kurulu `kho` ana kültürüne uygun Kho çoğunluğuna çekildi; Pashtun ve Pencaplı topluluklar silinmedi.

[16 adlandırılmış hub yerleşimi](city-profiles.yml) devletin kendi province'inde doğrulandı. Kent tahminleri ortak kültür–din POP toplamlarının **alt kümesidir**; yeni game POP, bina, iş veya kentleşme oranı üretmez. Diğer küçük devletlerin oyun verisinde kendi payına düşen adlandırılmış hub bulunmadığı için onlara uydurma şehir profili eklenmedi.

**Açık temsil ve hukuk borcu:** Kurulu oyunda Khasi adına ayrı bir kültür yok; `MGH` (Khasi) şimdilik vanilla `naga` POP/ülke kültürüyle temsil edilir. `TIP` (Tipperah) için devralınan `lushai` de ayrıntılı Tripuri/Bengal topluluğunu tam anlatmaz. Bu iki kimlik daha sonra oyun kültürü tanımı ve homeland etkileriyle ele alınmalı. Bastar, Chitral, Bahawalpur ve Cooch Behar'da toplam **93.017** devralınmış köle mesleği POP'u vardır. Kesin hukuk/labor geçişi yazılmadan bunları otomatik serbest veya iki kez saymadım; ilgili başlangıç kanunları ayrı fazda denetlenmelidir.

`prepare.py` Atlas adayını üretir; `verify.py` 40 payın gerçek kültür–din/meslek sayılarını, 37 ülke toplamını, şehir alt kümelerini ve diğer ülke POP'larının korunmasını denetler. [Önizleme](../../../build/maps/minor-india-demography.html) siyasi sınırda değişiklik göstermedi. Atlas validate/build, etkin build/check ve siyasi denetim geçti: **0 hata, önceki 25 uyarı**. Oyun motorunda bu demografi sürümü henüz açılıp test edilmedi. Burma ve sınır aşan `KKI`/`DEN`, Mascarene `VMB`, Çin/Kaşgar ve ekonomi–kanun–ordu profilleri sonraki çalışma alanlarıdır.
