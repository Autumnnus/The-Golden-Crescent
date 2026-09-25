# Demografi 14 — Malay takımadaları, Yeni Gine ve Filipinler

Bu dilim [yazılı dünya atlasındaki](../../../docs/scenario/dunya_atlasi.md) **26 ayrı ülkenin 36 doğrudan state payını** etkin Atlas kaynağına işler. Johor, Aceh, Cava sarayları, Borneo kıyıları, Makassar–Maluku, Bali/Lesser Sunda, Papua ve Filipin siyasi alanları ayrı kalır. Siyam'ın Malaya payı [önceki anakara diliminde](../demography_phase13_mainland_seasia/README.md) belirlenmiştir ve bu dilimde korunur. Mısır/Umman liman sözleşmelerinden yeni subject, koloni veya province doğmaz.

[Plan](plan.yml) ülke toplamlarını, her state payının okuryazarlık girdisini ve üç Filipin kültür–din düzeltmesini kaydeder. [Dondurulmuş POP kaynağı](source-pops.json) uygulama öncesi oyun gruplarıdır. Bölgenin devralınmış **18.582.911** kişisi **19.304.000** oldu; artış 721.089 kişidir. Dünya toplamı **1.091.251.856** kişidir. Bunlar doğrudan ülke nüfuslarıdır; bağımlı veya liman sözleşmesi tarafları yeniden sayılmaz.

| Seçilmiş ülke | Doğrudan nüfus | Ağırlıklı okuryazarlık girdisi |
|---|---:|---:|
| Yogyakarta `YOG` | 6.200.000 | %21,28 |
| Surakarta `SRK` | 2.200.000 | %20,96 |
| Bali/Lesser Sunda `BAL` | 1.680.000 | %17,00 |
| Tondo `VTD` | 1.500.000 | %20,00 |
| Visaya `VVS` | 1.100.000 | %18,00 |
| Papua `PPU` | 770.000 | %8,53 |
| Aceh `ACE` | 430.000 | %22,00 |

Diğer 19 ülkenin kesin toplamları aynı [planda](plan.yml) ayrı satırlardır. Borneo'daki Dayak/Bornean/Hakka, Sumatra'daki Batak/Sumatran, Cava'daki Cava/Yue, Maluku'daki yerel inanç/Müslüman ve Yeni Gine'deki Melanezyalı nüfuslar tek dış sömürgeci kültüre çevrilmedi. Küçük Hollandalı/Portekizli tüccar ve yerel Hristiyan azınlıklar devralındığı yerde kaldı. **449.113 açık köle mesleği** önceki başlangıçtan aynen korundu; mevcut ülke kanunları ve iş ilişkileri ayrıca dengelenmelidir.

İspanyol egemenliği olmayan bu evrende devralınmış Luzon/Visaya Katolik çoğunluğu uygun değildi. Tondo'nun açık POP başlangıcı **%85,2 yerel `animist` / %14,8 Katolik**, Visaya'nınki **%81,8 / %18,2** olarak kuruldu; Tagalog, Ilocano ve Visayan kültürleri ayrı kalır. İki ülkenin resmî din girdisi `animist` oldu. `animist`, yerel farklı inançların oyundaki kaba karşılığıdır; tek bir birleşik din iddiası değildir. Sulu'nun Mindanao payında Moro/Sünni, Lumad/yerel inanç ve daha küçük Visayan/Katolik grupları birlikte kalır. İspanyol ve `filipino_mestizo` kimlikleri sıfırlanmadı fakat kolonici devlet olmamasına uygun küçük düzeye çekildi.

[31 hub yerleşim profili](city-profiles.yml) toplam **1.898.000** kişiyi ilgili state POP'larının tahmini alt kümesi olarak gösterir; yeni oyun nüfusu, iş veya bina değildir. Her ad ve hub province sahibi kurulu Türkçe oyun verisiyle, kültür–din alt toplamı aday POP'larla denetlendi. Hub'ı başka sahibin province'inde kalan Perak gibi paylara yanlış konumlu şehir profili eklenmedi. `Batavia`, `George Town` ve `Port Moresby` gibi devralınmış hub adlarının alternatif evren adlandırması ayrıca incelenmelidir.

`prepare.py --source build/demography/maritime-seasia-source.yml` dondurulmuş önceki kaynaktan adayı yeniden üretir; `verify.py` 36 payı, 31 yerleşimi, diğer dünya POP'larını, iki resmî din düzeltmesini, sınırları ve diplomasiyi denetler. [Atlas önizlemesinde](../../../build/maps/maritime-seasia-demography.html) siyasi sınır değişikliği yoktur. Aday validate/build, etkin build/check ve siyasi denetim geçti: **0 hata, önceki 25 uyarı**.

**Açık motor/kimlik işi:** Kurulu oyunun `tagalog`, `visayan` ve `ilocano` kültür tanımlarında varsayılan din hâlâ `catholic`; bu dilim açık POP ve ülke başlangıç dinini değiştirir, kültür tanımlarını henüz değiştirmez. Uzun süreli din/karakter davranışı ile `VTD`, `VVS`, Papua, Sulawesi ve Mindanao'nun sıfır bina başlangıcı oyun motorunda ve sonraki ekonomi/kimlik aşamasında ele alınmalıdır. Bu revizyon oyun içinde ayrıca açılıp test edilmedi.
