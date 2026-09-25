# M0 — Açılış logu temizliği

24 Eylül 2026 ilk oyun testindeki ~640 script hatasının kaynağına göre iki bölüm:

## Atlas kaynağındaki düzeltmeler ([prepare.py](prepare.py))

- **Bina sahipliği (132 kayıt):** Atlas vanilla sahipliği yeni ülkeye çevirirken eski sahibin başkent bölgesini koruyordu (ör. Burgonya binaları Île-de-France'a, Tatar hanlığınınkiler Ingria'ya bağlı). Bu kayıtlar aynı seviye ve üretim yöntemleriyle yerel kendi/devlet sahipliğine çevrildi. Aynı sahibin teknolojisine uymayan kayıtları da düzeltildi. Teknolojisi olmayan 4 seviye (ör. Aşanti limanı) kaldırıldı.
- **GBR ordusu:** Bu evrende GBR yalnız Londra tacının denizaşırı bağımlılıklarıdır; Avrupa karargâhlı vanilla ordu ve donanması boşaltıldı.
- **Bağımlılık isteği:** Artık tabi olmayan 8 ülkenin (IQU, KZH, NPU, OZH, SEQ, SER, UZH, WAL) devralınmış `add_liberty_desire` kayıtları diplomasi sıfırlamasıyla kaldırıldı. Sıfırlamanın götürdüğü üç ilişki açıkça geri yazıldı: Boğdan–Eflak +50, Karadağ–Sırbistan +30, Eflak–Sırbistan +20.

[verify.py](verify.py) hata kaynaklarının kalktığını ve nüfusun korunduğunu denetler. Uyarılar **27 → 14**, bina seviyesi 10.254 → 10.250.

## Vanilla dosya override'ları

[Çalışma zamanı temizliği](../../runtime_cleanup/README.md) bölümüne bakın.

## Açık kalanlar

- Avusturya'nın Lemberg ve Mısır'ın Suriye ordusu artık sahip olmadıkları bölgelerde karargâh arıyor (~10 hata). Atlas'ın `replace` modu vanilla generallerini taşımadığı için dokunulmadı.
- Bu üç sorun (bina sahipliği bölgesi, sahipsiz karargâh, tabisi olmayan ülkeye liberty desire) Atlas'ın genel hatalarıdır ve araç reposunda düzeltilmelidir. Araç reposunda başka bir çalışmanın commit edilmemiş değişiklikleri bulunduğu için bu turda araç koduna dokunulmadı.
