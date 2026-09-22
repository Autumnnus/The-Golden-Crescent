# Siyasi haritanın etkin mod kurulumu

**22 Eylül 2026.** Kullanıcının yeni hedefi, ülke ve sınırları yalnız Atlas önizlemesinde değil, Victoria 3'ün 1836 başlangıcında görmektir. Bu nedenle `world/scenario.yml` etkin Atlas V2 kaynağıdır. 65 siyasi kartın 675 state sahipliği ve başlangıç diplomasisi buraya taşındı; Atlas'ın ürettiği `common/` ve `localization/` dosyaları elle düzenlenmez.

## Kapsam

- 675 kara state'inin sahipliği siyasi kartlarla aynıdır. 556 ülkenin başlangıçta toprağı ve nüfusu vardır.
- Oyun kurulumundaki yaklaşık 1,022 milyar vanilla nüfus, yeni siyasi sahiplere Atlas'ın province örtüşmesiyle aktarılır. Bu geçici taşıma, senaryonun nihai nüfus/kültür/din tasarımı değildir.
- Vanilla binaları oyun teknoloji koşullarıyla uyumlu olan 361 state'te korunur. 314 state'teki uyumsuz binalar, yanlış teknoloji veya kanun eklenmemesi için geçici olarak düşürülür. Bu siyasi harita sürümü ekonomik oynanış dengesi sunmaz.
- Şirket, kanun, teknoloji, ordu ve Flavor için senaryo profili eklenmedi. Eski vanilla ülke başlangıç verileri yalnız Atlas'ın üretilmiş tam history katmanında güvenle taşınabildikleri ölçüde kalır.

## Doğrulama

Mod kökünde:

```sh
python3 scripts/tools.py doctor
python3 scripts/tools.py atlas build
python3 scripts/tools.py atlas check
python3 scripts/tools.py atlas scenario report world/scenario.yml --out build/world-political/active-political-report.json
python3 scenarios/atlas/world_political/active_political_audit.py
```

`active_political_audit.py`, etkin kaynağın kart önizlemesiyle aynı ülke, sınır ve diplomasi kararlarını taşıdığını; bütün eyaletlerin ve kara sahibi ülkelerin nüfusu bulunduğunu; metadata'nın tam history klasörlerini değiştirdiğini denetler. Bu kontrol statiktir.

**23 Eylül oyun testi:** Kullanıcı yalnız The-Golden-Crescent'ı etkin tutan `Dev` oyun setiyle yeni oyunun siyasi dünya haritasını açtı; paylaştığı ekranda dünya sınırları çizilmişti ve kaba bir senaryo uyuşmazlığı bildirmedi. Başlatıcı veritabanı test anında `Dev` setini etkin gösteriyordu. Bu, siyasi haritanın motor içinde açıldığını doğrular; tek tek ülke oynanışı veya uzun süreli simülasyon testi değildir. İlk logda 183 başkent efektinin yanlış `s:STATE_...` sözdizimiyle yazıldığı görüldü. Ortak Atlas üreticisi kurulu vanilla `STATE_...` sözdizimine düzeltildi ve mod yeniden üretildi; bu başkent düzeltmesinin oyun içinde ayrıca tekrar gözlenmesi yararlı olacaktır. Aynı logda yeni ülkelerin varsayılan kanunlarına ilişkin 139 uyarı ve vanilla AI'nin Osmanlı-Mısır karşılaştırmasında artık topraksız olan `TUR` etiketine erişmesine ilişkin dört hata vardır. Bunlar sonraki hukuk/AI aşamasına kaydedildi; sınır verisini değiştirmez.

Siyasi kart üreticilerinin `catalog_vanilla.py` yardımcısı, aktif `world/` dosyalarını okumayan geçici boş bir mod üzerinden kurulu oyunun başlangıç sınırlarını alır. Böylece etkin harita daha sonra değişse de kart 63 ve karar defteri aynı doğrulanmış temelden tekrar üretilebilir.

## Sonraki motor denetimleri

Vanilla'nın Atlas'ın değiştirdiği yedi history klasörü dışındaki karakter, AI, global başlangıç, journal ve event dosyaları hâlâ eski ülkeleri anabilir. Tek modla yapılan açılışta sınır çizimi başarılıydı. Başka modlarla açılan oyunun logları bu modun motor doğrulaması sayılmaz. İleride bulunan somut çökme veya sınır hataları siyasi kurulum kapsamında düzeltilir; ekonomi ve kanun dengesi daha sonraki aşamada ele alınır.
