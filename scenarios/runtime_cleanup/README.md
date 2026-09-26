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
| `common/history/characters/{org,pni,pra,prg,seq,uru}*.txt` | [D1](../atlas/diplomacy_d1_natives/README.md) ile merkezsiz yerli topluluk olan altı vanilla etiketin kreol hükümdar/general dosyaları boşaltıldı | 6 dosya |
| `common/history/treaties/00_historical_treaties.txt` (ek) | [D3](../atlas/diplomacy_d3_treaties/README.md) `drop_vanilla` listesindeki 7 anlamsız vanilla antlaşma da çıkarıldı | 11 → 4 |
| `common/history/power_blocs/00_power_blocs.txt` | Kurucusu topraksız veya bağlı olan bloklar ile topraksız üyeler çıkarıldı. Korumasız `member = c:TAG` satırı topraksız ülkede açılışta **çöküyordu** (`CCountry::JoinPowerBloc`; P3 sonrası Parma, 25 Eylül 2026 oyun testi). Kalan: Avusturya'nın Metternich bloku (Modena, Toskana, Napoli). | 5 blok → 1 |
| `localization/replace/<dil>/tgc_country_name_overrides_l_<dil>.yml` | Atlas'ın ürettiği ülke adı ve sıfatlarından vanilla'da da tanımlı olanlar (KUR, KZH, SIC, MUG...) buraya kopyalanır; aksi halde vanilla adı kazanıyordu ([P4](../atlas/political_p4_corrections/README.md)). `atlas check` bunları yinelenmiş anahtar sayıyor (araç sınırı). | 84 anahtar |
| `gfx/interface/icons/{lens_toolbar_icons,diplomatic_action_icons}/ve_*.dds` | Özel bağlılık türü (`ve_*`) varsa her birine taban türünün vanilla ikonu kopyalanır; türü kalmayan eski kopyalar silinir. [D5](../atlas/diplomacy_d5_vanilla_subjects/README.md) sonrası özel tür olmadığı için boş | 0 |
| `common/scripted_effects/00_political_setup.txt` | Vanilla kopyası. `effect_starting_politics_traditional`, ülkede okul kanunu varsa serfliği açmaz. Atlas açık kanunları devralınan efektlerden önce yazdığı için [M1b](../atlas/mechanics_m1b_literacy/README.md) İslam ülkelerinin tenant farmers ve okul kanunları başka türlü ezilirdi | 84 ülke |

**Kalan küçük kalıntılar:** 4'er satır hata veren ~15 vanilla tarihî günlük (Amerikan İç Savaşı, Alman birliği, Afyon Savaşları, Hint göçü...), vanilla AI stratejisindeki 8 komşuluk denetimi ve bir dinamik state adı. Bunlar yalnız açılışta bir kez hata veriyor. Her birini kopyalamak gelecekteki oyun güncellemelerinde kırılganlık yaratacağı için Flavor/ileri temizlik turuna bırakıldı.

Override'lar vanilla dosya düzenine bağlıdır. Oyun güncellemesinden sonra betik yeniden çalıştırılmalı; Peru–Bolivya düzeni değişirse betik bilerek hata verir.
