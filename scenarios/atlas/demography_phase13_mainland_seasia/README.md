# Demografi 13 — Güneydoğu Asya anakarası

Bu dilim [yazılı dünya atlasındaki](../../../docs/scenario/dunya_atlasi.md) Burma, Siyam, Đại Nam, Şan, Kuki, Chiang Mai, iki Lao yönetimi, Kamboçya, Khmer Loeu, Sip Song Chau Tai ve Degar'ın **28 doğrudan state payını** etkin Atlas kaynağına işler. Hindistan sınırındaki Kuki payı ve Siyam'ın Malaya payı aynı ülke toplamında sayılır; bağlı Lao/Khmer yönetimleri Siyam nüfusuna eklenmez. [Plan](plan.yml) devlet toplamlarını, state okuryazarlığını ve tek province düzeltmesini; [dondurulmuş POP kaynağı](source-pops.json) uygulama öncesi nüfusu gösterir.

| Ülke | Doğrudan nüfus | Ağırlıklı okuryazarlık girdisi |
|---|---:|---:|
| Burma `BUR` | 4.300.000 | %18,95 |
| Siyam `SIA` | 4.050.000 | %19,93 |
| Đại Nam `DAI` | 6.700.000 | %21,09 |
| Şan `SHS` | 650.000 | %15,00 |
| Kuki `KKI` | 90.000 | %10,72 |
| Chiang Mai `CMI` | 950.000 | %19,00 |
| Luang Prabang `LUA` | 330.000 | %16,00 |
| Champasak `CHP` | 150.000 | %15,00 |
| Kamboçya `CAM` | 740.000 | %17,00 |
| Khmer Loeu `KLO` | 47.000 | %10,00 |
| Sip Song Chau Tai `SCT` | 42.000 | %12,00 |
| Degar `DGR` | 58.000 | %10,00 |

Önceki bölge toplamı **17.419.657**, yeni doğrudan ülke toplamları **18.107.000** kişidir. Fark **687.343** kişidir. Pegu'daki 9.102 Mon/animist sakinli tek province, eski siyasi karttan kalan `DEN` sahibinden `BUR` sahibine geçirildi; dünya nüfusuna ikinci kez eklenmedi. Yazılı atlas Güneydoğu Asya'da Batılı Hristiyan toprak egemenliği öngörmez. [Harita değişiklik görünümü](../../../build/maps/mainland-seasia-boundary.png) yalnız bu province'i gösterir; diğer 674 state'in sınırı ve diplomasi aynıdır. Danimarka'nın diğer mülkleri değiştirilmedi.

Devralınan **ortak kültür–din çiftleri** korundu. Burma'da Bamar, Mon, Karen, Şan, Kachin ve Arakan'ın Müslüman toplulukları; Siyam'da Tay, Lao, Khmer, Malay ve Yue; Đại Nam'da Vietnamlı, Khmer, Cham, Miao ve mevcut yerel Hristiyan azınlıklar tek dine veya kültüre çevrilmedi. Kurulu oyundaki **489.883 açık köle mesleği** aynen korundu; bölgenin mevcut debt-slavery kanunlarıyla çelişen otomatik bir ilga yapılmadı. Bu hukuki/oynanışsal denge için ayrıca çalışma gerekir. Degar ülkesinin halkı kurulu oyunda ayrı `degar` kültürü bulunmadığından `champa/animist` ve `khmer/animist` karşılıklarıyla kalır; bu temsil eksiktir.

[22 hub yerleşim profili](city-profiles.yml) toplam **2.004.000** kişiyi state POP'larının tahmini alt kümesi olarak gösterir; yeni nüfus, bina veya meslek değildir. Her profil kurulu Türkçe hub adı, gerçek hub province sahibi ve POP kültür–din alt toplamına karşı doğrulandı. Khmer Loeu ve Sip Song Chau Tai paylarının oyundaki hub province'i başka sahibin kontrolünde olduğundan onlara yanlış konumlu şehir profili uydurulmadı.

`prepare.py` adayı üretir, `verify.py` 28 payı, 22 yerleşimi, transfer edilen province/nüfusu, diğer dünya POP'larını ve değişmeyen diplomasiyi sınar. [Atlas önizlemesi](../../../build/maps/mainland-seasia-demography.html) ve aday build geçti; etkin build/check ile siyasi denetim **0 hata, önceki 25 uyarı** verdi. Dünya nüfusu **1.090.530.767** oldu. Şan, Kuki, Khmer Loeu, Sip Song Chau Tai ve Degar'ın etkin raporda başlangıç bina seviyesi **0**; bu dilim ekonomi, kanun/ordu, kurum veya gerçek motor okuryazarlığı dengesi değildir. Bu revizyon oyun motorunda ayrıca açılıp test edilmedi.
