# LLM ile tam başlangıç dünyası oluşturma

Bu modda kullanıcı hikâyeyi anlatır; LLM gerçek oyun kimliklerini sorgular, **version: 2** YAML/JSON senaryosunu yazar, derler ve raporunu inceler. Atlas görsel kontrol ve küçük sınır düzeltmeleri içindir. API anahtarı veya belirli bir LLM sağlayıcısı gerekmez.

## Zorunlu çalışma sırası

1. Kullanıcının hikâyesini ülke, sınır, ekonomi, toplum, askerî ve diplomatik başlangıç kararlarına çevir. Belirtilmeyen ayrıntılar için tutarlı varsayımlar yap ve senaryo açıklamasına yaz. Örnekleri bütün dünyayı dengelemiş hazır senaryolar sanma.
2. `catalog`, `find`, `show` ile gerçek eyalet/il/sahiplik verisini; `rules` ile kurulu oyunun mekaniklerini al. Kimlik, üretim yöntemi veya vasallık türü uydurma.
3. Tek bir `scenario.yml` veya `scenario.json` üret. Nüfus ve okuryazarlık, teknoloji, kanunlar, şirketler, binalar/üretim yöntemleri ve ordu birlikte tutarlı olmalı. Önce yalnızca haritayı boyayıp diğer mekanikleri vanilla bırakma.
4. `scenario validate` hatalarını düzelt. `scenario report --country TAG` ile değişen her önemli ülkeyi incele. İşgücü/altyapı notlarını değerlendir; sadece sıfır hata elde etmek dengeleme değildir.
5. `scenario build` ile ayrı bir çıktı klasörü oluştur; atlas ve değişiklik haritasını üret. Bu adımlar etkin modu değiştirmez. Girdi, mevcut `world/` üzerine uygulanır.
6. Kullanıcının mod geliştirme talebi kapsamında senaryoyu etkinleştireceksen tek kaynak olarak `world/scenario.yml` içine koy; `build` ve `check` çalıştır. Aynı ülke/eyaleti eski parçalı YAML'ler ile iki yerde farklı biçimde yönetme. Üretilen dosyaları elle düzenleme. Tam history katmanlarının yanında elle yazılmış çalıştırılabilir history dosyaları varsa aktif build çift yürütmeyi önlemek için hata verir; bu başlangıç değişikliklerini önce senaryo kaynağına taşı.
7. Kullanıcıya seçilen varsayımları, önemli önce/sonra farklarını ve test sonuçlarını anlat. Oyun motorunda sınamadığın sonuçlara “oyunda doğrulandı” deme.

```bash
.venv/bin/python tools/tgc.py catalog --region EGY,FRA --out build/scenario-context.json
.venv/bin/python tools/tgc.py rules                        # kategori ve adetler
.venv/bin/python tools/tgc.py rules --kind buildings --query textile --script
.venv/bin/python tools/tgc.py rules --kind laws --query schools --script
.venv/bin/python tools/tgc.py rules --kind technologies --query corporate --script
.venv/bin/python tools/tgc.py scenario schema --out build/scenario.schema.json
.venv/bin/python tools/tgc.py scenario validate scenario.yml
.venv/bin/python tools/tgc.py scenario report scenario.yml --country EGY --out build/egy-report.json
.venv/bin/python tools/tgc.py scenario build scenario.yml --out build/scenarios/my-world
.venv/bin/python tools/tgc.py atlas --scenario scenario.yml --out build/maps/my-world.html
.venv/bin/python tools/tgc.py map --scenario scenario.yml --mode changes --data
# world/scenario.yml etkin kaynak olduktan sonra:
.venv/bin/python tools/tgc.py build
.venv/bin/python tools/tgc.py check
```

`rules` sonuçları sayfalanır: `--limit 30 --offset 30`; `next_offset` bitene kadar devam et. `--script` tam kaynak düğümünü verir. Şema yapısal yardımcıdır; gerçek kimlik, oran, sahiplik, bağımlılık ve kaynak doğrulaması `scenario validate` içindedir. `scenario build` çıktısı üretilen başlangıç katmanları ve metadata'dır; modun elle yazılmış diğer içeriklerini kopyalayan bir dağıtım paketi değildir.

## Version 2 sözleşmesi

Üst alanlar: `version`, `title`, `description`, `countries`, `states`, `subject_types`, `diplomacy`. YAML'de yinelenen anahtarlar hata verir. Version 1 harita taslakları desteklenir; tam başlangıç mekanikleri için version 2 kullan.

Ülkede belirtilmeyen temel özellikler vanilla/mevcut dünyadan gelir. Örneğin yalnızca Mısır'ın nüfusunu değiştirmen onun `unrecognized` sınıfını değiştirmez. Yeni ülkede ad, renk, kültür, din, sınıf, tier ve sahip olduğu başkenti tanımla. `cultures` ülkenin birincil kültürleridir, `religion` resmî dinidir; nüfus dağılımını **population** ile ayrıca belirle.

Bir eyalete yalnızca `population` / `industry` / `homelands` / `claims` / `state_type` yazabilirsin; bu durumda sınırlar korunur. `owner` veya `split` yazarsan eyaletin sahiplik planını değiştirirsin. `homelands: []` ve `claims: []` ilgili listeyi temizler. Yeni kültür karışımı kendiliğinden homeland veya claim oluşturmaz. `state_type: incorporated|unincorporated` incorporation başlangıcını değiştirebilir. Bölünmüş eyalette `population.by_owner` ve `industry.by_owner` gerçek sahip etiketlerini kullanır.

### Nüfus, okuryazarlık, din ve kültür

```yaml
version: 2
countries:
  EGY:
    population:
      scale: 1.25       # başlangıç nüfusunu büyüt
      literacy: 0.65    # 0..1; her pop grubuna verilen hazırlık girdisi; oyun yeniden hesaplar
      wealth: 14        # başlangıç serveti; GDP hedefi değildir
states:
  STATE_LOWER_EGYPT:
    population:
      total: 2500000
      composition:
        - {culture: misri, religion: sunni, share: 0.80}
        - {culture: misri, religion: oriental_orthodox, share: 0.15}
        - {culture: turkish, religion: sunni, share: 0.05}
```

- `total` ve `scale` aynı planda birlikte kullanılamaz. Ülke `total` değeri mevcut nüfusa orantılı olarak sahip olduğu eyaletlere dağıtılır; eyalet `total` değeri eyaletin sahipleri arasında dağıtılır. Sıfır ağırlıkta eşit dağılım kullanılır.
- Öncelik **ülke → eyalet → by_owner**. Dar kapsamda yazılan `total` / `scale`, geniş kapsamdakini değiştirir. Bu yüzden eyalet istisnaları ülkenin geniş kapsamlı toplam hedefini değiştirebilir; rapordaki son toplamı kontrol et.
- Oranlar yüzde 100 üzerinden değil **1 üzerinden** yazılır, toplamı 1 olmalıdır. Kişiler tam sayı olduğundan en büyük kalan yöntemi toplamı tam korur; kesirler kişi hassasiyetinde yuvarlanır. Ülke oranları eyaletler bazında uygulanır; ülke toplamında küçük yuvarlama farkları olabilir.
- `composition` ortak kültür/din dağılımını korur. Bunun yerine `cultures: {misri: 0.9, turkish: 0.1}` ve `religions: {sunni: 0.8, oriental_orthodox: 0.2}` ayrı verilebilir; bunlar **bağımsız çapraz dağılım** oluşturur. Bağlı kültür/din grupları istiyorsan composition kullan.
- Composition satırına isteğe bağlı `pop_type` yazılabilir. Oran belirtmeden yalnızca ölçek değiştirildiğinde mevcut ortak dağılım korunur. Boş arazide pozitif nüfus yaratmak için açık composition gerekir.
- Devralınan başlangıç okuryazarlığı ülke scripted effect'lerinden gelir. Rapor açık literacy değerini hazırlık girdisi olarak gösterir. Vanilla scripted_effects dosyaları okuryazarlık ve servetin oyun hazırlığında yeniden hesaplandığını açıkça belirtir; 1 Ocak ekranında aynı değer garanti değildir.

### Binalar, üretim yöntemleri ve şirketler

```yaml
states:
  STATE_LOWER_EGYPT:
    industry:
      mode: merge
      buildings:
        building_textile_mill: 12
        building_tooling_workshop: 6
        building_university: {level: 3, ownership: government}
        building_port: 4
```

`industry.mode: merge` mevcut binaları korur; yazılan bina türünün seviyesini **mutlak** değerle değiştirir. `replace` o kapsamın mevcut binalarını silerek listeden başlar. `scale` devralınan seviyeleri çarpar; açık bina değerleri sonra uygulanır. Seviye 0 o türü kaldırır. Ülke `industry.buildings` listesi **sahip olunan her eyalete** uygulanır; ülke çapında paylaştırılan toplam değildir. Genel dönüşüm için ülke `scale` / `replace`, sanayi merkezleri için eyalet bazında bina listeleri tercih et.

Bina nesnesi `level`, `production_methods: [gerçek_pm_id]`, `ownership: self|government`, `reserves: 0..1` alır. PM verilmezse her üretim yöntemi grubunun ilk kaynak yöntemi kullanılır; teknoloji gereksinimleri doğrulanır. Kısmi PM listesinde kalan gruplar otomatik tamamlanır. Yalnız seviye değiştirildiğinde mevcut üretim yöntemleri korunur. Sahiplik varsayılanı binanın kaynak tanımına göre özel veya hükümettir.

Kaynak ve ekilebilir alan sınırları bölünmüş eyalette tüm sahiplerin toplamı için denetlenir. Yanlış kaynak yatağı, kara eyaletinde liman, hatalı PM grubu, PM/bina teknoloji gereksinimi ve merkezi olmayan ülkede bina hata üretir. Tahmini istihdam ve temel altyapı talebi raporlanır; gerçek işe alım, piyasa erişimi, girdiler, fiyatlar ve kâr motor simülasyonu ister. “Daha fazla fabrika” tek başına iyi ekonomi değildir; tarım, hammadde, ulaşım, eğitim, bürokrasi ve ticareti de tasarla.

```yaml
countries:
  EGY:
    companies:
      mode: replace
      add: [{type: company_misr, headquarters: STATE_LOWER_EGYPT}]
      remove: []
```

Şirket kimliği, merkez sahipliği ve merkezde uygun bina türü denetlenir. Şirketin `possible`, `attainable`, minimum seviye, incorporation, teknoloji ve DLC koşullarını `rules --kind companies --query ... --script` ile ayrıca incele. Tüm script trigger'larını çalıştıran bir motor emülatörü yoktur.

### Teknoloji, kanunlar, kurumlar, çıkar grupları

```yaml
countries:
  EGY:
    technology: {mode: merge, tier: 1, add: [corporate_charters]}
    laws:
      values: [law_freedom_of_conscience, law_tenant_farmers, law_public_schools]
    institutions: {institution_schools: 2}
    interest_groups:
      mode: replace
      ruling: [ig_industrialists, ig_intelligentsia]
      strength: {ig_industrialists: 0.5, ig_landowners: -0.3}
```

Teknoloji `mode: replace` ile geçmiş başlangıç listesini temizler; `tier` kurulu oyunun 1–7 başlangıç paketidir (**1 ileri, 7 geri**). `add` ve `remove` gerçek teknoloji ID listeleridir. Varsayılan `prerequisites: add` eksik öncülleri tamamlar; `error` eksik öncülü hata yapar. Hâlâ başka bir teknolojinin gerektirdiği teknoloji silinemez. Teknolojiyi geriletirken korunmuş bina/PM/ordu ve kanunlar uyumsuz kalırsa bunları da değiştir.

Kanunlar aynı grupta birleşir: yazılan kanun o grubun eskisini değiştirir. `laws.mode: replace` açık başlangıç kanun listesini sıfırlar; tam alternatif ülke için istediğin grupları açıkça yaz. Hiç yazılmayan grupları oyun varsayılanı tamamlayabilir; rapor bunlar için uydurma değer göstermez. Aynı gruba iki kanun, bilinen yasaklayıcı kanunlar ve eksik teknoloji denetlenir. Kurum seviyesi 0–5 ve etkinleştiren kanun denetlenir; bütün dinamik yatırım üst sınırları simüle edilmez.

`interest_groups.ruling` hükümete ekler; `mode: replace` mevcut hükümet IG'lerini önce çıkarır. `strength` siyasi güç **çarpanına eklenen değişimdir**: 0.5 = +%50, -0.3 = -%30. Bu değer kesin clout yüzdesi değildir; nüfusun meslekleri, serveti ve kanunlar sonucu değiştirir. Oluşturulan güç modifier'ı kalıcıdır.

`history_mode: inherit` ülkenin vanilla başlangıç öykü/effect'lerini korur. `replace` o ülkenin `history/countries` bloğunu baştan kurar; teknoloji ve kanunları açıkça tanımla. Bu alan nüfus, askerî veya diplomasi katmanlarını otomatik sıfırlamaz; onların kendi mode ayarlarını kullan. Karakterler, journal tanımları, on_action'lar ve ileride çalışan olaylar ayrı mod içerikleridir.

### Ordu ve donanma

```yaml
countries:
  EGY:
    military:
      mode: replace
      formations:
        - name: Nil Ordusu
          type: army
          hq_region: region_near_east
          units:
            - {type: combat_unit_type_line_infantry, state: STATE_LOWER_EGYPT, count: 25}
        - name: İskenderiye Filosu
          type: fleet
          hq_region: region_near_east
          ships:
            - {type: ship_type_frigate, state: STATE_LOWER_EGYPT, count: 5}
```

1.13 kaynağı donanmada `ship_type` ve gemi kullanır. Eski sürümlerden ezber flotilla/barracks kimliği üretme. `mode: merge` yeni formasyonları ekler; `replace` ülkenin askerî başlangıç bloğunu değiştirir. `formations: []` ile temizlenebilir. Kara biriminde eyalet zorunludur; filo eyaleti isteğe bağlıdır, ülkenin kıyısı olmalıdır. Birim/teknoloji/eyalet sahipliği denetlenir. Devredilen eyalete bağlı eski askerî birimler eski sahibin bloğundan çıkarılır; yeni sahibine otomatik bir ordu yaratılmaz. Yeni orduları açıkça tanımla.

### Diplomasi, sömürgeler ve iç içe bağlılıklar

```yaml
subject_types:
  ve_feudal_vassal:
    base: vassal
    name: Feudal Vassal
    name_tr: Feodal Vasal
    overlord_types: [recognized, unrecognized]
    subject_types: [recognized, unrecognized]
    can_have_subjects: true
    join_overlord_wars: true
    income_transfer: 0.15
diplomacy:
  mode: inherit
  reset_countries: [FRA, ZBR]
  subjects:
    - {overlord: FRA, subject: ZBR, type: ve_feudal_vassal, liberty_desire: 25}
  relations:
    - {actor: FRA, target: EGY, value: -30}
```

- `mode: replace` tüm vanilla başlangıç diplomasisini kaldırır; yalnızca listelenenleri kurar. `inherit` diğer ilişkileri korur.
- `reset_countries` listedeki ülkeye ait veya o ülkeyi hedefleyen devralınmış başlangıç işlemlerini kaldırır. Yeni senaryo ilişkileri sonra uygulanır.
- Yeni subject kaydı hedefin eski overlord'unu değiştirir. İki overlord ve dolaylı bağlılık döngüleri hatadır. Üstüne bağlı devletler bağlanacak bir vasalın türünde `can_have_subjects: true` gerekir.
- `relations.value` -100..100; `liberty_desire` 0..100. Liberty desire bütün başlangıç pact'ları oluşturulduktan sonra uygulanır.
- `pacts: [{actor: FRA, target: EGY, type: alliance}]` gibi kalıcı anlaşmalar desteklenir. Türü katalogdan doğrula. Subject ilişkileri için pacts kullanma.
- `remove: [{actor: GBR, target: BIC}]` belirtilen yöndeki devralınan hedef işlemlerini kaldırır; `type` vererek belirli pact ile daraltabilirsin. Her iki yönü kapsayan tam sıfırlama için reset_countries kullan.
- Özel tür ID'si `ve_` ile başlamalıdır. Derleyici kurulu oyunun subject_type **ve** diplomatic_action tanımlarını birlikte türetir, gelir payını ve tanınmış devlet izinlerini uygular. Vanilla `vassal`, tanınmış Fransa'ya uygun değildir. Özel tür başlangıç pact'ı için hazırlanır; yeni diplomatik oyun/sway arayüzü ve bütün gelecekteki özerklik geçişleri ayrıca tasarlanabilir.

**BIC'yi kaldırma:** Önce `catalog --region BIC` ile BIC'nin bütün eyalet paylarını bul. Yalnızca BIC paylarını yeni ülkelere dağıt; split eyaletlerde diğer devletlerin illerini yanlışlıkla yutma. Yeni ülkelerin başkentini, kültürünü, dinini ve başlangıç mekaniklerini tanımla. `reset_countries: [BIC]` eski bağımlılık ağını temizler; eski vasalları yeni `subjects` kayıtlarıyla bağla. Toprağı kalmayan ülke üretilen diplomasi/ordu/ülke başlangıç katmanlarından çıkarılır; tarihî tag tanımını silmek gerekmez. İngiliz olaylarının ilerideki etkilerini kaldırmak ayrı event/on_action işidir. İngiltere'nin diğer kolonilerini de istemiyorsan onların toprak ve diplomasi planını ayrıca değiştir.

## Çıktıları nasıl yorumlamalı?

`scenario-report.json` üretilen nüfus/dağılım ve bina seviyeleri, açık teknoloji/kanun listeleri, ülke askerî toplamı, bağlılık ağı, vanilla nüfus/bina karşılaştırması ve sınırlar içerir. `validation: passed`, kaynak kontrollerinin geçtiğini söyler; `validation_scope: static_source` ve `runtime_tested: false` bu sınırı makine tarafından da okunabilir kılar. Runtime/DLC tetikleyicilerinin veya denge hedefinin garantisi değildir. Vanilla'da da mevcut hatalar notlara çevrilir. Karakter geçmişi, journal, event ve on_action içerikleri yeniden üretilmez; değişen ülke ve formasyonlar bu içeriklerdeki kayıtlı scope'ları oyun hazırlığı sırasında da geçersiz kılabilir. Etkin senaryo için oyun içi yeni başlangıç testi ayrıca gerekir.

Atlas v2 alanlarını import/export sırasında korur. Derlenmiş v2 atlasında eyaletin başlangıç dünya paneli vardır. Taslak değiştirilince önceden hesaplanmış ekonomik rapor gizlenir ve LLM bağlamından çıkarılır. Dışa aktar, tekrar validate/report/atlas çalıştır; tarayıcıda ekonomi simüle edilmez.

Örnek: `tools/examples/ve_industrial_reversal.yml`. Fransa veya başka bir ülke için varsayılan özel vasallık yoktur; özel türler yalnız açık scenario.subject_types girdisinden üretilir. Test fixture dosyaları kullanıcı senaryosu değildir. Test: `PYTHONPATH=tools .venv/bin/python -m unittest tools/test_scenario.py tools/test_atlas.py` ve `tools/tgc.py selftest`.
