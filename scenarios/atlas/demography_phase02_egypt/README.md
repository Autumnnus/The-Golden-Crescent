# Demografi 2 — Mısır ve Dongola koridoru

**Etkin kaynak:** `world/scenario.yml`. Siyasi sınırlar değişmeden Mısır'ın yedi doğrudan state payına nüfus, ortak kültür–din ve okuryazarlık girdileri eklendi. Tasarım [plan.yml](plan.yml), eski oyun POP dağılımı [dondurulmuş kayıtta](legacy-population-snapshot.json) tutulur.

## 1836 tasarım sonucu

| Bölge | Nüfus | Okuryazarlık girdisi | Toplumsal odak |
|---|---:|---:|---|
| Aşağı Mısır | 5.900.000 | %43 | Kahire, İskenderiye, Delta sulaması ve limanlar |
| Orta Mısır | 3.200.000 | %36 | Tarım kasabaları, Kıpti yerleşimler, Süveyş kara aktarması |
| Yukarı Mısır | 1.650.000 | %28 | Nil tarımı, Kıpti ve güney nehir toplulukları |
| Dongola | 550.000 | %24 | Bedevi, Beja ve güney Nil toplulukları |
| Mısır Çölü | 95.000 | %19 | Vaha ve geçiş yolları |
| Matruh | 50.000 | %20 | Bedevi, Berberi ve Mısır toplulukları |
| Sina | 55.000 | %21 | Kervan ve kıyı yerleşimleri |

**Toplam 11.500.000** kişi; nüfus ağırlıklı okuryazarlık girdisi **%37,59**. Yazılı hedef olan 10–13 milyon ve %34–40 aralığına uyar. Ülke toplamında yaklaşık %84,1 Mısır Arap, %6,8 Sudanese, %3,5 Bedevi, %1,3 Beja kültürü; %84,1 Sünni, %13,7 Doğu Ortodoks, %1,1 Yahudi inancı bulunur. Bu oranlar bütün ülkenin toplamıdır; state'lere aynı karışım uygulanmaz. Kıpti topluluklar `misri/oriental_orthodox` ortak grubunda temsil edilir. Dongola'nın inancı ve kültürü tek tipe indirgenmez.

Vanilla'da Nil Nubyalıları için özgül bir kültür yoktur. `nuba` Kordofanî bir kültür olduğu için Nubyalı yerine kullanılması yanlış olur. Bu dilimde `sudanese` geniş güney Nil vekili olarak kullanıldı; **Nubyalıların ayrı kültürel kimliği henüz oyun POP'unda temsil edilmiyor**. Bu, ileride kurulu oyun sözdizimi ve isim havuzuyla güvenli bir `ve_` kültürü eklenerek giderilmeli. Yazılı lore Nubyalıları ayrı topluluk olarak korur.

Mevcut **189.833 köle POP'u** ve diğer sabit meslek POP'ları kültür, din, meslek ve kişi sayısıyla aynen kalır. Mısır'ın etkin `law_slave_trade` kanunu demografi aşamasında değiştirilmedi; özgürleşme ancak hukuk/emek tasarımında birlikte ele alınır. Bu, köleliği olumlayan bir tasarım hedefi değil, ayrı karar verilmesi gereken başlangıç mekanik bağıdır.

## Şehir profilleri

[Şehir profili](city-profiles.yml) Kahire 1,1 milyon, İskenderiye 600 bin, Beni Suef 200 bin, Asyut 250 bin, Uksur 150 bin ve Haiya 50 bin kişilik tahmin içerir. Toplam **2,35 milyon** kişi state paylarının içindedir; ayrıca oyun POP'u yaratmaz. Bu altı merkez ülke nüfusunun %20,43'ünü oluşturur; yazılı %18–24 kentleşme hedefi içinde diğer kasabalar için de alan bırakır. Yerleşim ve port hub adları kurulu oyunun `hub_names_l_turkish.yml` dosyasından doğrulandı. Birden fazla şehir aynı state'teyse ortak kültür–din sayılarının toplamı state grubunu aşmaz. Geri kalan nüfus diğer kentler, kasabalar ve kırsal bölgelerde kalır.

## Denetim ve sınır

Mod kökünden:

```sh
python3 scenarios/atlas/demography_phase02_egypt/prepare.py
python3 scripts/tools.py atlas scenario validate build/demography/egypt-candidate.yml
python3 scripts/tools.py atlas scenario report build/demography/egypt-candidate.yml --out build/demography/egypt-candidate-report.json
python3 scripts/tools.py atlas scenario build build/demography/egypt-candidate.yml --out build/scenarios/egypt-demography-candidate
python3 scenarios/atlas/demography_phase02_egypt/verify.py
python3 scripts/tools.py atlas build
python3 scripts/tools.py atlas check
```

Denetim 675 siyasi state'in, 556 ülkenin, Mısır dışı POP bloklarının ve mevcut Rûm nüfusunun değişmediğini kontrol eder. Atlas `build/check` sıfır hata verdi; 25 eski sınır/ordu uyarısı sürüyor. Bunlar statik sonuçlardır: oyun motorunda bu Mısır nüfusuyla yeni başlangıç veya zaman ilerletme henüz sınanmadı. Okuryazarlık motorun başlangıç etkileriyle yeniden hesaplanabilir. Şehir sayıları oyun motorunda ayrı yerleşim nüfusu olarak uygulanmaz.
