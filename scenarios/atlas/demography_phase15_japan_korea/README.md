# Demografi 15 — Japonya, Kore, Ryukyu ve Ezo–Sahalin

Bu dilim [yazılı dünya atlasının](../../../docs/scenario/dunya_atlasi.md) Tokugawa/Joseon iç sürekliliğini korur. Yedi ülkenin **22 doğrudan state payı** etkin Atlas kaynağına işlendi; sınır, bağlılık, ticaret ilişkisi, kanun ve bina değiştirilmedi. Japonya'nın Ryukyu ve Hokkaido payları Ryukyu/Ezo nüfusundan ayrı sayılır. Sahalin'deki `ALK` payı (793 kişi) ile Alaska'nın diğer payları önceki halleriyle korunur.

| Ülke | Önce | Etkin doğrudan nüfus | Ağırlıklı okuryazarlık girdisi |
|---|---:|---:|---:|
| Japonya `JAP` | 32.545.935 | 32.600.000 | %32,68 |
| Kore `KOR` | 16.202.232 | 16.250.000 | %21,36 |
| Ryukyu `RYU` | 193.495 | 195.000 | %23,00 |
| Ezochi `EZO` | 31.871 | 34.000 | %8,96 |
| Ainu Mosir `AIN` | 7.281 | 7.281 | %6,00 |
| Evenki `SKH` | 5.193 | 5.193 | %5,00 |
| Ulta `ULT` | 4.242 | 4.242 | %5,00 |

Bölgenin doğrudan toplamı **48.990.249 → 49.095.716** kişidir; dünya toplamı **1.091.357.323** olur. Hedefler [planda](plan.yml), uygulama öncesi ortak POP grupları [dondurulmuş kaynakta](source-pops.json) bulunur. Nüfus paylaştırması önceki state ağırlığını ve mesleği açıkça belirtilmiş POP sayılarını korur. Japonya'nın mevcut `japanese/mahayana` grubu değiştirilmedi: bu tek oyun dini, Budist ve kami uygulamalarının ayrı ayrı nüfusa eklenmesi anlamına gelmez. Kore'nin Konfüçyüsçü/Budist grupları, Ryukyu'daki yerel ve küçük Han/Japon toplulukları, Hokkaido/Sahalin'deki Ainu ve Sibiryalı gruplar da korunur. Yeni Şinto POP payı yaratılmadı; bunun kültür, din ve ilerideki karakter olaylarındaki temsilinin ayrıca motor içinde değerlendirilmesi gerekir.

[20 hub profili](city-profiles.yml) kurulmuş Türkçe yerleşim adlarını ve ilgili hub province'inin siyasi sahibini kullanır. Edo, Osaka, Kyoto, Hanseong, Shuri, Hakodate ve Sahalin'deki Ai/Okhe/Sistukari gibi alt kümeler state nüfusunun **içindedir**; oyun bunlar için ayrı şehir POP'u oluşturmaz. Ezo'nun Sahalin parçası ve `ALK` payının kendi sahibi olduğu bir hub yoktur, bu yüzden onlara yanlış konumlu şehir profili yazılmadı. Kurulu oyunda `Naha` adlı liman hub province'i `JAP` payındadır, fakat yazılı atlas Naha'yı Ryukyu merkezi sayar. Sınır kararını bu demografi diliminde değiştirmeden, yanlış bir Japon Naha şehir profili eklemeyip bunu siyasi/yer adı denetiminde çözülmesi gereken açık uyuşmazlık olarak tutuyoruz. Yerleşim profili zenginlik, iş, bina veya eğitim sonucunu simüle etmez.

Yeniden üretim ve denetim:

```sh
python3 scenarios/atlas/demography_phase15_japan_korea/prepare.py --source build/demography/japan-korea-source.yml
python3 scripts/tools.py atlas scenario validate build/demography/japan-korea-candidate.yml
python3 scripts/tools.py atlas scenario build build/demography/japan-korea-candidate.yml --out build/scenarios/japan-korea-candidate
python3 scenarios/atlas/demography_phase15_japan_korea/verify.py
python3 scripts/tools.py atlas build
python3 scripts/tools.py atlas check
```

`snapshot.py` yalnız uygulama **öncesinde** bir kez çalıştırılır; mevcut [source-pops.json](source-pops.json) dosyasını silip yeniden dondurmaz. `verify.py` hedef dışı POP bloklarını, state/ülke ve diplomasi alanlarını, hedef grupları/meslekleri, toplamları ve hub sahipliğini karşılaştırır. [Önizleme](../../../build/maps/japan-korea-demography.html) siyasi renkte değişiklik göstermez (0 sınır değişikliği); sayısal değişim raporda ve bu plandadır. Son denetimde 675 state, 556 kara sahibi ülke, **0 hata ve önceki 25 uyarı** vardı. Oyun motorunda bu yeni nüfus ve okuryazarlık dilimi ayrıca çalıştırılmadı; ilk gün gerçek okuryazarlığı oyun hazırlığı yeniden hesaplayabilir.
