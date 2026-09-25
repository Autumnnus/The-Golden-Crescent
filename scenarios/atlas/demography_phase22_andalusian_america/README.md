# Demografi 22 — Endülüs Amerika'sı: Meksika, Orta Amerika ve Karayipler

Bu paket [Amerika tasarımının](../../../docs/scenario/senaryo_amerika.md) Endülüs Amerika'sı bölümünü nüfusa uygular. **30 state'te 26 ülkenin 35 doğrudan payı** etkin Atlas kaynağına işlendi: Meksika'nın 15 state'i ile Orta Amerika/Karayipler teknik bölgesinin 20 payı. Sınır, bağlılık ve bina değişmedi. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Kimlik kararları

- Kurulu oyunun `mexican`, `central_american`, `caribeno` kültürleri İspanyolca konuşan yerleşimci mirası taşır. Bu evrende Endülüs kolonilerinin Romans/Arapça kreol toplumu ("Yeni Endülüslü") için en yakın karşılık olarak ölçülü kullanıldı ve Sünni/Katolik olarak bölündü. Endülüs'ten gelen yöneticiler ve tüccarlar `ve_andalusi`, Mağribi ve Sefarad toplulukları ayrıca yer alır.
- **Yeni Endülüs** (2,11 M): Meksika havzasında Nahua çoğunluğu korunur; Nahua halkı Sünni, Katolik ve yerel inançlar arasında bölünür. Kreol pay yaklaşık %24'tür. Birincil kültürler `nahua, mexican` oldu. 1801 kalıtsal kölelik ilgası nedeniyle köle POP'u yoktur.
- **İç Meksika meclisleri ve Maya:** Yerel halklar çoğunluktadır; kreol tüccar/madenci toplulukları %12–28 arasıdır. Hatalı `nahua`/`mayan` birincil kültürleri gerçek sahiplerine göre düzeltildi: Baja `hokan`, Durango ve Sonora/Sinaloa `oodham`, Rio Grande `nahua, oodham`, Chihuahua `apache, oodham`, Bajío `nahua, tarascan`, San Salvador `nahua` (Pipil), Nicaragua `nahua, miskito`, Kosta Rika `muisca` (Chibcha karşılığı). Eski Fransız Antil meclisleri `VLE`/`VWI` `afro_caribbean` yerine Fransız kreolü `afro_antillean` oldu.
- **Orta Amerika:** İspanyol fethi yaşanmadığı için devralınan `central_american` çoğunluğu (Honduras'ta %99) yerel halklara döner; Lenca, Chorotega ve Matagalpa için ayrı oyun kültürü bulunmadığından `mayan`, `nahua` ve `muisca` karşılık olarak kullanılır. Kreol topluluklar %15–30'dur.
- **İnci Adaları** (`VPI`, 1,58 M): H10 hukukuna göre kölelik yasaldır; `law_legacy_slavery` yazıldı. Küba ve Porto Riko'daki **441.525** devralınmış köle sayısı korunur, fakat tek "Katolik Afrikalı" kimliği yerine %50 Katolik, %25 Müslüman, %25 yerel inançlı olarak dağıtıldı. Kanona göre İngiliz değil Endülüs kolonisi olan **Jamaika**, devralınmış İngilizce kreol/Protestan nüfus yerine Endülüs plantasyon adası olarak kuruldu: 380 bin kişinin **190.000'i köleleştirilmiş** Afro-Karayiplidir. Bu yeni ve ağır bir tasarım kararıdır.
- Nikaragua ve Panama yerel meclislerindeki **5.100** köle POP'u serbest bırakıldı. Haiti, Londra tacı, Danimarka, Hollanda ve Venezuela'nın Karayip payları devralınan bileşimiyle ölçeklendi; Santo Domingo'daki açık asker/memur meslekleri korundu.
- Homeland'ler Faz 21 kuralıyla yazıldı (yerli ≥%1 korunur, yerleşimci/diaspora ≥%10, yeni ≥%10); ör. Jamaika `afro_caribbean` → `afro_caribeno, caribeno`, Kosta Rika `central_american` → `central_american, muisca, nahua`.

| Alan | Önce | Etkin başlangıç |
|---|---:|---:|
| 35 hedef pay | 11.951.647 | 11.739.100 |
| Açık köle mesleği | 446.625 | 631.525 |
| Dünya nüfusu | 1.089.185.598 | 1.088.973.051 |

[38 yerleşim profili](city-profiles.yml) state nüfusunun içindeki tasarım alt kümeleridir. Yalnız yerel dillerden (Meksika Şehri, Toluca, Guanajuato, Oaxaca, Havana, Bayamo, Panama), Endülüs Arapçasından (Guadalajara) veya yeri gerçekten tutan koloni gücünden gelen adlar (Port au Prince, Saint-Pierre, Nassau, Willemstad, Christiansted) profillendi. Veracruz, San Juan, Kingston gibi Kastilya azizi/İngilizce hub adları bu evrende anakroniktir; oyundaki görünen adlar değişmedi.

## Doğrulama

[Önizleme](../../../build/maps/andalusian-america-demography.html) 0 sınır değişikliği gösterir. Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/andalusian-america-verification.json) (hedef dışı POP/nüfus korunur, ülke tanımı farkları planla sınırlıdır, yeniden kimliklenen köle toplamı aynıdır, köle tutan her ülkenin raporda kölelik kanunu vardır, homeland ve hub sahipleri planla eşleşir), etkin Atlas `build/check` (**0 hata; 25 uyarı**) ve siyasi denetim geçti. Motor testi yapılmadı; okuryazarlık ilk gün hesabında değişebilir. Yerel meclislerin bina/teknoloji/kanun başlangıcı ekonomi–hukuk aşamasına kalır; Jamaika'nın yeni plantasyon nüfusu ekonomi aşamasında bina ve iş kapasitesiyle birlikte dengelenmelidir.

Yeniden üretim: `andalusian-america-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `snapshot.py` (dondurulmuş kaydı üzerine yazmaz) → `prepare.py` → `scenario validate/build --out build/scenarios/andalusian-america-candidate` → `verify.py`.
