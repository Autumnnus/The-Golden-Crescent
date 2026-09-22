# Atlas üretim fazları ve devam kaydı

> **Tarihsel kayıt:** Bu belge önceki Rûm mekanik denemelerini açıklar; güncel dünya siyasî kaynağı değildir. Dünya sınırları, ülkeler ve başlangıç diplomasisi için [SİYASİ İNŞA PLANI](SIYASI_INSA_PLANI.md), siyasi state karar defteri ve `scenarios/atlas/world_political/` kullanılır.

**19 Eylül 2026.** Önceki bölgesel mekanik fazları korunur; kullanıcı artık dünya sınırı, ülke ve bağlılık iskeletini önce bitirme kararı aldı. Yeni çalışma sırası [dünya siyasi inşa planında](SIYASI_INSA_PLANI.md) tanımlıdır. Yazılı tasarım önceki aşamanın kaynağıdır; bir fazın önizlemesi bütün dünyayı tamamlanmış veya oyuna etkinleşmiş saydırmaz.

| Faz | Sonuç / kabul koşulu | Durum |
|---|---|---|
| 1A — Rûm coğrafyası | İl sahipliği, altı bağlı devlet, bağımsız ara kuşak, aktarımda veri korunumu, incelenebilir harita | İlk önizleme üretildi; küçük sınır/hub kararları faz kaydında görünür |
| 1B — Aynı bölgenin başlangıç dünyası | Bölgesel demografi, sanayi/tedarik, hukuk, teknoloji, ordu ve port/başkent temsili; eski Osmanlı/Yunan/İyonya scope denetimi | Askıda; 1B.5 statik entegrasyon denetimi tamamlandı. Dünya siyasi iskeleti kilitlendikten sonra uyumluluk katmanı, Nizam sözleşmesi ve motor testi yeniden açılacak |
| S0 — Dünya siyasi iskeleti | Tüm kıtalarda devlet, doğrudan sahiplik, bağlılık ve sömürge statüsü; mekanik veri yok | **Devam ediyor**; Kart 0A (Rûm/İran çekirdeği), Kart 1A (altı Fransız devleti), Kart 2A (BIC tasfiyesi) ve Kart 3A (Çin ayrımı) Atlas önizlemesinde doğrulandı |
| 2 — Mısır/İran ve bağlantıları | Nil–Levant–Körfez dengesi, yedi İran üyesi ve karşılıklı ekonomi/diplomasi | Bekliyor; gerekirse alt fazlara ayrılır |
| 3 — Avrupa ve kuzey | Lehistan, Moskova/Tatarlar, Kalmar/Britanya, Endülüs ve Avrupa devletleri | Bekliyor |
| 4 — Asya/Afrika/Amerika/Okyanusya | Her bölge ayrı coğrafya + başlangıç mekanikleri paketi; sömürge/yerel egemenlik birlikte | Bekliyor; tek oturumluk görev değildir |
| 5 — Dünya bütünleştirmesi | Bölge sınırları, toplamlar, vanilla ilişki/artık içerik denetimi; aktif build/check ve motor testi | Bekliyor |

**Önceki coğrafya:** [Faz 1A paketi](../../scenarios/atlas/phase01_rum/README.md). Kaynak `scenarios/atlas/phase01_rum/geography.json`; doğrulama özeti aynı klasörde. `world/` henüz boş. Bu harita dışında Rusya/Fransa/BIC'nin vanilla görünmesi bilinçli geçiş durumudur.

Her oturum önce kullanım limitini ve Git durumunu kontrol eder; küçük bir kabul koşulu seçer. Kapanışta kaynak dosyası, çalıştırılan kontroller, motor testi durumu ve sonraki somut iş kaydedilir. Yüksek kullanımda yeni bölge açılmaz; mevcut dosyalar doğrulanıp güvenli bir durma noktası bırakılır. Kullanım yüzdesi iş miktarından güvenilir biçimde tahmin edilemediği için ara kontrol gerekir; reset kredisi kendiliğinden kullanılmaz.

## Önceki kabul noktası — 1B.1

[Rûm demografi ve kurum paketi](../../scenarios/atlas/phase01b_rum_demography/README.md): 27 milyon doğrudan nüfus, 25 bölge, %40,18 ağırlıklı eğitim girdisi, 24 kanun ve üç kurum.

## Önceki kabul noktası — 1B.2

[Rûm özgürleşme ve ekonomi omurgası](../../scenarios/atlas/phase01b2_rum_economy/README.md): devralınan 216.325 köle statüsü kültür/din kaybı olmadan özgürleştirildi; 1.231 bina seviyesiyle kömür–demir–çelik–alet, dokuma, gıda, kâğıt, ulaşım ve idare omurgası kuruldu.

## Önceki kabul noktası — 1B.3

[Rûm silahlı devleti](../../scenarios/atlas/phase01b3_rum_military/README.md): saray/mülk sahibi uzlaşması, merkez ordusu ve meslek bürokrasisi başlangıç hükümetine çevrildi. 160 profesyonel tabur ve 48 gemi, top–mühimmat–patlayıcı zinciriyle birlikte doğrulandı; açık mal kapasitesi oluşum girdilerinden sonra pozitiftir. 452 diğer ülke değişmedi ve yeni uyarı yok. Atlas şeması başlangıç borç/hazine alanı sunmadığı için borç anaparası uydurulmadı; askerî maaş, piyasa, meşruiyet ve donanma hazırlığı motor kapısıdır.

## Önceki kabul noktası — 1B.4A

[Altı Nizam bağlısı](../../scenarios/atlas/phase01b4a_nizam_subjects/README.md): Bosna, Arnavutluk, Tuna, Adana, Erzurum ve Trabzon için toplam 6,55 milyon nüfus, 258 bina, 66 tabur ve 14 gemi; ortak H1 hukuk/kurum omurgası ve ülkeye özgü hükümetler doğrulandı. 17.806 devralınmış köle statüsü kültür/din kaybı olmadan özgürleştirildi. Trabzon şehir hubı atabegliğe aktarıldı; Rûm nüfusu ve kuvvetleri değişmedi. 446 diğer ülke aynıdır ve yeni statik uyarı yoktur. Nizam sözleşmesi, pazar, meşruiyet ve emancipasyon etkisi motor kapısıdır.

## Önceki kabul noktası — 1B.4B

[Bağımsız Ortadoğu ara kuşağı](../../scenarios/atlas/phase01b4b_independent_belt/README.md): Kürdistan, Basra, Şam, Cebel-i Lübnan, Kudüs ve Kuveyt için toplam 4,52 milyon nüfus, 242 bina, 68 tabur ve 13 gemi; H7/H8 hukuk farkları, kurumlar, hükümetler ve ticaret bağımlılıkları doğrulandı. Basra 3.530 devralınmış köle statüsünü özgürleştirirken beş H8 hanedanı kendi yazılı başlangıç hukukunu korur. Altı ülke bağımsızdır, 447 diğer ülke değişmemiştir ve yeni statik uyarı yoktur. Vanilla'nın tek Basra liman hubı Kuveyt'te kaldığı için ikinci Basra limanı ayrı state-region harita kararıdır.

## Güncel devam noktası — 1B.5

[Rûm statik entegrasyon denetimi](../../scenarios/atlas/phase01b5_integration_audit/README.md): Atlas'ın değiştirdiği yedi history klasörünün üretilmiş çıktısında `TUR`, `GRE` veya `ION` kalmadığı doğrulandı. Bunun yanında yüklenmeye devam eden 10 vanilla başlangıç dosyasında 29 etkin referans; event, journal, on_action ve diğer runtime tanımlarında 30 dosyada 253 etkin referans bulundu. Doğrulanmış parse/build çökmesi yoktur, ancak eski karakter, power bloc, antlaşma, lobi, AI ve global başlangıç davranışları oynanabilir sürümü bloke eder. Altı Nizam bağı doğru kurulmuştur; yüzde 8 gelir aktarımı sabit katkı değildir ve yazılı levy, pazar ve karşılıklı fesih şartları henüz uygulanmamıştır. Basra–Kuveyt tek port topolojisi ayrı harita kararı olarak ertelendi. **Bir sonraki çalışma 1B.5B:** dar başlangıç uyumluluk katmanı ve Nizam sözleşmesinin düzeltilmesi; ardından izole motor açılışı.
