# Atlas üretim fazları ve devam kaydı

**13 Eylül 2026.** Kullanıcı Atlas ile fazlar halinde uygulamayı başlattı. Yazılı tasarım önceki aşamanın kaynağıdır; bir fazın önizlemesi bütün dünyayı tamamlanmış veya oyuna etkinleşmiş saydırmaz.

| Faz | Sonuç / kabul koşulu | Durum |
|---|---|---|
| 1A — Rûm coğrafyası | İl sahipliği, altı bağlı devlet, bağımsız ara kuşak, aktarımda veri korunumu, incelenebilir harita | İlk önizleme üretildi; küçük sınır/hub kararları faz kaydında görünür |
| 1B — Aynı bölgenin başlangıç dünyası | Bölgesel demografi, sanayi/tedarik, hukuk, teknoloji, ordu ve port/başkent temsili; Osmanlı/Greek eski scope denetimi | **Devam ediyor**; 1B.1 Rûm nüfus/eğitim/hukuk girdileri doğrulandı. 1B.2 özgürleşme, üretim ve kurum bütçesi sırada |
| 2 — Mısır/İran ve bağlantıları | Nil–Levant–Körfez dengesi, yedi İran üyesi ve karşılıklı ekonomi/diplomasi | Bekliyor; gerekirse alt fazlara ayrılır |
| 3 — Avrupa ve kuzey | Lehistan, Moskova/Tatarlar, Kalmar/Britanya, Endülüs ve Avrupa devletleri | Bekliyor |
| 4 — Asya/Afrika/Amerika/Okyanusya | Her bölge ayrı coğrafya + başlangıç mekanikleri paketi; sömürge/yerel egemenlik birlikte | Bekliyor; tek oturumluk görev değildir |
| 5 — Dünya bütünleştirmesi | Bölge sınırları, toplamlar, vanilla ilişki/artık içerik denetimi; aktif build/check ve motor testi | Bekliyor |

**Önceki coğrafya:** [Faz 1A paketi](../../scenarios/atlas/phase01_rum/README.md). Kaynak `scenarios/atlas/phase01_rum/geography.json`; doğrulama özeti aynı klasörde. `world/` henüz boş. Bu harita dışında Rusya/Fransa/BIC'nin vanilla görünmesi bilinçli geçiş durumudur.

Her oturum önce kullanım limitini ve Git durumunu kontrol eder; küçük bir kabul koşulu seçer. Kapanışta kaynak dosyası, çalıştırılan kontroller, motor testi durumu ve sonraki somut iş kaydedilir. Yüksek kullanımda yeni bölge açılmaz; mevcut dosyalar doğrulanıp güvenli bir durma noktası bırakılır. Kullanım yüzdesi iş miktarından güvenilir biçimde tahmin edilemediği için ara kontrol gerekir; reset kredisi kendiliğinden kullanılmaz.

## Güncel devam noktası — 1B.1

[Rûm demografi ve kurum paketi](../../scenarios/atlas/phase01b_rum_demography/README.md): 27 milyon doğrudan nüfus, 25 bölge, %40,18 ağırlıklı eğitim girdisi, 24 kanun ve üç kurum. Ayrı rapor/build/Atlas önizlemesi üretildi; 452 diğer ülke değişmedi, yeni uyarı yok. Motor testi yapılmadı. **Bir sonraki çalışma 1B.2:** önce 1811 özgürleşme/ham köle statüsü tutarlılığı, ardından üretim zinciri ve kurum bütçesi. Nihai kültür/din, teknoloji, ordu ve bölgedeki diğer devletler henüz tamamlanmadı.
