# Demografi 18 — Sahel ve Batı Afrika

Bu paket [Afrika tasarımındaki](../../../docs/scenario/senaryo_afrika.md) ayrı Sahel ve kıyı devletlerini koruyarak **23 state, 41 ülke ve 56 doğrudan state–ülke payını** etkin Atlas kaynağına işler. `ADG`, `ADR`, `AJJ`, `BOR`, `FTR`, `OUA`, `RGB`, `SOK`, `TBI` ve `WAD` için [planda](plan.yml) yazan ülke toplamları **yalnız bu paketteki payları** kapsar; diğer state payları değiştirilmez.

Bu payların toplam nüfusu **21.564.133 → 22.264.600** kişidir. Dünya toplamı **1.092.325.693** olur. Nüfus hedefleri mevcut kaynağa göre yaklaşık %2–4 artar; büyük bir göç veya sanayi patlaması varsayılmaz. Sokoto/Hausa ve Bornu kent ağları, Massina–Timbuktu ilim/ticaret hattı ve Aşanti/Futa Jallon merkezleri daha yüksek okuryazarlık girdisi alır. Segu, kıyı ve otlak topluluklarına ayrı girdiler verilir. Bunlar oyun motorunun ilk gün hesapladığı kesin eğitim oranları değildir.

[Dondurulmuş kaynak POP'larındaki](source-pops.json) ortak kültür–din grupları korunur: örneğin Segu çevresindeki Bambara/yerel inanç ve Mande/Müslüman toplulukları, Hausa kuşağındaki Müslüman ve yerel inanç toplulukları, Gine kıyısındaki küçük Hristiyan cemaatler birlikte kalır. Ülke birincil kültürleri, resmî dinleri, siyasi sınırlar ve diplomasi değiştirilmez. Kaynaktaki **1.635.092 açık köle mesleği** aynı kişi sayısıyla korunur; ilgili ülkelerin mevcut raporunda köleliğe izin veren kanunlar vardır. Emek rejimi ve istihdam dengesinin nihai kabulü ayrı ekonomi/kanun incelemesine bağlıdır.

[23 yerleşim profili](city-profiles.yml) Ségou, Bamako, Timbuktu, Agadez, Saint-Louis, Sokoto, Kano, Kumasi, Lagos ve diğer merkezlerin state nüfusu **içindeki** tasarım alt kümeleridir. Kurulu oyunun Türkçe hub etiketleri ve hub province sahipliği doğrulanmıştır. Örneğin oyunda Timbuktu `farm`, Kano `mine` hub'ıdır; profil bu teknik sınıflandırmayı bina veya ek nüfus talimatına çevirmiyor.

Önizleme: [Sahel–Batı Afrika atlası](../../../build/maps/sahel-west-africa-demography.html). Aday `scenario validate/build` geçti; [doğrulama](../../../build/demography/sahel-west-africa-verification.json) hedef dışı POP, ülke, state ve diplomasinin korunmasını denetledi. Etkin Atlas `build/check` **0 hata, önceki 25 uyarı**, siyasi denetim ve 38 araç öz testi geçti. Bu dilim için yeni oyun motoru testi yapılmadı.

Güncel dünya kapsama sayısı için mod kökünden `python3 scripts/demography_progress.py` çalıştırılır. Bu sayı yalnız açık state–ülke POP planlarını sayar; bütün bölgenin ekonomi, yasa veya motor davranışı tamamlandı anlamına gelmez.
