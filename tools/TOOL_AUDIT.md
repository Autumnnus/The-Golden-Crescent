# Atlas ve senaryo derleyicisi denetimi

12 Eylül 2026. İncelenen yerel oyun: Victoria 3 **1.13.11**, `15aa89ae4`.

**Sonuç:** Araçta gerçek veri kaybı ve doğrulama eksikleri vardı; aşağıdaki sorunlar düzeltildi. Üretilen başlangıç dosyaları kurulu oyunun script/veri dosyalarıyla karşılaştırıldı. Bu, kapalı kaynak oyun motorunun çalıştırıldığı veya her senaryonun çökmeden açılacağının kanıtlandığı anlamına gelmez.

## Bulunan ve düzeltilen sorunlar

| Sorun | Düzeltme ve kontrol |
|---|---|
| Kapanmamış tırnak kabul ediliyor; ters eğik çizgi ve `"<3"` gibi alıntılı değerler yazılırken değişebiliyordu. | Parser hatalı metni reddediyor, mevcut alıntılı değerlerin yazımını koruyor. Boşluklu `hsv {}` blokları doğru türde okunuyor. |
| Birden fazla `add_ownership` bloğu olan binanın yalnız son sahipliği sayılıyordu. | Tüm sahiplik blokları toplanıp orantılı ölçekleniyor. Gerçek New Castile/Old Castile örnekleriyle saptandı. |
| Yalnız bina seviyesi değiştirilince mevcut üretim yöntemleri ve sahiplik yapısı kaybolabiliyordu. | Seviye değişikliği mevcut yapıyı koruyor; açık sahiplik/PM tercihi ayrıca uygulanıyor. Eksik PM grupları tamamlanıyor. |
| Teknolojiler şirket gibi bunlara bağlı başlangıç işlemlerinden sonra yazılıyordu. | Teknoloji öncülleri sıraya konuyor ve diğer işlemlerden önce veriliyor. Döngülü bağımlılık reddediliyor. |
| Değiştirilen kanunlar devralınan kurum işlemlerinden sonra yürüyebiliyordu. | Önce teknoloji, ardından kanunlar, ardından kalan başlangıç işlemleri yazılıyor. |
| Harita/kanun değişince devralınmış şirket merkezi ve kurum seviyesi geçersiz kalabiliyordu. | Kaybedilen şirket merkezi ve etkinleştiren kanunu kalmayan pozitif kurum seviyesi hata veriyor. |
| Yeni formasyonun karargâh bölgesinde ülkenin toprağı olmayabiliyordu. | Yeni karargâh için sahiplik kontrolü eklendi. Ülke türünün askerî yeteneği gerçek kaynak tanımından okunuyor. |
| Özel bağlılık türünün izin verdiği ülke sınıfları yeterince doğrulanmıyordu. | Gerçek `country_types` kataloğu kullanılıyor. Kimlik çakışması, bozuk diplomatik alan ve yinelenen pact reddediliyor. |
| Desteklenmeyen history kökleri sessizce atılabiliyordu. | Derleyici tanımadığı kök/global kayıtla karşılaşırsa veri kaybetmek yerine duruyor. Eski parçalı YAML kaynaklarında da yinelenen anahtar reddediliyor. |
| V2 `check`, gerçekten diske yazılmış dosyaların eski/elle değiştirilmiş olmasını kaçırabiliyordu. | Beklenen çıktı yeniden hesaplanıp gerçek baytlarla karşılaştırılıyor. Eksik, değişmiş ve artık kullanılmayan dosyalar ile yanlış `replace_paths` raporlanıyor. |
| Yazma hatasında önceki üretilmiş dosyalar silinmiş kalabiliyordu. | Yazım öncesi dosyalar ve metadata saklanıyor; yakalanan hata durumunda geri yükleniyor. İkinci yazımda simüle edilen disk hatasıyla test edildi. |
| Oyun güncellemesinden sonra eski indeks kullanılabiliyordu. | İlgili kaynak yolları, boyutları ve zaman damgaları değişince yeni süreçte indeks yenileniyor. |
| Selftest son iki saatteki her değişikliği araca mal ediyordu. | Test başlangıcı/sonu karşılaştırılıyor. Önceden oluşmuş Finder `.DS_Store` dosyası artık hatalı alarm üretmiyor. Oyun dosyası silinmedi veya değiştirilmedi. |

## Önemli anlam düzeltmesi: okuryazarlık

Vanilla `common/scripted_effects/00_starting_pop_literacy.txt` ve `00_starting_pop_wealth.txt`, değerlerin oyun hazırlığında yeniden hesaplandığını açıkça belirtiyor. Bu nedenle **%65 girdisi, oyun ekranında tam %65 garantisi değildir**. Önceki kesinlik ifadesi fazla güçlüydü; atlas etiketi, rapor ve LLM rehberi düzeltildi.

Nüfus sayıları ve kültür/din bileşimi üretilen dosyalarda kişi hassasiyetinde hesaplanır. Kesirler tam kişiye yuvarlanırken toplam korunur. Sonraki oyun simülasyonunda nüfus, servet, istihdam ve kültür/din dağılımı değişebilir.

## Fransa örneği ve genel bağlılık desteği

Fransa'ya özel otomatik vasallık eklenmiyor. Kullanıcıya sunulan sanayi dönüşümü örneğinden Fransa/Brittany vasallık değişiklikleri çıkarıldı. Bu örnek artık diplomasiye müdahale etmiyor.

Özel türler yalnız senaryodaki `subject_types` tanımından üretilir; kurulu oyunun subject type ve diplomatic action dosyaları birlikte temel alınır. Eski örnek yalnız regresyon testi fixture'ında tutuldu. BIC paylarının çok sayıda yeni ülkeye dağıtılması ve iç içe bağlılıklar da test kapsamındadır. Hiçbir fixture etkin `world/` senaryosu yapılmadı.

## Doğrulama kapsamı

- **1.278 gerçek oyun dosyası:** parse → serialize → parse karşılaştırmasında AST eşitliği korundu; hata yok. Kapsam: history, country definitions, subject types, diplomatic actions, buildings, production methods, technology ve scripted effects. Sonuç: `build/audit/source_roundtrip.json`.
- **62 Python testi:** parser, nüfus/ekonomi, şirketler, teknoloji/kanun sırası, diplomasi, hatalı girdiler, salt okunur önizleme, çıktı bütünlüğü, geri yükleme, atlas ve başlatıcı. Sonuç: `build/audit/full_tests.log`.
- **38 selftest kontrolü:** üretim, temizlik, replace paths, harita kuralları, atlas regresyonları ve kurulumdaki common/map_data/localization dosyalarının test süresince değişmemesi. Sonuç: `build/audit/selftest.log`. Bu toplam, ayrıca çalıştırılan atlas testleriyle kısmen örtüşür.
- Tarayıcı regresyonları: V1 harita seçimi/düzenleme, undo/redo, JSON/PNG dışa aktarma, hatalı import; V2 ekonomik panel, alanların korunması, düzenleme sonrası eski raporun geçersizleştirilmesi ve geri alma. Sunucusuz `file://` üzerinden çalışır.
- Mac başlatıcısının mevcut harita ve YAML senaryo önizlemesi, hatalı dosya yolu ve kontrol akışı ayrıca sınanır. Windows `.bat` dosyası bu Mac ortamında çalıştırılmadı.

Yerel kanıt dosyaları `build/audit/`, tarayıcı çıktıları `build/atlas-tests/` altında bulunur; `build/` Git'e eklenmez. Tekrar çalıştırma komutları aşağıdadır.

## Hâlâ oyun motorunda sınanması gerekenler

1. **Yeni oyun başlangıcı:** Bu denetimde üretilen V2 senaryoyla oyun başlatılmadı. `validation: passed` yalnız statik kontrollerdir; rapor ayrıca `validation_scope: static_source` ve `runtime_tested: false` taşır.
2. **Karakterler ve olaylar:** Karakter history'si, journal, on_action ve event içerikleri yeniden kurulmaz. Silinen/değişen ülke veya formasyon, bu içeriklerin scope varsayımlarını başlangıçta bile bozabilir. Özellikle BIC gibi bir ülkenin kaldırıldığı senaryoda ilgili içerikleri ayrıca incelemek gerekir.
3. **Dinamik koşullar:** Şirket possible/attainable, DLC koşulları, tüm diplomatik trigger'lar, kurumların dinamik üst sınırları ve tam oyun ekonomisi çalıştırılmaz. GDP, gerçek işe alım, fiyatlar ve kesin IG clout tahmin edilmez.
4. **Özel bağlılığın ileriki davranışı:** Başlangıç pact'ı üretmek, özel diplomatik oyun/sway arayüzü ve bütün özerklik geçişlerini tasarlamakla aynı kapsam değildir. Gereken davranış senaryoya göre ayrıca geliştirilir.
5. **Yazımın kesilmesi:** Geri yükleme yakalanan Python/yazım hatalarına karşı korur; güç kesilmesi, zorla süreç öldürme veya geri yüklemeyi de engelleyen disk arızası için işlemsel garanti verilmez.
6. **İndeks ve kapsama:** İndeks önbelleği metadata değişimini izler; aynı boyut ve zaman damgası korunarak yapılan haricî değişiklikte `index` komutuyla elle yenile. Kaynak karşılaştırması ve graph kapsam kontrolü motorun bütün davranışlarının kanıtı değildir.

Aktif senaryo için son doğrulama: kaynağı derle, `check` çalıştır, Victoria 3'te yeni oyun başlat, birkaç gün ilerlet ve o çalıştırmanın hata/çökme günlüklerini incele. Eski günlükte hata olmaması yeni senaryonun doğrulandığı anlamına gelmez.

## Kullanım ve tekrar test

Günlük kullanım: [kısa Türkçe rehber](../ATLAS_KISA_REHBER.md). Mac'te `Atlas.command`, Windows'ta `Atlas.bat`; terminalde `./Atlas.sh`. Sunucu açmak gerekmez. LLM çalışma sözleşmesi: [LLM_SCENARIO_WORKFLOW.md](LLM_SCENARIO_WORKFLOW.md).

```sh
PYTHONPATH=tools .venv/bin/python -m unittest tools/test_tool_audit.py tools/test_scenario.py tools/test_atlas.py -q
.venv/bin/python tools/tgc.py selftest
./Atlas.sh --check
./Atlas.sh tools/examples/ve_industrial_reversal.yml --no-browser

# Tarayıcı testleri için önce iki fixture atlasını hazırla:
.venv/bin/python tools/tgc.py atlas --region 08_middle_east --scenario tools/examples/ve_atlas_scenario.yml --out build/maps/ve_demo.html
.venv/bin/python tools/tgc.py atlas --scenario tools/tests/fixtures/ve_subjects_regression.yml --out build/maps/ve_subjects_regression.html --width 3200
# Node + Playwright gerekir; TGC_CHROME kurulu Chrome yolunu seçebilir.
node tools/test_atlas_browser.cjs
node tools/test_scenario_browser.cjs
```

`selftest` geçici `world/*/t_selftest.yml` dosyaları ve üretilen çıktı üzerinde çalışır; aynı anda başka derleme/düzenleme başlatma. Mevcut senaryo veya üretilmiş dosyalardaki elle yapılmış değişiklikleri testten önce sürüm kontrolüne al. Gündelik inceleme için menüdeki **3 — Kontrol** yeterlidir.
