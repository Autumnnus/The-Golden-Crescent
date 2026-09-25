# Demografi 20 — Orta ve Güney Afrika'nın kalan payları

Bu paket [Afrika tasarımındaki](../../../docs/scenario/senaryo_afrika.md) ayrı Kongo/Loango, Luba–Lunda, Merina, Mozambik, Zulu, Xhosa, Tswana, Basotho ve güneybatı yönetimlerini koruyarak **30 state'te 47 ülkenin 72 doğrudan state–ülke payını** etkin Atlas kaynağına işler. `SOK` hedefi yalnız Kuzey Kamerun'daki kısmi payıdır. Bölge toplamı **18.989.854 → 19.602.700** kişi, dünya toplamı **1.093.551.034** kişi olur.

## Önceki siyasi kalıntının düzeltilmesi

Yazılı senaryo Boer cumhuriyetleri ve Cape Kolonisi kurmazken eski siyasi kaynak `ORA` ve `TRN` etiketlerini iki küçük toprak payında bırakmıştı. [Dar siyasi düzeltme](political.py), `STATE_VRYSTAAT` içindeki 17 Oranje province'ini Basotho `BST` yönetimine, `STATE_TRANSVAAL` içindeki 11 Boer Transvaal province'ini Ndebele `MTB` yönetimine aktarır. Dört güney state'inden Boer homeland kaldırılır. İki state'in nüfusu ve dünya nüfusu değişmez, diplomasi aynı kalır; kara sahibi ülke sayısı **557 → 555** olur. [Değişiklik haritası](../../../build/maps/south-africa-political-correction.png) iki state'i gösterir.

Eski `TRN` bölgesindeki **5 bina seviyesi**, yeni sahibi `MTB` oyunda decentralised olduğu için Atlas'ın kaynak kuralıyla düşer. Bu ekonomik etki gizlenmez; Ndebele'nin devlet tipi ve yerel tarım/askerî bina planı ayrı ekonomi aşamasında incelenecek. Yeni siyasi düzeltme henüz oyun motorunda sınanmadı.

## Nüfus ve yerleşimler

Mevcut ortak kültür–din grupları, küçük Hristiyan ve Müslüman topluluklar ve **969.842 açık köle mesleği** korunur. Dört güney payında sömürge devrinden kalmış aşırı Britanyalı/Boer başlangıç oranı ayrıca düzeltilir: Cape/Khoi, Doğu Cape/Xhosa, Kuzey Cape/Tswana ve Transorangia/Basotho paylarında bu iki grubun toplamı **220.108 → 27.632** olur. Yerel Protestan Griqua/Khoisan toplulukları ve küçük yabancı ticari/yerleşik topluluklar kalır. Bu, 1836 alternatif başlangıç nüfusunun yeniden yazımıdır; oyun içinde gerçekleşmiş bir göç olarak sunulmaz. Diğer payların ortak kültür–din grupları ve meslekleri korunur.

[37 yerleşim profili](city-profiles.yml) Tananarive, Kinshasa, Luanda, Ulundi, Maputo ve başka merkezlerin state nüfusu **içindeki** tasarım alt kümeleridir; ek POP veya bina üretmez. Kurulu oyundaki `Pretoria`, `Bloemfontein`, `Johannesburg` ve bazı Cape hub adları bu evren için anakronik olabilir. Kesin alternatif ad ve yerelleştirme kararı verilmeden bu hub'lara yeni profil yazılmadı; oyundaki görünen adları bu paket değiştirmez.

[Bölgesel önizleme](../../../build/maps/central-southern-africa-demography.html), aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/central-southern-africa-verification.json), etkin Atlas `build/check` (**0 hata; önceki 25 uyarı**), siyasi denetim ve 38 araç öz testi geçti. Bu rakamlar nüfus girdileridir; oyun motorunun istihdam, hukuk ve okuryazarlık sonucu ayrıca değerlendirilmelidir. Güncel dünya kapsamı: `python3 scripts/demography_progress.py`.
