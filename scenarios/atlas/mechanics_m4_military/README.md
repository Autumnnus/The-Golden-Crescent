# M4 — Ordular, donanmalar ve komutanlar

**26 Eylül 2026 · etkin.** [Öneri](../../../docs/scenario/ORDU_KURULUM_ONERISI.md) üzerine kullanıcı kararları:
- ölçek vanilla ile küçük seçenek arasında orta (yaklaşık 2.700 tabur);
- bütün dünya tek pakette;
- komutanlar dahil;
- en büyük donanma koloni imparatorluğu Endülüs'te.

Kurallar [targets.yml](targets.yml) dosyasında (elle yazılır); [plan.py](plan.py) bunları ülke ülke [plan.yml](plan.yml) dosyasına çevirir (üretilir).

## Sonuç

**Toplam:**

| | Önce | Sonra |
|---|---:|---:|
| Tabur | 964 | 2.807 |
| Gemi | 98 | 648 |
| Ordulu ülke | — | 288 örgütlü ülke |
| Formasyon | — | 457 |
| Komutan | — | 268 general, 133 amiral |

Merkezsiz topluluklarda ordu yoktur. Londra'nın denizaşırı taç bağımlılıkları M0 kararıyla ordusuz kalır. Ülkelerin nüfus, bina, kanun, teknoloji ve bağlılık içerikleri değişmedi.

**Başlıca güçler:**

| Güç | Tabur | Gemi | Not |
|---|---:|---:|---|
| Rûm | 160 | 54 | 1B.3 paketinin Balkan, Anadolu, Irak–Levant orduları ve iki filosu; Sicilya istasyonunda Batı Akdeniz filosu |
| Lehistan–Litvanya | 123 | 8 | Avrupa'nın en büyük kara ordusu, süvari ağırlıklı |
| Jiangnan / Kuzey Çin | 119 / 103 | 14 / 8 | Kalabalık, düzensiz |
| Gurkanî | 100 | — | |
| **Endülüs** | 88 | **60** | **En büyük donanma**: Atlantik ve Yukarı Endülüs filoları |
| Mısır | 77 | 26 | |
| İsfahan (+ Tebriz 22 ve diğer İran kuklaları) | 62 | 8 | |
| Londra | 46 | 50 | |
| Uygur | 45 | — | Gansu ve Hindukuş orduları |
| Tatar | 34 | 2 | Süvari ağırlıklı |

**B1 sonrası (26 Eylül):** [B1](../balance_b1_tech_laws/README.md) teknolojileri değiştirdiği için `plan.py` yeniden çalıştırıldı ve 116 ülkenin birlik türleri yeni teknolojiye göre seçildi. Örnekler: Mısır avcı piyadesi, Gurkanî hat piyadesi ve seyyar topçu, Londra toplu topçu. Sokoto 2 topçu taburu aldı. Toplam tabur, gemi ve komutan sayısı aynı kaldı.

**Üçüncü tur (26 Eylül):** `admiralty` teknolojisi olmayan ülkeye donanma verilmiyor, çünkü donanma yönetimi kurulamaz ve gemiler mürettebatsız kalır. Buenos Aires ile Panama'nın birer fırkateyni ve iki amiral kalktı: 646 gemi, 131 amiral. Donanma yönetimi binaları [B2/B3](../balance_b2_economy/README.md) tarafından mürettebata göre kurulur.

## Kurallar

- **Ordu büyüklüğü:** `m × nüfus_milyon^0,85`.
  - `m` M1b okuryazarlık bandından gelir: İsfahan 16, çekirdek İslam 15, orta İslam 12, Avrupa üst 12...
  - Bazı ülkelere ayrı katsayı verildi: Mısır 20, İsfahan 22, Endülüs 16, Lehistan 14, Çin devletleri 3,5–4,5.
  - Koloniler ×0,6, bağlılar ×0,85.
  - Sonuç dünya toplamına göre ölçeklenir. En küçük ordu 2 taburdur.
- **Birlik türleri** teknolojiye göre seçilir:
  - piyade: avcı → hat → düzensiz;
  - süvari: hüssar → mızraklı → dragon;
  - topçu: seyyar → top.
- **Bileşim:** süvari payı %12; bozkır, çöl, Sahel, Afgan ve Leh orduları için %30. Topçu payı İslam çekirdeğinde %15–16, başka yerlerde %8–12.
- **Yerleşim:** her 35 tabura bir formasyon (1–5). Formasyonlar, ülkenin en çok nüfus tuttuğu strateji bölgelerinin en kalabalık state'lerine konur.
- **Donanma:**
  - Hedefler `targets.yml` dosyasında; listede olmayan kıyı ülkelerine 1–4 gemilik varsayılan filo verilir.
  - Hat gemisi `drydocks` teknolojisi olan ve 6+ gemili donanmalarda payın %35'idir.
  - 24+ gemili donanmalar iki filoya bölünür.
- **Komutanlar** ([build.py](build.py) → `common/history/characters/ve_m4_commanders.txt`):
  - Her orduya bir general, her filoya bir amiral verilir. Rütbe formasyon büyüklüğüne göre 1–4 arasıdır.
  - Vanilla geçmişi zaten komutan veren ülkelerde (Mısır, Japonya...) bu sayı düşülür.
  - Ad, portre, özellik ve çıkar grubunu oyun ülkenin ana kültüründen kendisi seçer.
  - Komutan formasyonun karargâh bölgesinde oluşur; bu, vanilla'nın İngiliz amiralleri için kullandığı yöntemdir. Formasyona atamayı oyun ve AI yapar.
- **Formasyon adları:** `ve_m4_*` anahtarlarıyla `localization/<dil>/ve_m4_military_l_<dil>.yml` dosyasında ("Endülüs Yukarı Endülüs Donanması", "Leh-Litvanya Harkiv Ordusu"). Rûm formasyonları 1B.3 adlarını taşır.

## Doğrulama

[verify.py](verify.py):
- rapor askerî toplamları planla aynı;
- dünya formasyonları planla aynı;
- her formasyonun adı var;
- askerî olmayan içerik değişmedi;
- toplam hedefin %5 yakınında;
- en büyük donanma Endülüs'te;
- yeni uyarı yok.

[Siyasi denetim](../world_political/active_political_audit.py) M4 alanlarını planla karşılaştırarak geçti; araç testleri 123/123. `check`: yalnız bilinen 168 `localization/replace` tekrarı ([P4](../political_p4_corrections/README.md)) ve 1 uyarı. Oyunda sınanmadı.

## Açık konular

- **Tedarik (M4d):** büyük ordular silah, top ve mühimmat ister. Birçok ülkenin askerî sanayisi yok, bu yüzden oyunun ilk aylarında mal kıtlığı ve bütçe baskısı görülebilir. Silah sanayisi ve ordu kanunları sonraki pakettir.
- **Komutanların formasyonlara bağlanması:** başlangıçta oyuna bırakıldı. Oyunda generaller atanmamış görünürse `transfer_to_formation` ile bağlamanın yolu araştırılacak.
- **Merkezsiz topluluklar:** kolonileştirilebilir yerli toplulukların direniş gücü yok.

```sh
cp world/scenario.yml build/mechanics/m4-source.yml; cp build/world-political/active-political-report.json build/mechanics/m4-source-report.json
python3 scripts/tools.py atlas rules --kind strategic_regions --limit 200 --out build/m4-strategic-regions.json
python3 scenarios/atlas/mechanics_m4_military/plan.py
python3 scenarios/atlas/mechanics_m4_military/prepare.py
python3 scripts/tools.py atlas scenario validate build/mechanics/m4-candidate.yml
python3 scripts/tools.py atlas scenario build build/mechanics/m4-candidate.yml --out build/scenarios/m4-candidate
python3 scenarios/atlas/mechanics_m4_military/verify.py
# etkinleştirme sonrası: atlas build → atlas scenario report → vanilla_overrides.py → d3 build.py → m4 build.py → atlas check
```
