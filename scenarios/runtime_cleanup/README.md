# Çalışma zamanı temizliği — vanilla override'ları

[vanilla_overrides.py](vanilla_overrides.py), Atlas'ın yönetmediği ve 1836 alternatif dünyasında var olmayan ülkelere başvurduğu için açılışta hata veren vanilla dosyalarını dar biçimde override eder. Kurulu oyun dosyaları salt okunur okunur; mod içinde aynı adlı dosya üretilir. Etkin `atlas build` sonrasında yeniden çalıştırılmalıdır.

| Override | İşlem | Girdi (vanilla → mod) |
|---|---|---:|
| `common/history/trade/00_historical_trade.txt` | Sahibi değişmiş state ihracatları çıkarıldı | 17 → 4 |
| `common/history/lobbies/00_lobbies.txt` | Var olmayan ülkelerin veya hedeflerin lobileri çıkarıldı | 45 → 15 |
| `common/history/treaties/00_historical_treaties.txt` | Var olmayan tarafların antlaşmaları çıkarıldı | 46 → 11 |
| `common/history/production_methods/00_urban_center.txt` | Var olmayan ülkelerin kent yöntemleri çıkarıldı | 9 → 3 |
| `common/history/military_deployments/00_military_deployments.txt` | 1836 cephe konuşlanmaları bu evrende yok; boş | → 0 |
| `common/journal_entries/02_peru_bolivia.txt` | Vanilla kopyası; iki tetikleyiciye `exists = c:BOL` | 396 hata |
| `common/cultures/ve_andalusi.txt` + `ve_andalusi_*` | UTF-8 BOM; motorun beklediği 6 kültür static modifier'ı ve 3 modifier tipi | 7 hata |
| `common/scripted_effects/00_political_setup.txt` | Vanilla kopyası. `effect_starting_politics_traditional`, ülkede okul kanunu varsa serfliği açmaz. Atlas açık kanunları devralınan efektlerden önce yazdığı için [M1b](../atlas/mechanics_m1b_literacy/README.md) İslam ülkelerinin tenant farmers ve okul kanunları başka türlü ezilirdi | 84 ülke |

**Kalan küçük kalıntılar:** 4'er satır hata veren ~15 vanilla tarihî günlük (Amerikan İç Savaşı, Alman birliği, Afyon Savaşları, Hint göçü...), vanilla AI stratejisindeki 8 komşuluk denetimi ve bir dinamik state adı. Bunlar yalnız açılışta bir kez hata veriyor. Her birini kopyalamak gelecekteki oyun güncellemelerinde kırılganlık yaratacağı için Flavor/ileri temizlik turuna bırakıldı.

Override'lar vanilla dosya düzenine bağlıdır. Oyun güncellemesinden sonra betik yeniden çalıştırılmalı; Peru–Bolivya düzeni değişirse betik bilerek hata verir.
