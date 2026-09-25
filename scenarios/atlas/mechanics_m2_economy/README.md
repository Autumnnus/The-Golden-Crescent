# M2 — Temel ekonomi

[Mekanik aşama planının](../../../docs/scenario/MEKANIK_ASAMA_PLANI.md) ikinci paketi. İlk oyun testindeki çok düşük hayat standardı ve tavan yapan tahıl/giyim fiyatları, siyasi aşamada 314 state'in vanilla binalarının düşürülmesinden kaynaklanıyordu. Bu state'lerde **747 M kişi** (dünyanın %70'i) yaşıyor ve etkin dünyada yalnız 3.228 bina seviyesi vardı.

## M2a — Vanilla bina tabanının geri getirilmesi

[restore.py](restore.py), M1 ile teknoloji kazanan sahipler için 314 state'i `buildings: inherit`'e çevirir ve vanilla binaları uyarlar ([restore-plan.yml](restore-plan.yml)):
- Seviyeler state'in güncel/vanilla nüfus oranıyla yalnız aşağı ölçeklenir (en az 0,25). Tahmini iş sayısı nüfusun %28'ini aşan 23 state'te ölçek, iki turda orantılı küçültüldü (ör. Tennessee 0,31, Sahalin 0,03).
- Sahibin kullanamadığı üretim yöntemleri aynı gruptaki ilk kullanılabilir yöntemle değiştirildi (245 değişiklik). Vanilla kayıtlarında eksik kalan gruplar da kullanılabilir yöntemle dolduruldu; böylece Atlas plantasyonlarda varsayılan köle emeği yöntemine düşmez.
- Teknolojisi olmayan, kıyısız state'te liman/donanma, izinsiz ürün veya kaynak yatağı olmayan binalar kaldırıldı (111 kayıt). Başka ülkeye veya şirkete ait sahiplikler yerelleştirildi (53).
- Sonuç: vanilla'nın 5.486 seviyesinin 5.191'i geri geldi.

## M2b — Kural tabanlı temel ekonomi

[fill.py](fill.py), merkezsiz olmayan her state payında bina yoğunluğunu kademe hedefine tamamlar ([fill-plan.yml](fill-plan.yml)). Hedef, milyon kişi başına kademe 1'de 7, 2'de 6, 3'te 5, 4'te 4,5, 5'te 4 ve 6'da 3 seviye. Doldurma sırası:
1. Hükümet idaresi.
2. State'in izin verdiği tahıl (pirinç, buğday, mısır, çavdar, darı).
3. Hayvancılık, kereste ve kıyıda balıkçılık.
4. Kademe ≤5 ise gıda, dokuma ve mobilya.

Paylaşılan ekilebilir alan ve kaynak sınırları gözetilir. 133 paya **1.917 seviye** eklendi; hedefin altında pay kalmadı.

| Ülke | Önce | Sonra | Seviye / milyon |
|---|---:|---:|---:|
| Jiangnan | 0 | 1.045 | 7,0 |
| Kuzey Çin | 0 | 507 | 5,0 |
| Bengal | 0 | 300 | 6,0 |
| Lehistan–Litvanya | 0 | 291 | 9,5 |
| Rûm | 1 | 257 | 9,5 |
| Endülüs | 0 | 151 | 8,6 |
| Moskova | 0 | 139 | 9,0 |
| Paris | 0 | 227 | 19,1 |

## Doğrulama ve sınırlar

Dünya toplamı **3.228 → 10.254** seviye (vanilla başlangıcına yakın). [verify.py](verify.py) yalnız bina politikası/endüstri alanlarının değiştiğini, nüfus, ülke, sınır ve diplomasinin aynı kaldığını denetler. Etkin `build/check` 0 hata verdi; yeni uyarı yalnız Goiás ve Rio Grande do Norte'deki tek seviyelik binaların işgücü tahminidir. Siyasi denetim ve öz testler geçti.

**Motor testi gerekli:** Hayat standardı, fiyatlar ve işsizlik ancak oyunda ölçülebilir. Rûm, İsfahan, Tebriz ve Jiangnan gibi yazılı sanayi havzaları henüz temel düzeydedir; M3 (Rûm 1B.2 dahil) bunları ekleyecek. Şirketler ve altyapı dengesi yoktur.
