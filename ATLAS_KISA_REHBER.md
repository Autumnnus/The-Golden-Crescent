# Atlas — kısa kullanım

**Mac:** `Atlas.command` dosyasına çift tıkla.  
**Windows:** `Atlas.bat` dosyasına çift tıkla.  
**Linux / terminal:** mod klasöründe `./Atlas.sh` çalıştır.

Açılan menüde **Enter**: mevcut haritayı açar. İlk çalıştırmada eksik Python paketlerini ve harita önbelleğini hazırlar. İlk kurulumda internet, makinede Python 3.10+ ve Victoria 3 kurulumu gerekir. Mevcut Mac ortamında Python hazırdır.

- **2 — Senaryo önizle:** LLM'nin yazdığı YAML/JSON dosyasını terminale sürükle, Enter'a bas. Etkin mod değişmez.
- **3 — Kontrol:** etkin modda hatalı, eksik veya eski üretilmiş dosyaları kontrol eder.
- **4 — Derle ve kontrol:** `world/` kaynağını oyun moduna yazar. Yalnızca etkin senaryoyu güncellemek istediğinde kullan.

Harita açıldıktan sonra terminali kapatabilirsin. **Sunucu, port veya sürekli açık terminal gerekmiyor.** Daha sonra `build/maps/atlas_world.html` dosyasına doğrudan çift tıklayabilirsin. Kaynak değiştiğinde güncel harita için başlatıcıyı tekrar aç.

## LLM'ye ne söylemeliyim?

> Önce `tools/LLM_SCENARIO_WORKFLOW.md` dosyasını oku. Anlatacağım dünyayı version 2 senaryo olarak oluştur. Gerçek oyun kimliklerini sorgula, senaryoyu doğrula ve atlasını üret. Harita, nüfus, ekonomi, teknoloji, kanunlar, ordu ve diplomasi tutarlı olsun. Örnek senaryoları benim isteğim sayma. Senaryom: …

Fransa'ya özel bir varsayılan vasallık kuralı yoktur. Özel bağlılık türü ancak senaryoda açıkça tanımlanırsa oluşturulur.

## Açılmazsa

Mac dosyayı metin olarak açarsa **Birlikte Aç → Terminal** seç. Çalıştırma izni yoksa mod klasöründe bir kez `chmod +x Atlas.command Atlas.sh` çalıştır.

“Oyun bulunamadı” hatası için gerçek `game` klasörünü belirt:

```sh
# Mac/Linux; yolu kendi oyun kurulumuna göre değiştir:
VIC3_GAME_DIR="/oyunun/kurulu/oldugu/Victoria 3/game" ./Atlas.sh
```

Windows Komut İstemi'nde:

```bat
set "VIC3_GAME_DIR=D:\SteamLibrary\steamapps\common\Victoria 3\game"
Atlas.bat
```

Hata olursa başlatıcı başarılıymış gibi eski haritayı açmaz. Terminaldeki ilk hata satırını LLM'ye ilet. “Stale/edited/missing generated output” görürsen önce senaryo kaynağını doğrulat, sonra menüden **4** ile yeniden derle.

Ayrıntılı sözleşme: [LLM senaryo rehberi](tools/LLM_SCENARIO_WORKFLOW.md). Güvenilirlik incelemesi: [Araç denetimi](tools/TOOL_AUDIT.md).
