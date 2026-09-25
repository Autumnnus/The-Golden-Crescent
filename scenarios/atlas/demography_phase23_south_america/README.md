# Demografi 23 — Güney Amerika

Bu paket [Amerika tasarımının](../../../docs/scenario/senaryo_amerika.md) "tamamlanmamış fetih" ilkesini Güney Amerika nüfusuna uygular. **53 state'te 38 ülkenin 63 doğrudan payı** etkin Atlas kaynağına işlendi; sınır, bağlılık ve bina değişmedi. Bu paketle Amerika'nın üç teknik bölgesindeki bütün paylar açık nüfus planı taşır. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Kararlar

- **İber kalıntısı:** Devralınan POP'ların **6.524.856**'sı gerçek tarihteki İspanyol/Portekiz sömürge kültürlerindeydi (`south_andean`, `north_andean`, `platinean`, `brazilian`, `nordestino`, `paulista`, `sulista`, `amazonic`); bunlar **1.309.608**'e iner. Kalanlar Endülüs ve Fas ticaretine bağlı kreol tüccar/liman toplulukları ile Yeni İşbiliye ve Venezuela'nın kreol toplumudur; Sünni ve Katolik olarak bölünür.
- **And krallıkları:** Quito (918 bin), Cusco (632 bin) ve Charcas (230 bin) kendi Quechua/Aymara çoğunluklarıyla ve yerel inançla başlar; Hristiyan ve Müslüman dönüşümler cemaat ölçeğindedir. La Paz, Atacama ve Santa Cruz meclisleri de Aymara, Quechua, Guaraní ve Amazon halklarıyla kurulur.
- **Brezilya:** Fas Brezilyası (1,36 M) Mağribi/Berberi yerleşimciler, Fas Yahudileri, Tupi halkları ve Afrikalı-Brezilyalılarla kurulur. Pernambuco ve Bahia'daki **312.075** köle sayısı korunur; kanonun "daha küçük ayrı yerleşim ağı" olarak tanımladığı Rio'da Portekiz başkentinden kalan 265.153 köle **95.000**'e indirildi. Korunan köleler tek Katolik kimlik yerine Afrikalı-Brezilyalı (yerel inanç/Sünni), Yoruba, Hausa, Bakongo ve Fulbe gruplarına dağıtıldı. Fas'ın ana yurt kanunu izlenerek `law_slave_trade` yazıldı. İç yayla, Amazon ve güneyin yerel meclisleri Lusofon yerleşimci ve köle POP'ları yerine Tupi, Gê (`amazonian` karşılığı) ve Guaraní halklarıyla başlar.
- **Yeni İşbiliye** 62.000 köleyi korur (Katolik/Sünni/yerel inanç olarak yeniden dağıtıldı), `law_legacy_slavery` alır. **Venezuela** (`VNZ`) ile Lima kıyı yönetimi (`NPU`) devralınmış kreol kimliği ve kölelik kanunuyla kalır; köle sayıları korunur, Venezuela'da yeniden dağıtılır.
- **Hollanda Guyanası:** Yazılı hukuktaki H10 kölelik istisnası nedeniyle 180 bin kişinin **72.000**'i köleleştirilmiş olarak kuruldu; maroon toplulukları, Arawak/Karib halkları, Sefarad ve Fransız kreolü Cayenne toplulukları ayrıdır. Jamaika kararı gibi yeni ve ağır bir tasarım girdisidir.
- **Plata, Pampa ve Şili:** Kanondaki Fas tüccar mahalleleri Buenos Aires (90 bin) ve Montevideo'da Mağribi ağırlıklı kent toplulukları olarak yer alır; nehir ve otlak egemenliği Guaraní, Charrúa ve Pampa halklarındadır. Orta Şili "yerel yönetimleri" Picunche çoğunluğuyla kurulur (Mapuçe ile aynı oyun kültürü, ayrı siyasi birim); Güney Nehirleri, Tehuelche ve Mapuçe payları Patagonya halklarıyla başlar. `patagonian` Mapudungun ve Charrúa için geniş karşılıktır.
- **Kimlik ve din düzeltmeleri:** Vanilla `SPU`, `NPU`, `PRG`, `URU`, `PRA`, `PNI` birincil kültürleri yerel halklara, resmî dinleri `animist`e çevrildi; `IQU`, `VCS`, `VCQ` resmî dini de `animist` oldu. `VCS` (`chilean` → `patagonian, south_andean`), `VOR` (`muisca` → `amazonian`) ve Aymara ağırlıklı And yönetimlerinin kültür listeleri düzeltildi.
- **Kölelik:** Yerel (H9) yönetimlerdeki **675.091** köle POP'u serbest bırakıldı ya da yerleşimci akınıyla birlikte kaldırıldı. Açık köle mesleği 1.395.593 → 622.349.
- Homeland'ler Faz 21 kuralıyla yazıldı: 53 state'in 40'ında değişti (ör. Pernambuco `brazilian, nordestino, afro_brazilian` → `afro_brazilian, tupinamba, maghrebi`).

| Alan | Önce | Etkin başlangıç |
|---|---:|---:|
| 63 hedef pay | 13.630.090 | 10.653.000 |
| Dünya nüfusu | 1.088.973.051 | 1.085.995.961 |

[47 yerleşim profili](city-profiles.yml) state nüfusunun içindeki tasarım alt kümeleridir. Yalnız yerel dillerden gelen adlar (Quito, Bogotá, Cuzco, Arequipa, Potosí, Cochabamba, Temuco, Manaus, Cuiabá, Curitiba, Caracas, Paramaribo) ve yazılı kanonun kullandığı adlar (Recife, Rio de Janeiro, Buenos Aires, Montevideo, Cartagena) profillendi; Asunción, Santiago, Belém, São Paulo, La Paz gibi Kastilya/Portekiz kuruluş adları profillenmedi, oyundaki görünen adlar değişmedi.

## Doğrulama ve açık kalanlar

[Önizleme](../../../build/maps/south-america-demography.html) 0 sınır değişikliği gösterir. Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/south-america-verification.json), etkin Atlas `build/check` (**0 hata; 25 uyarı**), güncellenen siyasi denetim ve 38 araç öz testi geçti. Motor testi yapılmadı.

- Onaylı siyasi haritada Cusco şehir hub'ı `STATE_ICA` içindeki `SPU` payındadır; `VCU` Cusco Krallığı'nın başkenti Arequipa'dır. Yazılı kanon başkenti Cusco sayar; bu siyasi/başkent uyuşmazlığı ayrı karar ister.
- `PRG`, `URU`, `PRA`, `SPU` vanilla kölelik kanunlarını hâlâ taşır, fakat köle POP'ları kaldırıldı; hukuk aşamasında H9'a çevrilmeli. Yerel meclislerin bina/teknoloji/kanun başlangıcı yoktur.
- Fas Brezilyası ile Guyana'nın plantasyon nüfusu ekonomi aşamasında bina ve iş kapasitesiyle dengelenmelidir. `afro_brazilian` kurulu oyunda Lusofondur; Fas kolonisindeki Afrikalı kökenli topluluklar için yalnız en yakın karşılıktır.

Yeniden üretim: `south-america-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `snapshot.py` (dondurulmuş kaydı üzerine yazmaz) → `prepare.py` → `scenario validate/build --out build/scenarios/south-america-candidate` → `verify.py`.
