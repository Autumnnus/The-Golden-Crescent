# Demografi 11 — beş Çin yönetimi ve Kaşgar

Bu dilim [yazılı Çin atlasındaki](../../../docs/scenario/dunya_atlasi.md) Kuzey Çin, Jiangnan, Yue, Shu ve Mançurya yönetimleriyle Kaşgar'ın **34 doğrudan state payını** etkin Atlas kaynağına işler. Sınır ve diplomasi değişmez. [Plan](plan.yml) ülke toplamlarını, her state'in okuryazarlık girdisini ve Yue'nin ana kültür düzeltmesini kaydeder; [dondurulmuş POP kaynağı](source-pops.json) kültür–din/meslek dağılımının önceki hâlidir.

| Ülke | Doğrudan nüfus | Ağırlıklı okuryazarlık girdisi | Ölçek yorumu |
|---|---:|---:|---|
| Jiangnan `JNG` | 150.000.000 | %36,02 | Altı state'lik aşağı Yangtze çekirdeği **84.423.560**; Jiangxi, Hunan ve Hubei ayrıca aynı ülkenin doğrudan payları |
| Kuzey Çin `NCH` | 102.000.000 | %23,94 | Başkent ile Gansu/Qinghai sınırı aynı eğitim seviyesine zorlanmaz |
| Yue `YUE` | 57.000.000 | %30,02 | Yue, Zhuang, Min, Hakka ve Han toplulukları birlikte yaşar |
| Shu `SHU` | 45.000.000 | %26,10 | Sichuan–Chongqing ile Yunnan–Guizhou ayrı state girdileri |
| Mançurya `MCH` | 14.300.000 | %21,22 | Han, Mançu, Koreli, Moğol ve Amur yerel halkları korunur |
| Kaşgar `KSG` | 850.000 | %30,00 | Yalnız Tianshan; Dzungaria veya Moğol otlakları dahil değil |

Jiangnan'ın eski **80–100 milyon** doğrudan ülke ve Kaşgar'ın **3,5–4,5 milyon** tek-state hedefleri mevcut siyasi haritayla uyuşmuyordu. [Ekonomi hedefi](../../../docs/scenario/ekonomi_ve_toplum.md) Jiangnan için **140–155 milyon doğrudan / 80–100 milyon aşağı Yangtze çekirdeği**, Kaşgar için **0,75–1,05 milyon** olarak düzeltildi. Adayda çekirdek bu aralığa girer. Kaşgar'ın kurulu oyunda 40 arable land'i ve 370.200 devralınmış nüfusu vardır; 850 bin, sulama/ticaret ilerlemesini yansıtan ölçülü fakat yine de kırılgan bir büyüme varsayımıdır. Bu bir motor taşıma kapasitesi simülasyonu değildir.

Kurulu oyunun ortak kültür–din çiftleri her state'te korunur; Konfüçyüsçü resmî tören bütün halkı tek dine dönüştürmez. `YUE` ülkesinin ana kültür listesine oyunda zaten tanımlı **`yue`** eklendi; önceki `han` ve `zhuang` silinmedi. Bu, Yue kültürlü milyonlarca kişinin kendi konfederasyonunda sırf ülke tanımı eksik diye yabancı sayılmasını önleyen dar bir ülke tanımı düzeltmesidir. Jiangnan çevresindeki Wu kimliği oyunda ayrı kültür olmadığı için şimdilik `han` karşılığıyla kalır; ayrı kültür eklemek homeland ve kabul mekaniklerini incelemeyi gerektirir.

[35 hub şehir profili](city-profiles.yml) toplam **24.490.000** kişiyi ilgili state POP'larının alt kümesi olarak tasarlar; bunlar ilave oyun nüfusu, meslek veya bina değildir. Kaşgar–Aksu–Hotan profilleri birlikte 170.000 kişidir ve tek Tianshan toplamının içindedir. Şehirlerin kültür–din alt toplamları ve gerçek hub province sahipleri aday POP'larına karşı denetlendi. [Atlas önizlemesi](../../../build/maps/china-kashgar-demography.html) siyasi sınırda değişiklik göstermedi.

`prepare.py` adayı üretir; `verify.py` 34 payı, 35 şehri, diğer dünya POP'larının korunmasını, alt Yangtze hedefini, diplomasi ve Yue kültür eklemesini denetler. Aday validate/build ile etkin build/check ve siyasi denetim geçti: **0 hata, önceki 25 uyarı**. Dünya nüfusu **1.089.631.812** oldu. Atlas raporunda bu altı ülkenin başlangıç bina seviyesi **0**; nüfus ve okuryazarlık girdisi tek başına ticari/sanayi oynanışı yaratmaz. Çin'in kurum, binalar, askerî/teknoloji profilleri ve Kaşgar kervan ekonomisi ayrı aşama gerektirir. Bu revizyon oyun motorunda henüz açılıp test edilmedi.
