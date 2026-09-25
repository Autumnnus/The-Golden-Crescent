# M1 — Kurumsal iskelet ve eğitim

[Mekanik aşama planının](../../../docs/scenario/MEKANIK_ASAMA_PLANI.md) ilk paketi. Kullanıcı kararları (24 Eylül 2026): sıra **M1 → M2 → M0**, teknoloji kademeleri **kanondaki sınıflara** göre.

## Neden

İlk oyun testi, başlangıç history'si olmayan **159 ülkenin (714 M kişi, dünyanın %66'sı)** teknolojisiz, kanunsuz ve kurumsuz başladığını gösterdi. Rûm, Jiangnan, Lehistan, Endülüs, İngiltere, Paris ve İsfahan da bunların arasındaydı. Kurulu oyun başlangıç okuryazarlığını eğitim erişiminden hesaplar (eğitim kanunu, okul kurumu seviyesi, teknoloji). Bu ülkelerde demografi planındaki okuryazarlık yalnız etkisiz bir girdi olarak kalıyordu.

## Ne yapıldı

[classify.py](classify.py), [overrides.yml](overrides.yml)'deki isimli kanon kararlarını ve sınıf kurallarını birleştirerek [plan.yml](plan.yml)'i üretir; [prepare.py](prepare.py) bunu `world/scenario.yml`'e uygular.

- **Teknoloji kademesi** (1 en ileri): kademe 1'de 5 ülke (Rûm, İsfahan, Tebriz, Endülüs, Jiangnan), kademe 2'de 10, kademe 3'te 56, kademe 4'te 10, kademe 5'te 29, kademe 6'da 48, kademe 7'de 1 ülke var. Kademe başına teknoloji listesi ([tier-techs.json](tier-techs.json)) Atlas raporuyla ölçüldü: 52, 44, 31, 20, 10, 3 ve 0 teknoloji. Cumhuriyetlere (Venedik, Milano, Novgorod, Ren/Brabant kentleri, Jiangnan, Basra, Pennsylvania, Gujarat) cumhuriyet kanunu için gereken `democracy` teknolojisi eklendi.
- **Tam kanun seti:** 24 kanun grubunun tamamı yazıldı (kast ve Edo grupları ilgili ülkelere özgüdür). Seçimler H1–H10 profillerinden türetildi. Her kanun kademe teknolojisine ve yasaklayıcı kanunlara göre denetlendi ([law-rules.json](law-rules.json)); tek bir yedek seçim yapıldı (Lehistan'da serflik nedeniyle tüketim vergisi). Demografide yazılan kölelik kanunları korundu, köle POP'u olmayan ülkelere `law_slavery_banned` yazıldı.
- **Önemli çakışmalar:** Dinî ve kamu okulları serflikle, kamu ve özel okullar devlet diniyle birlikte seçilemez. Bu yüzden Lehistan'a serflik + özel okullar + vicdan özgürlüğü verildi. Moskova serflik, devlet dini ve okulsuz düzende kaldı. H9 yerel meclisler ortak toprak hakkı nedeniyle `law_peasant_proprietorship` aldı.
- **Kurumlar:** Okul seviyesi demografi planındaki ağırlıklı okuryazarlıktan hesaplandı. Kalibrasyon noktası İsveç: vanilla'da dinî okullar ve seviye 3 ile oyunda %51 açılıyor. Kural `seviye = yuvarla((hedef − 0,05) / 0,14)` (0–5). Hedefi %12'nin altındaki ülkeler okulsuz. Vakıf sağlığı alan ülkelere sağlık kurumu 1, yerel polis alanlara polis 1 verildi.

| Ülke | Kademe | Eğitim kanunu | Okul seviyesi | Demografi hedefi |
|---|---:|---|---:|---:|
| `RUM` | 1 | public_schools | 3 | %40 |
| `ISF` | 1 | public_schools | 3 | %52 |
| `VAN` | 1 | public_schools | 3 | %50 |
| `JNG` | 1 | private_schools | 2 | %36 |
| `VPL` | 2 | private_schools | 2 | %36 |
| `VEL` | 2 | religious_schools | 2 | %36 |
| `FPA` | 3 | religious_schools | 2 | %31 |
| `VMS` | 4 | no_schools | 0 | %8 |
| `VTA` | 4 | religious_schools | 1 | %13 |
| `BGL` | 2 | religious_schools | 1 | %25 |
| `MAR` | 3 | religious_schools | 1 | %20 |
| `VNI` | 3 | religious_schools | 3 | %51 |
| `VNE` | 2 | religious_schools | 2 | %28 |
| `VCE` | 5 | religious_schools | 1 | %14 |
| `VHD` | 6 | no_schools | 0 | %8 |

## Doğrulama ve sınırlar

Aday `scenario validate/build` ilk denemede geçti. [verify.py](verify.py) yalnız 159 ülkenin teknoloji/kanun/kurum alanlarının değiştiğini, raporda kademe teknolojilerinin ve kanunların planla eşleştiğini, nüfus, bina, sınır ve diplomasinin aynı kaldığını denetler. Etkin `build/check` **0 hata, 25 uyarı** verdi. [Siyasi denetim](../world_political/active_political_audit.py) M1 alanlarını planla karşılaştırır ve geçer. Öz testler 38/38.

**Motor testi gerekli:**
- Okuryazarlığın gerçekte nasıl açıldığı henüz görülmedi; eşleme bir tahmindir ve kalibre edilecek.
- `law_slavery_banned` ile diğer kanunların vanilla `on_activate` blokları başlangıçta beklenmedik değişkenler yaratabilir.
- Yönetimdeki çıkar grupları yazılmadı; oyun hükümeti kendisi kurar.
- Bina ve ordu bu paketin kapsamında değildir; hayat standardı M2 ile düzelecek.
