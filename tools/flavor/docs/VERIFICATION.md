# Doğrulama ve sınırlar

İlk uygulama 12 Eylül 2026'da kurulu Victoria 3 **1.13.11** script/veri dosyaları okunarak hazırlandı. Motorun C++ kaynak kodu erişilebilir değildir. Kurulum ve oyun günlükleri salt okunur referanstır; testler oyun kurulumuna dosya yazmaz.

## Motor sözdizimi için kullanılan kanıtlar

| Kaynak, `game/` altında | Karar |
|---|---|
| `common/on_actions/_on_actions.md` | Vanilla on_action'a yeni effect bloğu eklemek çakışır. Ayrı isimli on_action tanımlanır, vanilla hook'a yalnız `on_actions = { ... }` listesi eklenir. |
| Aynı belge: Root = Country pulse listesi | Girişler `on_monthly_pulse_country` / `on_yearly_pulse_country` ile country scope'ta çalışır. |
| Aynı belge: `trigger_event = { on_action = ... days = ... }` | Gecikmeli bağlantılar ayrı teslim on_action'ına yönlendirilir. O anda koşullar, ülke varlığı ve tek kullanım kontrol edilir. |
| Aynı belge: effect ve events eşzamanlılığı uyarısı | On_action'ın `events` listesinde başka bir effect'in önceden çalıştığı varsayılmaz. Değişken atama ve sonraki tetikleme aynı effect zincirinde açık sırada üretilir. |
| `events/canal_events.txt` | Country event alanları, localization bağlantıları, `event_image.video`, icon, immediate, options, `add_journal_entry` ve ülkeler arasında event iletimi. |
| `common/journal_entries/00_canals.txt` | Manüel başlayan journal, country scope complete/on_complete, aylık ilerleme, current_value, goal_add_value ve `scope:journal_entry.is_goal_complete`. |
| `common/journal_entries/00_acw_entries.txt` | Gün cinsinden timeout ve on_timeout. |
| `events/1848.txt` | Seçenek AI ağırlığı `ai_chance.base`. |
| `events/indochina.txt`, `common/on_actions/00_code_on_actions.txt` | Resmî din, birincil kültür, ülke varlığı, tarihler, değişkenler ve state sahipliği koşulları. |
| `events/bic_breakup.txt` | Country scope `add_primary_culture` / `set_state_religion`. |
| `gfx/media_aliases/media_aliases.txt` | Medya alias'ı, fiziksel video ve fallback zinciri; özel videoya ayrı alias üretimi. |
| `common/static_modifiers/bulgarian_modifiers.txt`, `content_304_modifiers.txt`, `00_test_modifiers.txt` | Bu sürümün desteklediği prestige/authority/bureaucracy country modifier anahtarları. |

Katalog gerçek ID düğümünü ve kaynak dosyasını döndürür. Planın kullandığı tanım, script sözleşmesi, GFX ve isteğe bağlı dünya raporunun dosya özetleri onaya dahil edilir. Derleyici/önizleme uygulaması değişince de onay yenilenir. Bu, bütün yeni oyun sürümlerini otomatik destekleme garantisi değildir; sözdizimi değişirse adaptör ve testler güncellenmelidir.

## Otomatik test kapsamı

`tests/test_flavor.py`, gerçek kurulu tanımlarla plan ve derleyici regresyonlarını çalıştırır:

- Bağlı ve dallanmış örnek; kopuk hedef, ulaşılamayan düğüm, döngü, yinelenen event numarası.
- Eksik koşulsuz seçenek, yanlış alan, yanlış veri türü, yinelenen YAML/JSON anahtarı, döngülü YAML alias.
- Gerçek ülke/teknoloji/kültür/din/medya kimlikleri; ülke kültürü ile pop kültürünün farklı scope'ları.
- Tarih doğrulaması, değişken referansları, ham script ve bağlanmamış dinamik localization'ın reddi.
- DDS yükleme/kopyalama, eksik GFX, yol dışına çıkma, sahte Bink başlığı.
- Eksik/eski/false onayın reddi; plan veya kaynak değişikliğinin onayı geçersiz kılması; sohbet onayının mevcut review sürümüne bağlanması.
- Önizlemede yalnız HTML/JSON/Mermaid üretilmesi; HTML script kapatma metninin escape edilmesi.
- Üretilen PDX dosyalarının parse/dump/parse eşitliği, UTF-8 BOM ve localization anahtarları.
- Ayrı country hook, gecikmeli teslim kontrolü, pending/seen koruması, başka ülkeye geçiş ve journal sonuçları.
- İlerleme sıfırlama, aylık sayaç ve hedef/koşul birleşimi.
- Atlas raporunda yeni ülkeye önizleme; etkin tanımı olmadan kurulumun reddi; bağlamdan kaldırılan ülkenin reddi.
- Ayrı bundle üretimi; Atlas history/metadata'sının korunması; elle değiştirilmiş dosya ve symlink üzerine yazmanın reddi; manifestin başka dosyalara sahiplik iddia edememesi; yazma hatasında geri yükleme.

`tests/browser.cjs`, gerçek üretilen çevrimdışı HTML üzerinde diyagram, seçenek → günlük → sonuç akışı, dil değiştirme, checkbox ile onay belgesi indirme, Escape ile dialog kapatma, mobil yatay taşma ve ağsız çalışma kontrollerini yapar. Tarayıcı testinin onay belgesi **sentetik testtir, kullanıcı onayı değildir**; adı ve notu bunu açıkça belirtir.

Test çıktıları: `build/flavor-tests/unit.log`, `browser.log`, `browser/desktop.png`, `browser/mobile.png`. Eski Atlas regresyonu ve aktif `tgc.py check` ayrıca çalıştırılır. Geliştirme testlerinde kurulan paketler yalnız geçici `build/` alt dizinlerinde tutulur; örnek etkin moda kurulmaz.

```sh
PYTHONPATH=tools:tools/flavor .venv/bin/python -m unittest discover -s tools/flavor/tests -v
.venv/bin/python tools/flavor/flavor.py preview tools/flavor/examples/academy.yml
# Geliştirici ortamında Node + Playwright gerekir. TGC_CHROME kurulu Chrome yoludur.
node tools/flavor/tests/browser.cjs
```

## Bilinçli sınırlar

1. **Motor testi yapılmadı.** Statik sözdizimi ve kaynak örnekleri doğrulandı. Olayların gerçek dispatch sırası, pulse zamanları ve günlük sonuç önceliği oyun motorunda ayrıca sınanmalıdır. Bu görevde kullanıcı belirli bir oyun hikâyesi onaylamadığı için demo etkinleştirilmedi.
2. **Sabit ülke scope'u.** Dinamik karakter/alıcı seçimi, saved scope taşıma, portre/özel event GUI'si, dinamik localization ve keyfî ham script yoktur. Desteklenmeyen işler sessizce kabul edilmez. Daha ileri ihtiyaçta kaynak kanıtlı DSL desteği eklenir.
3. **Tek kullanımlı DAG.** Tekrar eden veya döngülü olaylar yoktur. Çoklu giriş AND birleşimi değil, ilk geçerli teslimdir. Kuyruğa alınan hedef koşulunu teslimde kaybederse atlanır. Tüm mantıksal çelişkiler veya ulaşılabilir dünya durumları hesaplanmaz.
4. **Başlangıç dünyası sınırı.** Kültür/din/bina/teknoloji tanımları katalogdan gelir; bu tool yeni temel ülke/kültür/din veritabanı türleri oluşturmaz. Bunlara bağlı hikâyeyi üretir. Atlas raporu bir bağlam snapshot'ıdır; etkin dünyanın bütün ekonomik değerleriyle otomatik eşitlik kontrolü değildir. Yeni ülke tanımı kurulumda kontrol edilir.
5. **Görsel sınırı.** DDS simgesi okunur; mevcut video alias'ları ve fallback yolları çözülür. Yeni Bink videonun sadece başlığı ve dosya varlığı doğrulanır; tam codec/DLC davranışı veya tasvirin tarihî uygunluğu otomatik kanıtlanmaz. Poster yalnız tarayıcıda kullanılır.
6. **Onay sınırı.** JSON makbuz kimlik doğrulama/imza sistemi değildir. Tam plan ve bağımlılık sürümünü sabitler; LLM'nin kullanıcı adına onay uydurmaması çalışma sözleşmesinin parçasıdır. Değişiklik içeren kullanıcı notu, değişiklik tamamlanmadan onay sayılmaz.
7. **Kurulum sınırı.** Manifest sadece bu paketin dosyalarını yönetir. Mevcut vanilla event/journal'larını silmez ve save migrasyonu yapmaz. Dosya yazımı hatalarında geri yükleme vardır; güç kesilmesi veya geri yüklemeyi de engelleyen disk arızası için tam işlemsel garanti yoktur.
8. **Platform testi.** Python CLI, Mac `.command/.sh` ve Chrome önizlemesi bu makinede çalıştırılır. Windows `.bat` başlangıcı kaynak incelemesiyle kontrol edilir; Windows'ta çalıştırıldığı iddia edilmez.
