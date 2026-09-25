# Demografi 19 — Nil, Afrika Boynuzu ve Doğu Afrika

Bu paket [Afrika senaryosundaki](../../../docs/scenario/senaryo_afrika.md) bağımsız Sennaar, Darfur, Vaday, Habeş yaylası, Somali kıyısı, Büyük Göller ve Umman–Zanzibar ilişkilerini koruyarak **16 state'te 54 ülkenin 57 doğrudan state–ülke payını** etkin Atlas kaynağına işler. `BOR`, `OMA` ve `WAD` için [planda](plan.yml) yazan hedefler yalnız bu paketteki paylardır; önceki bölgelerdeki nüfusları korunur.

Paket nüfusu **17.468.905 → 18.081.400** kişiye çıkar; dünya toplamı **1.092.938.188** olur. Sennaar/Hartum, Habeş kentleri ve Svahili kıyısı ile göl ve otlak toplulukları aynı okuryazarlık girdisini almaz. Eyalet–ülke girdisi her POP grubuna uygulandığı için şehir/kır veya özgür/köle eğitim eşitsizliğinin tamamını ifade etmez; motorun ilk gün okuryazarlığını da garanti etmez.

Kaynakta birlikte bulunan Sünni, İbadi, Şii, Ortodoks, Yahudi ve yerel inanç POP'ları korunur. **Dar kültür düzeltmesi:** Gonder, Amhara ve Oromia'daki `kikuyu/animist/slaves` olarak yazılmış **298.711 kişi**, aynı din, meslek ve sayıyla ilgili paylarda Oromo veya Sidama olarak işaretlendi. Kenya ve Rift Valley'deki Kikuyu POP'ları değişmedi. Bu, her yerel topluluğu eksiksiz temsil eden yeni bir kültür envanteri değildir.

Kaynağın **1.260.340 açık köle mesleği** korunur. Sennaar `VSN` payında 228.000 köle meslekli kişi olmasına rağmen ülkenin açık başlangıç kölelik kanunu yoktu; kurulu oyunun `law_debt_slavery` kanunu eklendi. Diğer ülke kanunları, siyasi sınırlar ve diplomasi değişmedi. Kanunun ve mesleklerin oyun içi emek/istihdam sonuçları ayrıca test edilmelidir.

[27 yerleşim profili](city-profiles.yml) Massava, Hartum, Gonder, Muqdisho, Mombasa, Kampala, Zanzibar ve diğer merkezlerin kendi state–ülke nüfusları **içindeki** tasarım alt kümeleridir. Türkçe hub adı ve province sahibi kurulu oyundan doğrulandı; bu dosya yeni POP veya bina üretmez.

[Önizleme](../../../build/maps/nile-horn-east-africa-demography.html) sınır değişikliği göstermez. Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/nile-horn-east-africa-verification.json), etkin Atlas `build/check` (**0 hata, önceki 25 uyarı**), siyasi denetim ve 38 araç öz testi geçti. Bu dilim için yeni motor testi yapılmadı. Güncel sayısal kapsam: `python3 scripts/demography_progress.py`.
