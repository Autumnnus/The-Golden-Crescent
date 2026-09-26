# P5 — Endülüs'ün kuzey sınırı

**26 Eylül 2026 · etkin.** Kullanıcı isteği: "Endülüs'e Kastilya ve Aragon'un güneylerinden toprak verelim, oldukça küçük kalmış." [plan.yml](plan.yml), P3 biçimindedir ve [P3 prepare.py](../political_p3_borders/prepare.py) ile `--plan-dir scenarios/atlas/political_p5_andalusia --name p5` olarak uygulanır.

| Değişiklik | Kaynak | Nüfus |
|---|---|---:|
| **La Mancha** (Ciudad Real, Albacete, güney Cuenca): Yeni Kastilya'nın kurulu haritada y ≥ 1150 olan 7 ili → Endülüs | Kastilya | 470 bin |
| **Valensiya** kıyısı, Aragon'un güneyi: bütün state → Endülüs | Aragon | 0,97 M |

- **Yeni sınır:** Madrid (şehir merkezi `xDCD24C`) ve Toledo Kastilya'da kaldı. Kastilya ile Aragon kaybettikleri yerlere hak iddiası taşır.
- **Nüfus:** Endülüs 17,5 → 18,9 M; Kastilya 3,5 → 3,0 M; Aragon 3,0 → 2,0 M. Taşınan halkın kültürü ve dini korundu (İspanyol Katolik); Endülüs anayurdunda tanınan cemaatlerin eşit statüsü geçerlidir.
- **Binalar:** P3 kuralıyla yeniden kuruldu (8 düzeltme).
- **Ordular:** M4 planı yeniden üretildi. Endülüs 88 → 94 tabur, Kastilya 13 → 11, Aragon 11 → 8.

[P3 verify](../political_p3_borders/verify.py) geçti. [Siyasi denetim](../world_political/active_political_audit.py) P5'i paket listesine aldı; M1b soy kaydı (`lineage.yml`) P5 katmanını okur. Oyunda sınanmadı.

```sh
cp world/scenario.yml build/political/p5-source.yml; cp build/world-political/active-political-report.json build/political/p5-source-report.json
python3 scripts/tools.py atlas scenario build build/political/p5-source.yml --out build/scenarios/p5-source
python3 scenarios/atlas/political_p3_borders/prepare.py --plan-dir scenarios/atlas/political_p5_andalusia --name p5
python3 scripts/tools.py atlas scenario validate build/political/p5-candidate.yml
python3 scripts/tools.py atlas scenario build build/political/p5-candidate.yml --out build/scenarios/p5-candidate
python3 scenarios/atlas/political_p3_borders/verify.py --plan-dir scenarios/atlas/political_p5_andalusia --name p5
# sonra: B1 prepare --countries-only, M4 plan/prepare, B2 plan (bkz. balance_b2_economy/README.md)
```
