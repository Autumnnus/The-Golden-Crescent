# Demografi 27 — Batı Avrupa

Bu paket [yazılı atlasın](../../../docs/scenario/dunya_atlasi.md) Avrupa düzenini nüfusa uygular: altı bağımsız Fransız devleti, Bavyera tacı altındaki fakat onun tabiisi olmayan Alman prenslikleri (Prusya birleşmesi yok), Bohemya, Avusturya, Alçak Ülkeler, İsviçre ve Kalmar taçları. **47 ülkenin 84 doğrudan payı** etkin Atlas kaynağına işlendi; sınır, bağlılık, kanun ve bina değişmedi. Batı Avrupa teknik bölgesinde açık pay kalmadı. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Kararlar

- Devralınan Avrupa nüfusu yazılı tasarımla uyumludur (sömürgeci yerleşimci kalıntısı yoktur); ölçek ve ortak kültür–din grupları korunur. Payların toplamı 81.770.952 → 81.770.700 (yuvarlama).
- **Okuryazarlık**, "geciken Avrupa" kanonuna göre farklılaştırıldı: Kalmar taçları %45–48 (İzlanda %55), Hamburg/Bremen/Lübeck ve Frankfurt %44–45, Saksonya ve Thüringen düklükleri %40, İsviçre ve Hollanda %42–45, Brandenburg/Hannover/Ren kentleri %36, Bavyera ve Bohemya %30, Avusturya %28, Paris %31, Burgonya %30–34, Provence %24, Akitanya %20, Oksitanya %18, Bretonya %14. Bunlar Faz 05'teki İngiltere (%30–38) ve Faz 06'daki Lehistan (%32–40) hedefleriyle tutarlıdır.
- **Dar karışım düzeltmeleri:**
  - Alsas'ta vanilla'nın %65 Protestan Alemanik çoğunluğu Katolik çoğunluğa (%56) çevrildi.
  - Nantes Fermanı'nın iptali yaşanmadığı için Poitou/La Rochelle'de (%6,5) ve Cévennes/Languedoc'ta (%10) Huguenot toplulukları büyüdü.
  - İslam dünyasının ticaret ağırlığı küçük tüccar toplulukları olarak yansıtıldı: Marsilya, Bordeaux, Paris, Amsterdam ve Hamburg'da Mağribi, Endülüslü, Rûm ve Levantenli topluluklar (payın %0,5–5'i).
- **Homeland:** Devralınan yerel homeland'ler eşiksiz korundu; yalnız ≥%10 kültürler eklendi (ör. Flandre'ye `wallonian`, Tirol'e `alemannic`, Provence'a `north_italian`).

[89 yerleşim profili](city-profiles.yml) 1836 için tasarım tahminleridir: geciken Avrupa nedeniyle gerçek tarihten hafifçe küçük (Paris 800 bin, Viyana 300 bin, Amsterdam 190 bin). Berlin, Prusya devleti olmayan bir Brandenburg merkezi olarak 170 bindir. Hepsi state nüfusunun içindedir; ek POP veya bina üretmez.

## Doğrulama

Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/west-europe-verification.json), etkin Atlas `build/check` (**0 hata; 25 uyarı**), siyasi denetim ve 38 araç öz testi geçti; önizleme 0 sınır değişikliği gösterir. Motor testi yapılmadı. Avrupa devletlerinin malikâne/lonca/serflik kurumları ve Bavyera imparatorluk düzeni hukuk aşamasına kalır.

Yeniden üretim: `west-europe-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `snapshot.py` → `prepare.py` → `scenario validate/build --out build/scenarios/west-europe-candidate` → `verify.py`.
