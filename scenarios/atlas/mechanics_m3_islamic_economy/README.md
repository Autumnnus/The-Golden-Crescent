# M3-lite — İslam dünyasının tüketim ekonomisi

**24 Eylül 2026 · etkin.** İkinci oyun testinde hayat standardı hâlâ kötüydü. M2'den sonra İslam çekirdeğinde milyon kişi başına 7–10 bina seviyesi vardı (Rûm 9,5; İsfahan 6,8). Karşılaştırma için VEL'de bu değer 41, İsveç'te 28'dir. M1b ile yükselen okuryazarlık beklenen hayat standardını da artırdığı için bu paket İslam dünyasının ekonomisini kanondaki önceliğe göre yoğunlaştırır. Oyun başlangıç servetini de kurulumda ekonomiden yeniden hesaplar (`00_starting_pop_wealth.txt` notu), yani asıl kaldıraç bina ve istihdamdır.

## Plan ([fill.py](fill.py) → [fill-plan.yml](fill-plan.yml))

1. **Rûm, Faz 1B.2:** [1B.2 paketinin](../phase01b2_rum_economy/README.md) 25 eyalet payındaki sanayi planı (Marmara çelik–alet–motor, Kastamonu kömürü, İzmir dokuması, Konya tahılı, Bağdat–Halep kâğıt/eğitim...) aynen yazıldı: 1.161 açık seviye. Rûm'un kademe 1 paketinde eksik olan `canneries`, `mechanized_workshops` ve `rifling`, M1 kanonuna ([overrides.yml](../mechanics_m1_institutions/overrides.yml) `add`) eklendi. Bölünmüş eyaletlerde ekilebilir alan ve kaynak sınırları güncel diğer sahiplerle yeniden denetlendi; kırpma gerekmedi. 11 üniversite kaydında boş kalan ilke yöntemi etkisiz yöntemle dolduruldu. Rûm 257 → 1.239 seviye (milyon kişi başına 45,9).
2. **Diğer İslam payları:** Merkezsiz olmayan ve en az 50 bin kişilik her İslam payı yoğunluk hedefine tamamlandı. Hedefler: çekirdek 32, tanınmış 20, tanınmamış 16 seviye/milyon. Tahmini istihdamın payın %27'sini aşmaması gerekir. Karışım tüketim önceliklidir: tahıl %28, hayvancılık %12, balıkçılık %8, kereste %10, dokuma %12, mobilya %10, gıda sanayii %8, cam %4, nakit ürün %8 (çay/kahve/tütün/pamuk). Kalan ihtiyaç tahıl ve tüketim sanayiine gider. Müslüman tüketici için damıtımevi yöntemi seçilmez; köle yöntemleri seçilmez. Mevcut seviye ve yöntemler korunur. 119 paya 3.166 seviye eklendi.

| Grup | Nüfus | Seviye/milyon, önce → sonra |
|---|---:|---:|
| İslam çekirdeği (tanınmış) | 57,1 M | 8,6 → **38,4** |
| Mısır | 11,5 M | 9,0 → **31,7** |
| Diğer İslam, tanınmış | 149,3 M | 7,2 → **20,4** |
| Diğer İslam, tanınmamış | 54,0 M | 16,1 → **20,0** |
| Batı–orta Avrupa / Avrupa üst / güney–doğu | — | 19,9 / 15,2 / 13,3 (değişmedi) |
| Doğu Asya | 417 M | 5,9 (değişmedi) |

Dünya toplamı 10.250 → **14.398** seviye.

## Yeniden üretme

```sh
cp world/scenario.yml build/mechanics/m3-source.yml
cp build/world-political/active-political-report.json build/mechanics/m3-source-report.json
python3 scenarios/atlas/mechanics_m3_islamic_economy/fill.py
python3 scenarios/atlas/mechanics_m3_islamic_economy/prepare.py
python3 scripts/tools.py atlas scenario validate build/mechanics/m3-candidate.yml
python3 scripts/tools.py atlas scenario build build/mechanics/m3-candidate.yml --out build/scenarios/m3-candidate
python3 scenarios/atlas/mechanics_m3_islamic_economy/verify.py
```

`verify.py` şunları denetler: yalnız planlanan payların sanayisi ve Rûm teknolojisi değişti; nüfus, kanun ve diğer teknolojiler korundu; Rûm 1B.2 teknolojilerinin tamamına sahip; yeni uyarı yok. Etkinleştirme sonrası `check` 0 hata, 15 uyarı; siyasi denetim geçti.

## Sınırlar ve sonraki işler

- Bu statik bir plandır. Fiyat, kâr, ücret ve hayat standardı motor sonucudur ve oyunda ölçülmelidir. Pazarın talebini aşan fabrikalar kârsız kalıp işçi çıkarabilir.
- 1B.2'nin kapasite denetimindeki açıklar (boya, kumaş, et, ipek, odun) ticarete bırakıldı; Rûm'un pazar ilişkileri henüz kurulmadı.
- Avrupa, Çin, Hindu devletleri ve Afrika'da yoğunluk M2 düzeyinde kaldı. Oyunda hayat standardı bu bölgelerde de çok düşük çıkarsa aynı planlayıcı daha düşük hedeflerle uygulanabilir.
- Yazılı sanayi havzalarının geri kalanı (Tebriz, İsfahan–Kaşan, Kahire–İskenderiye, Jiangnan, Varşova–Kraków, Ren–Saksonya–Bohemya, İsveç metal merkezleri) ve şirketler tam M3'e aittir.
