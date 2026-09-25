# Demografi 1 — Rûm'un 1836 toplumsal başlangıcı

**Etkin kaynak:** `world/scenario.yml`. Bu paket, siyasi sınırları değiştirmeden Rûm'un 25 doğrudan state payına nüfus, ortak kültür–din dağılımı ve okuryazarlık girdisi ekler. Önceki `phase01b_rum_demography` taslağının 27 milyonluk nüfus ve state ağırlıkları bugünkü sınırlarla birebir eşleştiği için kullanıldı. Yeni kültür–din kararları [plan.yml](plan.yml) içindedir; eski taslak bunların kaynağı değildir.

## Sonuç

- Rûm'un doğrudan nüfusu **27.000.000**; bağlı ülkeler buna eklenmez. 25 state payının toplamı tam eşittir. Nüfus ağırlıklı okuryazarlık girdisi **%40,18** olup yazılı %38–44 hedefindedir; oyun motorunda ölçülmüş sonuç değildir.
- Nüfusun yaklaşık %44,37'si Türk, %26,81'i Rum, %9,12'si Maşrıkî kültüründedir. İnanç dağılımı yaklaşık %53,49 Sünni, %31,74 Ortodoks, %6,13 Şii, %4,58 Doğu Ortodoks ve %2,92 Yahudidir. Bunlar bütün Rûm'un ağırlıklı toplamlarıdır; her eyalet için aynı oran kullanılmaz.
- Halep'teki Arap Ortodoks ve Şii, Ankara'daki Türk Şii, Van'daki Ermeni/Kürt, Selanik'teki Sefarad toplulukları ayrı ortak gruplardır. Kültür ve din marjinalleri bağımsız çaprazlanmaz.
- Vanilla POP kaydında `slaves` olarak işaretlenmiş **91.404** kişinin kültür, din ve nüfusu korunur; Rûm'un yazılı 1811 özgürleşmesine uygun biçimde başlangıç köle POP türü kaldırılır. Diğer ülkelerin POP kayıtları değişmez.
- Dokuz büyük yerleşim için toplam **4,2 milyonluk** ayrı [şehir profili](city-profiles.yml) vardır. Victoria 3 başlangıç nüfusunu state region ve ülke payı düzeyinde sakladığından bu şehir sayıları oyunda ayrı bir şehir POP'u olarak yazılmaz. Her şehir profili, ait olduğu state'in ortak kültür–din gruplarını aşmayacak şekilde denetlenir. Kalan kentler ve kır nüfusu state toplamının içindedir.

## Şehir kapsamı

| Yerleşim | State payı | Tasarım tahmini | Sınır notu |
|---|---|---:|---|
| Konstantiniyye | Eastern Thrace / RUM | 1.050.000 | 2.876.000 kişilik state'in kent çekirdeği |
| Bursa | Hüdavendigar / RUM | 450.000 | Marmara sanayi ve eğitim çekirdeği |
| İzmir | Aydın / RUM | 560.000 | Liman ve çok dilli ticaret çekirdeği |
| Selanik | Macedonia / RUM | 330.000 | Rum, Türk, Sefarad ve Balkan toplulukları |
| Atina | Attica / RUM | 280.000 | Kent ile çevre kırsal birlikte state'i oluşturur |
| Halep | Aleppo / RUM | 500.000 | Müslüman, Hristiyan ve Yahudi kent ağları |
| Bağdat | Baghdad / RUM | 580.000 | Akademi, idare ve nehir ticareti; hinterland ayrı kalır |
| Ankara | Ankara / RUM | 360.000 | Sünni/Şii Türk ve diğer yerel topluluklar |
| Van | Erzurum / RUM | 90.000 | Rûm payı yalnız Van çevresidir |

`STATE_ADANA`daki Rûm payı Adana kentini, `STATE_BASRA`daki Rûm payı Basra kentini, `STATE_TRABZON`daki Rûm payı Trabzon kentini içermez. Bu kentleri yanlış devlete yazmamak için profilleri burada oluşturulmadı.

## Yeniden üretim ve denetim

Mod kökünde:

```sh
python3 scenarios/atlas/demography_phase01_rum/prepare.py
python3 scripts/tools.py atlas scenario validate build/demography/rum-candidate.yml
python3 scripts/tools.py atlas scenario report build/demography/rum-candidate.yml --out build/demography/rum-candidate-report.json
python3 scripts/tools.py atlas scenario build build/demography/rum-candidate.yml --out build/scenarios/rum-demography-candidate
python3 scenarios/atlas/demography_phase01_rum/verify.py
python3 scripts/tools.py atlas build
python3 scripts/tools.py atlas check
```

`prepare.py` etkin kaynaktaki mevcut Rûm nüfusu farklıysa üzerine yazmaz. `verify.py`, 25 ortak kültür–din toplamını üretilmiş POP dosyasında, Rûm dışındaki POP bloklarının eşitliğini, şehir tahminlerinin state sınırlarını ve siyasetin değişmediğini denetler. [Dondurulmuş başlangıç nüfusu](legacy-population-snapshot.json) küçük tarihî toplulukların yanlışlıkla silinmesini önler. Oyun içi başlangıç ve zaman ilerletme testi bu demografi revizyonu için henüz yapılmadı.
