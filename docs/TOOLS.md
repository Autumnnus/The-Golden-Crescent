# Ortak araçlar

Bu modda Atlas/Flavor uygulama kodu bulunmaz. Tek ortak repo bilgisayarda `vic3-mod-tools` olarak tutulur. Yerel bağlantısı Git dışında `.vic3-tools.local.json` içindedir; `VIC3_TOOLS_HOME` ile geçersiz kılınabilir. Paylaşılan `.vic3-tools.json` hedef mod ayarlarını tutar.

## Kullanım

Mac: **Tools.command** → **1 Atlas** veya **2 Flavor**. Windows: **scripts/Tools.bat**. Terminal: **sh scripts/tools.sh**.

Mod terminalinden:

```sh
python3 scripts/tools.py doctor
python3 scripts/tools.py docs
python3 scripts/tools.py atlas preview
python3 scripts/tools.py flavor preview flavor/projects/hikaye/plan.yml --open
```

`docs` komutu ortak kısa rehber, araç seçimi ve LLM rehberlerinin tam yollarını gösterir. Ayrıntılı komutlar oradadır. Sunucu veya port kurulumu gerekmez. `build/` içindeki HTML önizlemeleri doğrudan açılır.

## Başka bilgisayar veya araç reposu taşınırsa

Ortak araç reposunu indir/kopyala. O reponun terminalinde:

```sh
python3 vic3tools.py init "/tam/yol/The-Golden-Crescent"
```

Bu bağlantı makineye özeldir; modun Git reposuna kişisel dizin yolunu ekleme. Oyun bulunamazsa `VIC3_GAME_DIR` kullan veya mod ayar dosyasına `game_dir` ekle. `doctor` yanlış yolu açıkça gösterir.

## LLM'ye verilecek kısa görev

> `python3 scripts/tools.py docs` ile ortak rehberleri bul ve WORKFLOWS.md dosyasını oku. Bu mod için senaryomu uygun araçlarla oluştur. Önce harita/diyagramı göster; Flavor diyagramının tam sürümünü onaylamadan oyun kodu üretme veya kurma. Senaryom: …

Atlas ve Flavor birlikte kullanılabilir. Her komut bu modun kökünü açıkça geçirir. Önizleme, cache, onay ve kurulum manifestleri diğer modlarla paylaşılmaz. Araç güncellemesi/taşıma sonrası eski Flavor onayları geçersiz olabilir; diyagramı yeniden üret ve yeniden onay al.

Eski `Atlas.*`, `Flavor.*` ve `tools/` komutları emekliye ayrıldı. Ortak araç reposunun `docs/MIGRATION.md` dosyası taşıma kararını ve yerel yedeği açıklar. Bu moda özel Codex otomasyon betiği `scripts/maintenance/` altında korunur; araç menüsünden otomatik çalıştırılmaz.
