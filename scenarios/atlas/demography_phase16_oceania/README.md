# Demografi 16 — Avustralya, Aotearoa ve Pasifik

Bu dilim [yazılı atlasın](../../../docs/scenario/dunya_atlasi.md) yerel egemenlik kararını nüfusa uygular. **20 state'te 37 ayrı ülkenin 56 doğrudan payı** etkin Atlas kaynağına işlendi; 22 kurulu hub için state içi yerleşim profili hazırlandı. Eski sömürge tarihinden gelen büyük yerleşimci POP çoğunlukları, Avustralya'daki yerel siyasi haritayla çelişiyordu. Bu dilim onları yerel nüfusa çevirirken küçük ticaret topluluklarını korur. Nüfus, okuryazarlık ve ortak kültür–din kararları [planda](plan.yml), uygulama öncesi POP grupları [dondurulmuş kaynakta](source-pops.json) bulunur.

**Tek siyasi düzeltme:** Kurulu `STATE_TONGA` içinde `Tafuna` ile `Apia`/`Salelologa` adlı hub'ları taşıyan `xA7F8A1` ve `xC00010` province'leri yazılı senaryodaki bağımsız Samoa'ya ayrıldı. `x208030` ile `xD98CDA` Tonga'da kaldı. Yeni `VSM` (Samoa Meclisi) yerel, `polynesian/animist`, bağımsız ve merkezi aynı oyun state'indedir; yeni bir subject/koloni ilişkisi yaratılmaz. [Siyasi hazırlama betiği](political.py) yalnız bu iki province ve bu ülke tanımını ekler. İki ülkenin doğrudan nüfusu ayrı ayrı **30.000** kişidir. Samoa'nın ayrı state bölgesi bulunmadığından Tonga ile kaynak/arable land sınırını paylaşır. `STATE_TONGA`nın şehir hub'ı Nuku'alofa Tonga payındadır; Samoa'nın capital state kaydı statik olarak geçse de başkent işareti/ülke seçimi bu bölünmüş state için oyun içinde ayrıca sınanmalıdır.

| Alan | Önce | Etkin başlangıç |
|---|---:|---:|
| Avustralya'daki `aborigine` POP'lar | 531.910 | 799.833 |
| Aynı yedi state'te Australian/Irish/Scottish POP'lar | 274.208 | 18.667 |
| Tasmania'daki Palawa oyun karşılığı `aborigine/animist` | 200 | 41.160 |
| Hawaii'deki Han/Confucian POP | 50.000 | 1.987 |
| Tonga + Samoa | 40.000, tek ülke | 60.000, iki ülke |
| Okyanusya kapsamındaki toplam | 1.766.315 | 1.825.800 |

Hawaii'nin yerel inanç çoğunluğu ile Protestan saray dinini ayrı tutuyoruz; küçük yabancı din adamı/sermayedar meslekleri ve tüccarlar korundu. Kuzey Ada'da `UNT` Māori/Protestan çoğunluğu, sömürge egemenliği olmadan gelişen yerel dinî tercihi yansıtacak daha küçük bir paya (%30) indirildi. Tahiti'nin resmî Protestan tanımı ile büyük yerel inanç çoğunluğu da tek tip halk dini değildir. `aborigine`, `melanesian` ve `polynesian` kurulu oyunun geniş kültür karşılıklarıdır; Palawa, Samoa ve ada içi toplulukları ayrı kültür ID'leriyle tam temsil etmezler.

[22 hub profili](city-profiles.yml) yeni POP veya bina değildir; kurulu Türkçe hub adının bağlı olduğu siyasi province'deki nüfusun tasarım alt kümesidir. Sydney, Melbourne, Hobart, Perth, Auckland gibi adlar oyunun devralınmış yer adlarıdır: bu alternatif dünyada aynı adların nasıl oluştuğu ayrıca yerelleştirme incelemesi gerektirir. Profiller bu adları yeni tarihsel kanon olarak dayatmaz.

Başlangıç nüfusu **1.091.357.323 → 1.091.416.808** oldu. [Okyanusya önizlemesinde](../../../build/maps/oceania-demography.html) yalnız Tonga/Samoa state'i siyasi olarak değişir. `verify.py` önceki etkin dünya ile dar Samoa düzeltmesini, ardından adayla siyasi kaynak arasındaki tüm diğer ülke/state/diplomasi alanlarını, hedef dışı POP'ları, hedef nüfus/meslekleri ve hub sahiplerini karşılaştırır. Atlas 675 state, 557 kara sahibi ülke için **0 hata, önceki 25 uyarı** verdi. Araç öz testi 38/38 geçti. Bu yeni nüfus ve Samoa sınırı oyun motorunda henüz açılarak sınanmadı; okuryazarlık oyunun ilk gün hesabında değişebilir. Ekonomi, kanun ve ülke içi kurum dengesi sonraki aşamadır.

Yeniden üretim için uygulama öncesi dondurulmuş `build/demography/oceania-source.yml` gerekir; mevcut etkin dünyadan `political.py` ile yeniden başlangıç almak çift Samoa eklemesini bilinçli olarak reddeder. `snapshot.py` da [dondurulmuş POP kaydını](source-pops.json) üzerine yazmaz. Hazırlanan aday `prepare.py` ile, statik sonuç `verify.py` ile denetlenir; etkin oyun dosyaları yalnız Atlas `build` ile yazılır.
