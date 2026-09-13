# Faz 1A — Rûm coğrafya ve bağlılık önizlemesi

**13 Eylül 2026 · Harita incelemesi için üretildi; etkin mod veya oynanabilir sürüm değildir.**

Kaynak: [geography.json](geography.json). İl kimlikleri, eski sahipler ve şehir noktaları: [source-evidence.json](source-evidence.json). Ana tasarım: [senaryo dizini](../../../docs/scenario/README.md). Doğrulama sonucu: [verification.json](verification.json).

## Kapsam ve açılış

41 eyalet planı, 13 ülke tanımı. Rûm; Bosna, Arnavutluk, Tuna, Adana, Erzurum ve Trabzon olmak üzere altı ayrı bağlı yönetime sahiptir. Kürdistan, Basra, Şam, Cebel-i Lübnan, Kudüs ve Kuveyt bağımsızdır. Sırbistan ve Eflak'ın eski Osmanlı ilişkileri temizlenir. TUR/GRE/ION bu önizlemede topraksız kalır. Dünyanın diğer bölgelerinde vanilla yalnız karşılaştırma zemini olarak bulunur; görünen büyük Rusya, İngiliz Hindistanı veya birleşik Fransa yeni senaryonun kararı değildir.

Mod kökünde tek komut:

```sh
python3 scripts/tools.py atlas preview --scenario scenarios/atlas/phase01_rum/geography.json --region RUM,BOS,ALB,BUL,ADA,ERZ,TRB,KUR,BSR,SYR,LEB,PAL,KUW --out build/maps/phase01-rum.html
```

Hazır dosya: `build/maps/phase01-rum.html`; siyasi ve değişim haritaları aynı klasörde `phase01-rum-political.png` ve `phase01-rum-changes.png`. `build/` silinirse önizleme kaynak JSON'dan yeniden üretilebilir. Nihai kaynak henüz `world/` içine taşınmaz.

## Sınır kararları ve kaynak tuzakları

| Alan | Bu önizlemede uygulanan | İnceleme sınırı |
|---|---|---|
| Adana | Adana/Mersin ve batı ova alanı ADA; Aintab/Gaziantep ve doğu geçitleri RUM | Toros sınırındaki numarasız küçük alanlar doğal il çizgisine uyar; ayrı tarihsel sınır iddiası değildir |
| Halep | Halep, Antakya, İskenderun ve Lazkiye kaynak hub'ları RUM | Aynı ildeki Tartus/Lazkiye hub paylaşımı oyun haritasının ölçeğidir |
| Erzurum | Erzurum/Erzincan ERZ; Van çevresinde dokuz il RUM | Van, ana Rûm gövdesinden ayrıdır; ulaşım atabeylik/Kürdistan transitine bağlıdır. Kesintisiz doğrudan kara bağlantısı varmış gibi sunulmaz |
| Trabzon | Batıdaki Samsun/Ordu illeri RUM; doğu kıyısı ve ilgili vadiler TRB | Kaynakta Trabzon bir wood hub, ana city Ordu'dur; başkent şehrinin gerçek gösterimi 1B'de çözülecek |
| Kars | Eski TUR payı ERZ | Rus payları Kafkasya fazına kadar korunur; bunlar nihai Gürcistan/Ermenistan sınırı değildir |
| Basra | Basra çekirdeği BSR; Nasıriye/Kut/Amara kuzeyi RUM; Kuveyt çevresindeki üç il KUW | Eyaletin kaynak port hub'ı Kuveyt'te. Basra için liman/hub temsili 1B'nin zorunlu işi |
| Tuna | Bulgaristan ve Kuzey Trakya BUL; Dobruca'nın eski TUR payı BUL | Dobruca Rus payı Avrupa fazına bırakılır. Tırnova kaynakta mine hub, city Sofya; başkent şehir gösterimi tamamlanmadı |
| Balkan çevresi | Kosova ALB; eski TUR Sırp payları SER; eski TUR Karadağ payları MON | Bunlar belirsiz küçük sınırlar için bu turun yapımcı önerileridir. Avusturya kıyı payı korunur; Karadağ için henüz yeni ayrıntılı lore yazılmadı |
| Adalar | Girit, Kıbrıs, Ege/İyon adaları ve Malta RUM | Yeni Bursa bu bölgesel fazın dışında; Rûm'un dünya çapındaki bütün mülkleri tamamlandı denmez |
| Şam | Şam ve Transjordan SYR | Transjordan, Şam'ın çöl/geçit uzantısının geçici idari eşlemesidir; bütün çölün yoğun devlet denetiminde olduğu anlamına gelmez |

`BAS` vanilla'da Bastar'dır; Basra için boş olduğu doğrulanmış `BSR` kullanıldı. Başka mod veya ülke etiketi üzerine yazılmadı. Devlet resmî dinleri için `sunni` mevcut motor kimliği olarak kullanıldı; Müçtehidî kurumlar veya Basra'nın çoğulcu hukuku bununla tamamlanmış sayılmaz. Halkların dinleri dönüştürülmedi.

## Oynanabilir sürümün önündeki zorunlu işler — Faz 1B

Bu maddeler çözülmeden aktif build yapılmaz; bu koşul harita önizlemesinin tamamlanmasını engellemez.

1. **Ekonomi ve nüfus:** bu paketteki nüfus/üretim vanilla aktarım tabanıdır. Yeni sınırda korunması doğrulandı; alternatif dünya hedefi değildir. Rûm 25–29 milyon hedefi, bölgesel kültür/din bileşimi, eğitim ve servet henüz uygulanmadı. Bölünmüş eyalette mevcut binalar en büyük payı alan ülkeye gider; bu nedenle Adana/Basra/Kuveyt'te bina bulunmaması gelecek tasarım değildir. Liman, atölye ve istihdam dağılımı açıkça kurulacak.
2. **Teknoloji:** geçici tier 4 yalnız devralınan binaların kaynak gereksinimlerini karşılayan derleme tabanıdır. Sanayi öncüsü Rûm'un gerçek teknoloji listesi değildir; ülke ve sektör bazında değiştirilecek.
3. **Kanun/kurum/IG:** H1/H8 ve Basra H7 açık motor kanunlarına çevrilecek; hanedan/cumhuriyet, dinî haklar ve resmî kültürlerin ayrımcılık etkisi birlikte incelenecek.
4. **Ordu/donanma:** yeni ülkelere ordu aktarılmaz; bu önizlemede orduları yoktur. Kaybettiği dört Levant eyaletindeki Mısır birimleri derleyici tarafından çıkarılır. Nüfus, bütçe, hammadde ve HQ konumuyla uyumlu yeni birlikler yazılacak.
5. **Nizam bağlılığı:** `ve_rum_nizam_dependency` genel kaynak vassal türünden türetilmiş teknik prototiptir. %8 değişken gelir aktarımı sabit tarihsel katkıyı temsil etmeye yetmez; `join_overlord_wars` sınırlı sefer kotası değildir. Devralınan annex-on-formation ve özerklik geçişleri incelenmeden gerçek anayasa uygulaması sayılmaz. Gelecekteki diplomatik oyun/arayüz davranışı doğrulanmadı.
6. **Şehir, karakter, olay:** Basra limanı ve Trabzon/Tırnova başkent yerleşimleri; kaldırılan TUR/GRE/ION'a bağlı karakter, journal, on_action ve kaydedilmiş scope'lar incelenecek. Bu faz Flavor üretmez.
7. **Motor testi:** bütün başlangıç katmanları hazır olduğunda etkin build/check, ardından yeni oyun başlangıcı ve kısa ilerleme/log kontrolü yapılacak. Statik başarı crash olmayacağı garantisi değildir.

## Doğrulama ve araç düzeltmesi

Kaynak harita, il etiketli inceleme görselleri ve sonuç PNG'leri incelendi. Tam rapor ve ayrı üretilmiş paket `build/phase01/` altında; oyun/mod içerikleri etkinleştirilmedi.

Bu ilk gerçek senaryo, Atlas'ın eski nüfus aktarımında iki hata yakaladı: küçük/büyük harfli il kodları farklı sayılıyor; her yeni sahip için ayrı yuvarlama toplamı değiştirebiliyordu. Ortak araç reposunda karşılaştırma normalize edildi ve eski her nüfus grubu en büyük kalan yöntemiyle tam kişi sayısı korunarak dağıtıldı. Bina devrindeki aynı harf duyarlılığı da düzeltildi. Gerçek Malta/Batı Ege/Dobruca ve sentetik üç sahip/bina vakaları regresyon kapsamına eklendi. Kaynak JSON'a kaybı gizleyen yapay nüfus çarpanı eklenmedi.

Uyarılar baseline ile karşılaştırılır: eski dünya kaynak uyarıları ayrı; bu fazın dört Mısır birlik çıkarımı ayrı kayıtlıdır. Harita, kaynak ve rapor değişirse `verification.json` eski revizyonun kanıtı olarak kalır; yeniden doğrulanmadan güncel sayılmaz.

Son araç regresyon koşusu: **122 test başarılı**. Mod kökünde `python3 scenarios/atlas/phase01_rum/verify.py` mevcut rapor, harita ve kaynak eşleşmesini yeniden denetler; rapor/derleme değişmişse önce Atlas çıktıları yenilenmelidir.
