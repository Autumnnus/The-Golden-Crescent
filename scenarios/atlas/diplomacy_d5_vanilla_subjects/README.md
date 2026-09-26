# D5 — Vanilla bağlılık türlerine dönüş

**25 Eylül 2026 · etkin.** Kullanıcı kararı: 14 özel bağlılık türü (`ve_*`) kafa karıştırıcıydı ve ikonları yoktu. Şimdilik oyunun vanilla türleri kullanılacak. Kullanıcı ileride kendi türlerini ayrıntılı yazacak.

Bağlılık ağı (66 ilişki, üst ve alt devletler, bağımsızlık istekleri) aynı kaldı; yalnız türler değişti ([plan.py](plan.py) → [plan.yml](plan.yml)):

| Eski tür | Vanilla tür | Kural |
|---|---|---|
| Sıkı bağlar: Şah, Feodal, Özerk, Sözleşmeli, Nil, Emirlik, Japon | **puppet** (26); tanınmamış üst devlette **vassal** (Japonya–Ezo) | Vanilla vassal ve tributary yalnız tanınmamış üst devlete izin verir |
| Gevşek bağlar: Sınırlı Koruma, Hac, Sınırlı Haraç, Tatar Haracı | **protectorate** (20); tanınmamış üst devlette **tributary** (Siam, Dai Nam, Burma mandalaları) | Aynı |
| Sömürge Şartı | **colony** (9), Yeni Endülüs **dominion** (kanondaki geniş özerk şart) | Vanilla colony/dominion `colonial` alt ülke ister |
| Londra Tacı Denizaşırı Bağımlılıkları | **crown_land** | Doğrudan taç bağımlılığı |
| Taç Birliği | **personal_union** (İrlanda, Schleswig, Holstein) | |

On koloninin ülke türü `colonial` oldu: Yeni Endülüs, Yeni İşbiliye, İnci Adaları, Yeni Gırnata, Fas Brezilyası, Yeni İngiltere, Virginia, Yeni Hollanda, Vinland, Yeni Bursa. Bu tür tanınmış türle aynı ayarlarda çalışır; varsayılan bağlılığı vanilla colony'dir.

Özel tür, eylem ve yerelleştirme dosyaları artık üretilmez. Eski ikon kopyaları [runtime temizliği](../../runtime_cleanup/README.md) tarafından silinir.

**Vanilla davranışı:**
- Puppet ve colony üst devlete gelirin %30'unu, dominion %25'ini, tributary %20'sini, crown land %15'ini aktarır. Protectorate ve personal union gelir aktarmaz.
- Puppet, vassal, colony, dominion, crown land ve personal union üst devletin savaşına katılır; protectorate ve tributary katılmaz.

**Sınır:** Vanilla türlerde alt ülke "büyük güç" rütbesinde olamaz ve üst devlet daha yüksek rütbeli olmalıdır. Rütbeler açılışta prestijden hesaplanır; Atlas bunu önceden denetleyemez. Özellikle Moskova (Tatar koruması, 16 M) ve Burgonya (Paris puppet'ı) oyunda kontrol edilmeli.

Doğrulama ([verify.py](verify.py)): ağ aynı; bütün türler vanilla; özel tür dosyası yok; yalnız on koloninin türü değişti; ülke içerikleri ve uyarılar aynı. Etkinleştirme sonrası `check` 0 hata; siyasi denetim geçti; testler 123/123.
