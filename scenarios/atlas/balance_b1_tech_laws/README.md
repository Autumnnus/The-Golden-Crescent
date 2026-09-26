# B1 — Teknoloji ve kanun dengesi

**26 Eylül 2026 · etkin.** [Denge önerisi](../../../docs/scenario/DENGE_KURULUM_ONERISI.md) üzerine kullanıcı kararları:
- Avrupa 3. kademe; Avrupa üstü (Lehistan, Kalmar taçları, İskoçya) bir adım önde; güney ve doğu Avrupa 4. kademe.
- Jiangnan 2, Yue 3, diğer Çin devletleri 4. kademe.
- İsfahan, Rûm ve Mısır başrol; en büyük üstünlük İsfahan'da.

Kurallar [targets.yml](targets.yml) dosyasında (elle yazılır); [plan.py](plan.py) bunları [plan.yml](plan.yml) dosyasına çevirir (üretilir).

## Sonuç

| Grup | Teknoloji paketi | Örnek (sayı) |
|---|---|---|
| İsfahan | Kademe 1 + anonim şirketler, psikiyatri, eczacılık, modern kanalizasyon, posta tasarrufu, realizm, kristal cam, kimyasal ağartma, damıtma, konserve, makineli atölye | **63** |
| Rûm | Kademe 1 + konserve, makineli atölye, yivli namlu, su borulu kazan, Bessemer, lojistik, mermi topu | 59 |
| Mısır | Kademe 1 + konserve, makineli atölye, damıtma, hidrolik vinç, mermi topu | 57 (önce 33) |
| İslam çekirdeği | Kademe 1 | Tebriz, Endülüs, Basra 52 |
| Orta İslam | Kademe 2 | Gurkanî 44 (önce 20), Bengal, Uygur, Fas 44 |
| Diğer İslam | Kademe 3 | Sokoto 31 (önce 10) |
| Avrupa üstü | Kademe 3 + torna, bankacılık, borsa, deneycilik, Napolyon savaşı | Lehistan, İsveç 36 (önce 44) |
| Londra | Kademe 3 + torna, atmosferik makine | 33 (önce 44) |
| Avrupa | Kademe 3 | Paris 31 |
| Güney ve doğu Avrupa | Kademe 4 + hat piyadesi (vanilla'nın Osmanlı örneği) | Macaristan, Moskova 22 |
| Doğu Asya | Jiangnan 2, Yue 3, Kuzey Çin, Shu ve Mançurya 4 + hat piyadesi | Jiangnan 44 (önce 52) |

**Değişim ölçeği:** 149 ülke değişti. Japonya, Kore ve kalan dünya aynı kaldı.

**Zorunlu düzeltmeler:**
- **Kanun (17):** Teknolojisi gidenlerde sansür yerine toplanma hakkı (6 ülke) ve kamu okulu yerine dinî okul (2 ülke). Tek ülkelik değişiklikler: gizli polis yerine iç işleri yok (Avusturya), hayır sağlığı yerine sağlık sistemi yok, milis yerine profesyonel ordu, tarımcılık yerine müdahalecilik. Avusturya'nın iç işleri ve bir ülkenin sağlık kurumu, dayanak kanunları gidince 0'a indi.
- **Mısır'ın H2 kanunları:** müdahalecilik, köle ticareti yerine mevcut köleliğin sürmesi, atanmış memurlar, özel polis, sansür, hayır sağlığı.
- **Binalar:** 7 bina kaldırıldı: 4. kademede akademi olmadığı için 6 üniversite, demiryolu teknolojisi gittiği için Bavyera'nın 1 demiryolu.
- **Üretim yöntemleri (26):** Teknolojisi gidenler, aynı gruptaki izinli en ileri yönteme indi. Örnekler: Londra'nın çelikten aleti dökme demire, mezbahalar kasap aletine, torna mobilyası el yapımına.
- **Ordu:** 116 ülkede birlik türleri M4 kuralıyla yeniden seçildi. Örneğin Mısır'ın hat piyadesi avcı piyadesine yükseldi; Gurkanî düzensiz piyadeden hat piyadesine, toptan seyyar topçuya geçti. Londra'nın seyyar topçusu toplu topçuya indi. Sokoto topçu teknolojisi kazandığı için M4 kuralı 2 topçu taburu ayırdı. Toplam tabur ve gemi sayısı değişmedi.

**Kolonicilik kanunları (26 Eylül, ikinci tur).** Kullanıcı, batılı kolonici devletlerde kolonicilik kanunu olmadığını gördü. [targets.yml](targets.yml) `law_overrides` ve `institution_overrides` ile:

| Ülke | Kanun | Kolonicilik kurumu | Gerekçe |
|---|---|---:|---|
| Endülüs | Sömürge sömürüsü | 2 | H4: kolonilerde tercihli tekel |
| Fas | Sömürge sömürüsü | 1 | Fas Brezilyası, Antiller, Timbuktu |
| Umman | Sömürge sömürüsü | 1 | Hint Okyanusu kıyısı |
| Londra | Sömürge iskânı | 1 | H5: yerleşimci kıyı kolonileri (Yeni İngiltere, Virginia) |
| Rûm | Sınır kolonizasyonu | 1 | Yeni Bursa; H1 büyük iskân programı finanse edemez |

Hollanda ve Danimarka sömürge sömürüsünü, Britanya tacı sömürge iskânını vanilla'dan taşıyor. Bu tur `prepare.py --countries-only` ile uygulandı: yalnız ülke alanları yazıldı, çünkü binalar artık B2'nin.

**Başlangıç serveti değiştirilmedi.** Atlas'ın servet alanı bütün POP'lara tabaka farkı olmadan aynı değeri yazar; oyun da kurulumda serveti ekonomiden yeniden hesaplar. Asıl kaldıraç B2 ekonomisidir.

## Doğrulama

[verify.py](verify.py) şunları denetler:
- teknoloji sayıları planla aynı ve sıra İsfahan > Rûm > Mısır > İslam çekirdeği > orta İslam > Avrupa üstü > Avrupa > güney/doğu Avrupa;
- plan dışında teknoloji ve kanun değişmedi;
- nüfus, bağlılık ve ordu büyüklüğü aynı;
- yalnız planlanan 8 bina seviyesi kalktı;
- plan ülkelerinde teknolojiye aykırı bina veya üretim yöntemi yok. Dünyada tek aykırılık, B1'den önce de olan Lourenço Marques limanı.

Etkinleştirme sonrası:
- `check`: yalnız bilinen 168 `localization/replace` tekrarı ve 1 uyarı;
- [siyasi denetim](../world_political/active_political_audit.py) B1 alanlarını planla karşılaştırarak geçti;
- araç testleri 123/123. Oyunda sınanmadı.

**Motor sınırları:**
- Teknoloji, okul kurumu ile birlikte eğitim erişimini de etkiler. M1b okuryazarlığı Avrupa'da birkaç puan düşebilir, İslam dünyasında yükselebilir; bu oyun testinde ölçülecek.
- Güney ve doğu Avrupa ile Çin'de artık üniversite ve demir iskeletli inşaat yok.

```sh
cp world/scenario.yml build/balance/b1-source.yml; cp build/world-political/active-political-report.json build/balance/b1-source-report.json
python3 scenarios/atlas/balance_b1_tech_laws/plan.py
python3 scenarios/atlas/balance_b1_tech_laws/prepare.py
python3 scripts/tools.py atlas scenario validate build/balance/b1-candidate.yml
python3 scripts/tools.py atlas scenario build build/balance/b1-candidate.yml --out build/scenarios/b1-candidate
python3 scenarios/atlas/balance_b1_tech_laws/verify.py
# etkinleştirme: cp → atlas build → atlas scenario report → mechanics_m4_military/plan.py ve prepare.py (--source world/scenario.yml)
# → tekrar build/report → vanilla_overrides.py → d3 build.py → m4 build.py → atlas check → siyasi denetim
```
