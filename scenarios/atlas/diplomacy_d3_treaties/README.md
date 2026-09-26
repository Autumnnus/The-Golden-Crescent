# D3 — Başlangıç antlaşmaları ve rekabetler

**25 Eylül 2026 · etkin.** Kanondaki ([diplomasi.md](../../../docs/scenario/diplomasi.md)) antlaşmalar Victoria 3'ün başlangıç antlaşma sistemine çevrildi.

- **Antlaşmalar:** [build.py](build.py), [plan.yml](plan.yml) planından `common/history/treaties/tgc_scenario_treaties.txt` dosyasını üretir. Atlas antlaşmaları yönetmez; bu dosya elle düzenlenmez. Toplam 23 antlaşma, 28 madde ([P3](../political_p3_borders/README.md) sonrası):
  - İran Birlik Tüzüğü 1815: İsfahan–Tebriz ittifakı.
  - Kalmar Deniz Ahdi: üç taç arasında savunma paktları.
  - Taçlar Ahdi: İngiltere–İskoçya.
  - Maratha konseyi: Pune–Gwalior/Indore/Nagpur.
  - Şam 1712: Rûm ve Mısır'ın Şam, Lübnan ve Kudüs'e garantisi.
  - Bağdat 1804: Rûm ve İsfahan'ın Basra ile Kürdistan'a garantisi.
  - Karpat Ahdi 1827: Macaristan–Erdel savunma paktı. P3 ile Tuna 1827 garantileri kalktı (Eflak Lehistan koruması oldu), Hansa paktları da kalktı (üç kent tek Hansa Kent Birliği oldu).
  - Mısır–Aceh ikmal, Umman–Johor konvoy ve Umman–Sulu geçiş sözleşmeleri.
  - Endülüs–Fas Atlantik ortaklığı.
- **Üretici denetimleri:** taraflar örgütlü ve topraklı mı; `international_relations` teknolojisi var mı; ittifak ve pakt tarafları bağımsız mı; garanti tarafları bağımsız mı.
- **Kapsam dışı kalanlar:** Mombasa bu teknolojiye sahip olmadığı için antlaşma kurulmadı. Makassar merkezsiz Sulawesi'de olduğu için kurulmadı.
- **Vanilla antlaşmaları:** 11 vanilla antlaşmanın 7'si `drop_vanilla` ile düşürüldü: Avusturya'nın Viyana Kongresi garantileri, Karayip'teki `GBR`'nin Johor limanı ve Güney Afrika garantileri. Kalan 4'ü korunur: Hollanda–Japonya ticareti, Siam–Kamboçya, Avusturya–Karadağ yardımı, Lahej–Zeydî.
- **Rekabetler:** Atlas `diplomacy.pacts` alanında karşılıklı 10 `rivalry`: Rûm–Mısır, Rûm–Tebriz, İsfahan–Umman, Lehistan–Tatar Hanlığı, Kuzey Çin–Jiangnan, Gurkanî–Maratha, Gurkanî–Bengal, Endülüs–İngiltere; P3 ile İsveç–Lehistan ve Uygur Hanlığı–Kuzey Çin. P3 hazırlayıcısı yeni rekabetleri dünyaya ekler.

**Sıra:** `atlas build` → `vanilla_overrides.py` → `atlas scenario report` → `diplomacy_d3_treaties/build.py`. Antlaşma dosyası Atlas çıktısı olmadığı için build tarafından silinmez, ama raporla uyumlu kalması için her etkinleştirmeden sonra yeniden üretilmelidir.

**Sınır:** `atlas check` antlaşma dosyasını denetlemez. Maddelerin `possible` ve `requirement_to_maintain` koşulları (ör. ilişki eşiği, rütbe) oyunda sağlanmazsa antlaşma açılışta bozulabilir. Oyun testinde antlaşmalar panelinden bakılmalı.
