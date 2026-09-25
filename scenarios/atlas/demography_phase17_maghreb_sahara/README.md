# Demografi 17 — Mağrip, Sahra ve Moritanya kuşağı

Bu paket [Afrika tasarımındaki](../../../docs/scenario/senaryo_afrika.md) ayrı Fas, Cezayir, Tunus, Trablus ve vaha/otlak yönetimlerini koruyarak **16 state'teki 24 ülkenin 40 doğrudan payını** işler. Yedi ülkenin faz dışında da toprakları vardır: `ADG`, `ADR`, `AJJ`, `FTR`, `OUA`, `RGB`, `TBI`. [Plandaki](plan.yml) onların nüfus hedefi yalnız bu 16 state'teki **kısmi** toplamdır; diğer bölge payları aynen korunur. Uygulama öncesi ortak POP kayıtları [dondurulmuştur](source-pops.json).

| Ülke / bu fazın payı | Önce | Etkin nüfus | Ağırlıklı okuryazarlık girdisi |
|---|---:|---:|---:|
| Fas `MOR` | 3.287.716 | 3.350.000 | %29,08 |
| Cezayir `MAS` | 2.198.179 | 2.250.000 | %31,29 |
| Konstantin `CON` | 1.521.724 | 1.550.000 | %30,00 |
| Tunus `TUN` | 1.315.008 | 1.350.000 | %39,00 |
| Trablus `TRI` | 782.104 | 800.000 | %26,41 |
| Fizan `FZN` | 168.640 | 170.000 | %17,58 |
| Mzab `MZB` | 10.991 | 11.000 | %19,00 |
| Tuareg `TUA` | 12.000 | 12.000 | %8,00 |

Diğer 16 yerel yönetimin pay hedefleri aynı planda ayrı satırlardır. Bölge toplamı **10.261.182 → 10.469.600** kişidir; dünya toplamı **1.091.625.226** olur. Fas'ın Fes mektepleri, Tunus'un hukuk/ticaret ağı ve Cezayir limanları daha yüksek okuryazarlık girdisi alır; çöl ve göçer paylarına aynı seviye yayılmaz. Bu girdiler oyunun ilk gün eğitim sonucunu garanti etmez.

Mevcut Maghrebi, Berber, Bidan, Haratin, Fulbe, İbadi, Yahudi ve küçük Akdeniz tüccarı toplulukları aynı ortak kültür–din gruplarında korundu. Dar kimlik düzeltmesi `TUA` için yapıldı: ülkesi kurulu oyunun mevcut `tuareg` kültürünü Berber'in yanında birincil kültür olarak alır, `STATE_SAHARA/TUA` payındaki 12.000 kişi `tuareg/sunni` olur. Diğer Berber/Mzab veya Tuareg ülkelerinin POP'ları değiştirilmez. **378.451 açık köle mesleği** miras alındığı sayıda korunur; ilgili ülke raporlarında kölelik kanunları vardır. Bu sayı sömürü rejiminin nihai dengesi veya etik onayı değildir; kanun/istihdam ve oyun motoru etkisi ayrıca incelenmelidir.

[17 yerleşim profili](city-profiles.yml) Fes, Marakeş, Tanca, Cezayir, Oran, Konstantin, Tunus, Misrata, Bingazi ve vaha/nehir merkezleri için state nüfusunun **içindeki** tasarım alt kümeleridir. Kurulu yerelleştirme Libya'daki Trablus şehir hub'ını `Trablusşam` diye adlandırdığı için bu hub'a yanıltıcı bir profil yazılmadı. `STATE_SAHARA`daki `Ghardaia` hub'ı da mevcut haritada Tuareg `TUA` province'indedir; Mzab `MZB` merkeziyle uyumsuzluğu siyasi/yer adı denetiminde açık kalır. Bu yerleşim profilleri yeni POP, bina veya sanayi işi yaratmaz.

[Önizleme](../../../build/maps/maghreb-sahara-demography.html) **0 siyasi sınır değişikliği** gösterir. `verify.py`, hedef dışı POP bloklarını ve bütün ülke/state/diplomasi alanlarını korur; kısmi ülke toplamlarını faz dışı nüfusla birlikte kontrol eder. Atlas doğrulaması 675 state, 557 kara sahibi ülke için **0 hata ve önceki 25 uyarı** verdi. Motor testi bu yeni dilim için yapılmadı.
