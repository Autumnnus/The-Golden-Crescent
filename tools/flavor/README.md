# Flavor Studio

**Hikâyeyi anlat → diyagramı incele → onayla → oyun dosyalarını üret.**

Atlas'tan bağımsız event ve günlük (journal entry) aracı. Ülke, kültür, din ve siyasi koşulları aynı plan içinde tutar; seçimleri, gecikmeleri ve günlük sonuçlarını birbirine bağlar. LLM planı yazar; sen hikâyeyi ve diyagramı değerlendirirsin.

## En kısa kullanım

- **Mac:** mod kökündeki `Flavor.command` dosyasına çift tıkla, Enter'a bas.
- **Windows:** `Flavor.bat` dosyasına çift tıkla.
- **Terminal:** `./Flavor.sh`.

Menüde **1** örnek hikâyenin diyagramını açar. **2** kendi YAML/JSON planını seçmeni sağlar. İlk kurulum Python 3.10+, Victoria 3 ve eksik paketler için internet gerektirir. Sonraki önizlemeler çevrimdışı çalışır; sunucu gerekmez. Oyun farklı yerdeyse Atlas'taki gibi `VIC3_GAME_DIR` gerçek `game` klasörünü göstermelidir.

Diyagramda düğüme tıkla. Sağda metni, koşulları, görsel tercihini ve sonuçları incele. Event seçeneğine veya günlük sonucuna tıklayarak bağlantıları gez. Bu bir **hikâye provasıdır**; oyun koşullarının doğru olduğunu varsayıp motoru simüle etmez.

Hazır olduğunda **Taslağı onayla** düğmesiyle onay belgesini indir; LLM'ye dosyayı belirt. Sohbette belirli diyagramı açıkça onaylaman da yeterlidir: LLM yalnız o açık onaydan sonra `approve` komutuyla kaydı oluşturabilir. Taslak, görsel, bağlam veya araç uygulaması değişirse eski onay geçersiz olur.

Önizleme hiçbir event/journal oyun dosyası yazmaz. Onaydan sonra `build` ayrı bir paket üretir; `install` paketi etkin moda kurar. Kurulum Atlas'ın başlangıç tarihçesine ve metadata'sına dokunmaz.

## LLM'ye verebileceğin talep

> Önce tools/TOOLS.md ve tools/flavor/docs/LLM_WORKFLOW.md dosyalarını oku. Anlatacağım olay için bağımsız bir flavor planı oluştur. Gerçek oyun kimliklerini ve GFX kaynaklarını sorgula. Eventler, günlük hedefleri, seçimler, tetikleyiciler ve sonuçlar diyagramda görülsün. Ben bu taslağı onaylamadan oyun dosyalarını üretme veya kurma. Hikâyem: …

Harita/ekonomi de değişecekse şunu ekle:

> Atlas senaryosunu ayrı kaynakta tut; flavor doğrulamasına tam scenario-report.json dosyasını bağlam olarak ver. İki aracın kaynaklarını ve ürettiği dosyaları birbirine karıştırma.

## Klasörler

```text
tools/flavor/
  flavor.py               CLI
  launch.py               kısa menü / bağımlılık kurulumu
  studio/                 kaynak kataloğu, plan, önizleme, derleyici
  web/                    çevrimdışı diyagram arayüzü
  docs/LLM_WORKFLOW.md     LLM çalışma sözleşmesi
  docs/SYNTAX.md           plan alanları ve desteklenen işlemler
  docs/VERIFICATION.md     kaynak kanıtları, testler ve sınırlar
  examples/academy.yml    örnek; etkin oyun içeriği değildir
  tests/                  sentetik testler
flavor/projects/          kendi hikâye planların ve yerel görsellerin
build/flavor/PAKET/
  review/                 index.html, review.json, flow.mmd
  bundle/                 yalnız onaydan sonra üretilen oyun dosyaları
.flavor/installed/        etkin kurulumların dosya sahipliği manifestleri
```

Planlar ve özgün görseller sürüm kontrolünde tutulabilir. `build/` yeniden üretilebilir. `.flavor/installed/` manifestlerini kurulu içerikle birlikte koru; elle silmek aracı dosyaların sahibi konusunda belirsiz bırakır ve üzerine yazmayı durdurur.

## Komutlar

```sh
# Rehberde P yerine kendi planının yolunu kullan:
.venv/bin/python tools/flavor/flavor.py catalog media --query middleeast
.venv/bin/python tools/flavor/flavor.py catalog laws --query school
.venv/bin/python tools/flavor/flavor.py validate P
.venv/bin/python tools/flavor/flavor.py preview P --open
# Kullanıcının onay belgesinden sonra:
.venv/bin/python tools/flavor/flavor.py build P --approval ONAY.json
.venv/bin/python tools/flavor/flavor.py install P --approval ONAY.json
.venv/bin/python tools/flavor/flavor.py check ve_paket --plan P
```

Mac/Windows/Linux başlatıcıları aynı argümanları geçirir: `./Flavor.sh preview P --open` veya `Flavor.bat preview P --open`. Geliştirici komutları için doğrudan CLI kullanılabilir.

**Bir hata alırsan:** İlk hata satırını LLM'ye ver. “Onay eski” hatasında güncel diyagramı yeniden incele. “Elle değiştirilmiş dosya” hatasında oyun çıktısını zorla ezme; değişikliği kaynak plana taşı ve sahiplik uyuşmazlığını çöz. `check`, kurulu dosyaları manifest ile; `--plan` verildiğinde kaynak sürümüyle de karşılaştırır.

Desteklenen sözleşme ve bilinçli sınırlar: [SYNTAX](docs/SYNTAX.md), [doğrulama](docs/VERIFICATION.md).
