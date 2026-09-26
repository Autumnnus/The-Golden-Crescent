# B0 — Denge ölçüm aracı

**26 Eylül 2026 · yalnız ölçüm; oyun dosyası üretmez.** [Denge önerisinin](../../../docs/scenario/DENGE_KURULUM_ONERISI.md) temelidir.

[measure.py](measure.py) aynı statik modeli iki dünyaya uygular:
- vanilla 1836 başlangıcı: kurulu oyunun history dosyaları, salt okunur;
- etkin mod: `build/world-political/active-political-report.json` ve `common/history/military_formations/`.

Sonuçları `build/balance/b0-vanilla.json`, `b0-mod.json` ve `b0-summary.md` dosyalarına yazar.

```sh
python3 scenarios/atlas/balance_b0_model/measure.py   # etkin rapor, etkinleştirme zincirinde üretilmiş olmalı
```

## Model

| Bileşen | Kural | Vanilla kaynağı |
|---|---|---|
| Bina üretimi ve girdisi | PM `goods_input/output_*_add` × seviye × ölçek ekonomisi (seviye başına +%1, en çok 20 seviye; yalnız `economy_of_scale = yes` grupları) | `common/production_methods`, `common/building_groups`, `00_code_static_modifiers.txt` |
| Ordu ikmali | Tabur başına `upkeep_modifier` malları; tabur başına 1.000 asker istihdamı | `common/combat_unit_types` |
| POP tüketimi | Nüfusun %25'i çalışır. İşler önce bina ve ordu istihdamıyla dolar; kalanlar pazara yalnız %5 ihtiyaç koyan geçimlik köylüdür. İşçi hanesi 2,5 paket tüketir. Servet = ülkenin başlangıç serveti tabanı + tabaka farkı. Paketin £ değeri ihtiyacın mallarına ağırlık × pazar arzı oranında bölünür (`max_supply_share` sınırı). | `buy_packages`, `pop_needs`, `pop_types`, `00_starting_pop_wealth.txt` |
| Pazar | Ülke ve bütün bağlıları (ayrı pazar anlaşması yoksa) | `36_subjects_grant_own_market.txt` |
| Bürokrasi | 100 + hükümet idaresi çıktısı; gider = state başına 10 + 100 bin kişi başına 4 (azaltan kanunlarla ×0,75) + devlet binası seviyesi başına 1. Kurum giderleri dahil değil. | `00_defines.txt` |
| Altyapı | 3 + nüfus altyapısı (teknoloji oranı ve sınırı; kıyı eki) + state özellikleri + liman/demiryolu; kullanım = seviye × bina grubunun seviye başına kullanımı | `technology`, `state_traits`, `building_groups` |
| Katma değer | Çıktı − girdi, taban fiyatla. Geçimlik üretim ve hizmetler dahil değil; GDP'nin yaklaşık göstergesidir. | `common/goods` |

## Sınırlar

- Motor simülasyonu değildir. Fiyat, kâr, gerçek servet dengesi, istihdam doluluğu ve ticaret akışı hesaplanmaz.
- Tüketim paketi biriminin 10 bin kişi başına £ olduğu dosya yorumlarından çıkarılmıştır. Mutlak talep yerine **vanilla ile oran karşılaştırması** kullanılır. Vanilla'da temel tüketim mallarında arz/talep 0,6–0,8'dir: oyun 1836'yı hafif kıtlıkla başlatır.
- Aristokrat ve din adamı gibi geçimlik tarımdaki üst tabaka hesaba katılmaz; lüks mal talebi eksik tahmin edilir.
- Bürokrasi giderinde kurumlar yoktur; açık gerçekte daha büyüktür.
