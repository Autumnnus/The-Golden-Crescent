# M1b — İslam önceliğiyle okuryazarlık

**25 Eylül 2026 · etkin (ikinci karar).** İlk M1b (24 Eylül) İslam çekirdeğine %60–70 girdi ve seviye 5 okul verdi. Üçüncü oyun testinde Rûm ve İsfahan açılışta %70–80 göründü. Kullanıcının yeni kararı: Ortadoğu'nun gelişmiş devletleri önde olmalı ama aralarında uçurum olmamalı. İsfahan en yüksek (%45–50), diğer gelişmiş Müslüman devletler %30–35, Avrupa ortalaması ve az gelişmiş Müslüman devletler %15–20.

**25 Eylül ince ayarı:** Kullanıcı sonucu beğendi ve üç bölgede küçük artış istedi. Senaryoda İran bilimin ve rönesansın merkezi olduğu için çevresi yükseltildi: Horasan ve Mazenderan %33, Kirman %30, Huzistan ve Herat %29, Azerbaycan %28, Luristan %26, Kabil %21, Kandahar/Mekran/Kalat %19. Rûm ve Mısır çevresi de yükseltildi: Adana ve Trabzon %31, Suriye %31, Lübnan %32, Filistin ve Hicaz %30, Erzurum %27, Trablus %25, Kürt beylikleri ve Bulgaristan %23, Bosna ve Sennar %21, Arnavutluk %19. Endülüs'ün karşı kıyısı da biraz arttı: Fas %29, Maskara %28, Konstantin %26. Bu değerler çekirdeği (%32–36) ve İsfahan'ı (%48) geçmez.

Bu turdan itibaren `target`, **oyunun açılış ekranında beklenen** okuryazarlıktır. Oyun kurulumda okuryazarlığı okul kanunu ve seviyesine göre girdinin birkaç puan üstüne çıkarır. Bu yüzden girdi `target − okul katkısı` olarak hesaplanır ([prepare.py](prepare.py) `boost`). Kalibrasyon: İsveç dinî okul 3 → +4,3 puan; Rûm kamu okulu 3 → +7; kamu okulu 5 → +8–11. Model: kamu okulu 0,01 + 0,02 × seviye, dinî/özel okul 0,015 × seviye, Japonya terakoya +0,05.

| Bant | Ülkeler | Açılış hedefi | Girdi | M1b öncesi girdi |
|---|---|---:|---:|---:|
| `islam_lead` | İsfahan (kamu okulu 3) | **%48** | %41 | %52 |
| `islam_core` | Rûm %35, Tebriz %36, Endülüs %34, Basra %34, Mısır %32 (kamu okulu 2) | **%34** | %29 | %43 |
| `islam_mid` | İran üyeleri, Levant, Hicaz, Anadolu beylikleri, Mağrip, Türkistan hanlıkları, Bengal, Gurkanî, Gucerat (%22–33, dinî okul 2) | **%25,3** | %22,3 | %25 |
| `islam` | Diğer İslam devletleri %15–23; merkezsiz çöl/bozkır toplulukları %13 (dinî okul 1) | **%18,9** | %17,5 | %18 |
| `europe_top` | İsveç, Danimarka, Norveç, İskoçya, Yeni İngiltere yerleşimleri, Lehistan, Kraków | **%24** | %22 | %40 |
| `europe` | Batı ve orta Avrupa, Avrupa kökenli Amerika yerleşimleri (%15–20) | **%17,5** | %15,6 | %31 |
| `europe_south` | Güney ve doğu Avrupa, Moskova ve Rus prenslikleri (%8–14) | **%11** | %10,6 | %18 |
| `east_asia` | Jiangnan, Japonya %18; Kore %16; diğer Çin %10–14 | **%15** | %14 | %30 |
| `rest` | Hindu/Budist devletler, Afrika, Amerika, Sibirya, Okyanusya yerel ülkeleri (%2–10) | **%8,6** | %8,6 | %16 |

Resmî dini Sünni, Şii veya İbadi olan ülkeler İslam ülkesi sayılır. Resmî dini boş olan vanilla ülkelerinde nüfus çoğunluğunun dinine bakılır. Ülke hedefleri [targets.yml](targets.yml) dosyasındadır ([targets.py](targets.py) üretir). `previous` M1b öncesindeki dondurulmuş demografi okuryazarlığıdır; ölçekleme her zaman dondurulmuş `build/mechanics/m1b-source.yml` paylarından yapılır, bu yüzden yeniden üretimde değer kaymaz. Her ülkenin okul kanunu, seviyesi ve girdisi `build/mechanics/m1b-audit.json` dosyasındadır.

## Uygulanan

1. **Başlangıç okuryazarlığı:** 1.046 state payının `literacy` girdisi, ülkesinin `girdi / önceki` oranıyla ölçeklendi. Ülke içi farklar (kent–kır, bölge) korundu. Atlas bu değeri ülke efektlerinden sonra state bazlı `set_pop_literacy` olarak yazar; vanilla `effect_starting_pop_literacy_*` bu yüzden bu değeri ezmez.
2. **M1 ülkeleri (159):** [classify.py](../mechanics_m1_institutions/classify.py) `--targets targets.yml` ile yeniden üretildi. Teknoloji kademeleri dondurulmuş kaynaktan hesaplandığı için değişmedi. Okul seviyeleri: İsfahan kamu okulu 3; Rûm, Tebriz, Endülüs ve Basra kamu okulu 2; orta İslam dinî okul 2; diğer İslam dinî okul 1. Eksikse `rationalism`/`empiricism` eklenir. İslam dışında eski kural yeni hedefe uygulanır (çoğu Avrupa ülkesi dinî okul 1).
3. **Vanilla history'li İslam ülkeleri (84):** [plan.py](plan.py) → [plan.yml](plan.yml). Vanilla kanunların üstüne dinî okul, okul kurumu 1–2 ve `law_tenant_farmers` eklendi. Mısır kamu okulu 2 ve `empiricism` aldı. Toprak kanunu serflik olan ya da vanilla efektine bırakılmış ülkelerde tenant farmers yazıldı, çünkü iki okul kanunu da serfliği yasaklar.
4. **Serflik koruması:** Atlas açık kanunları devralınan efektlerden önce yazar; vanilla `effect_starting_politics_traditional` ise serfliği yeniden açardı. [Vanilla override](../../runtime_cleanup/README.md) bu efektte serfliği yalnız ülkede okul kanunu varsa atlar.
5. **Üretim yöntemi düzeltmesi:** Yogyakarta'nın vanilla kahve plantasyonu sahip olmadığı bir teknolojiyi istiyordu; aynı gruptaki kullanılabilir yönteme çevrildi (24 Eylül turu, etkin kaynakta açık kayıt).

Vanilla history'li İslam dışı ülkeler (İsveç, Hollanda, Japonya...) vanilla okul kanun ve seviyelerini korur. Girdileri bu okulların katkısı düşülerek hesaplandı.

## Yeniden üretme

```sh
cp world/scenario.yml build/mechanics/m1b-source.yml   # yalnız ilk kurulumda (24 Eyl); M1b öncesi taban, ölçekleme buradan
cp world/scenario.yml build/mechanics/m1b2-source.yml  # uygulanacak güncel dünya (25 Eyl: M3 sonrası)
cp build/world-political/active-political-report.json build/mechanics/m1b2-source-report.json
python3 scenarios/atlas/mechanics_m1b_literacy/targets.py
python3 scenarios/atlas/mechanics_m1_institutions/classify.py --source build/mechanics/m1b-source.yml --targets scenarios/atlas/mechanics_m1b_literacy/targets.yml
python3 scenarios/atlas/mechanics_m1b_literacy/plan.py
python3 scenarios/atlas/mechanics_m1b_literacy/prepare.py
python3 scripts/tools.py atlas scenario validate build/mechanics/m1b-candidate.yml
python3 scripts/tools.py atlas scenario build build/mechanics/m1b-candidate.yml --out build/scenarios/m1b-candidate
python3 scenarios/atlas/mechanics_m1b_literacy/verify.py
```

`verify.py` şunları denetler: yalnız okuryazarlık ve planlanan kurum alanları değişti; her ülkenin girdisi hesaplanan değere ±0,006 içinde oturdu; nüfus ve bina seviyeleri korundu; M1 kanunları plana eşit; M1b kanun ve teknolojileri raporda var; hedef dışı ülkelerin kanunları değişmedi. 25 Eylül etkinleştirmesinden sonra `atlas check` 0 hata, 15 uyarı verdi ve yeni uyarı çıkmadı. Siyasi denetim ve araç testleri (123/123) geçti.

## Sınırlar

- Okul katkısı modeli üç gözleme dayanır. Açılış değerleri hedeften birkaç puan sapabilir; oyunda ölçülüp `boost` yeniden kalibre edilmeli. Uzun vadede okuryazarlık eğitim erişimine göre büyür veya düşer.
- Yüksek okuryazarlık beklenen hayat standardını da yükseltir. Bu yüzden İslam dünyasının ekonomisi [M3](../mechanics_m3_islamic_economy/README.md) ile birlikte yoğunlaştırıldı.
- Merkezsiz İslam toplulukları (Tuareg, Bidan...) kurum alamaz. Okuryazarlıkları yalnız başlangıç girdisidir (%13) ve zamanla düşebilir.
