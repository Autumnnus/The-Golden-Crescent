# LLM için flavor çalışma sözleşmesi

Kullanıcı hikâyeyi tarif eder; LLM planı yazar. Aracın kendisi bir LLM çağırmaz, API anahtarı istemez ve tarihi anlatıyı otomatik uydurmaz. Atlas ve Flavor ayrı CLI'lar ve ayrı kaynak dosyalarıdır; ortak olan yalnız düşük seviyeli PDX parser ve salt okunur oyun yolu yardımcılarıdır.

## Zorunlu akış

1. `tools/TOOLS.md`, bu belge ve `SYNTAX.md` dosyasını oku. Hikâyenin aktörlerini, tarih aralığını, kültür/din bağlamını, seçimlerini, hedeflerini ve sonlarını belirle. Kullanıcının belirtmediği kararları `assumptions` içine açıkça yaz.
2. `catalog` ile gerçek kimlikleri, medya takma adlarını, simgeleri ve kaynak scriptlerini incele. Desteklenmeyen DSL alanı veya motor komutu uydurma. Yeni bir DSL işlemi gerekiyorsa önce kurulu oyundan scope/syntax örneğini bul, derleyici ve doğrulamayı testlerle genişlet. Ham script ekleyerek doğrulamayı aşma.
3. Kendi kaynaklarını `flavor/projects/<hikaye>/plan.yml` ve aynı klasörün `assets/` dizininde tut. Örnek planı kullanıcının istediği senaryo sanma. Namespace'i `ve_` ile başlat; event numaraları ve düğüm kimlikleri sonraki düzenlemelerde sabit kalsın.
4. `validate` çalıştır. Ulaşılamayan düğüm, döngü, yanlış kimlik, eksik çeviri, koşullu varsayılan seçenek ve kopuk GFX bağlantılarını düzelt. Yalnız sıfır hata yeterli değildir: bütün uyarıları ve hikâye gerekçesini değerlendir.
5. `preview` üret. Kullanıcıya somut HTML diyagramını göster. Özellikle hangi ülkenin aldığı, otomatik giriş sıklığı, tarih aralığı, oyuncu seçenekleri, günlük hedefi/başarısızlığı/zaman aşımı, GFX ve bitiş dalları anlaşılır olsun. Bu aşamada oyun scriptlerini diske yazma.
6. **Bu belirli önizleme sürümünün kullanıcı onayını bekle.** “Tool'u geliştir”, “devam et”, kendi testlerinin geçmesi veya geçmişte başka senaryoya verilmiş onay yeni hikâyenin onayı değildir. Testlerin ürettiği sentetik belgeler hiçbir zaman kullanıcı onayı sayılmaz.
7. Kullanıcı HTML'den belge indirdiyse onu kullan. Kullanıcı sohbet içinde bu diyagramı açıkça onayladıysa aşağıdaki `approve` komutuyla gerçek onay cümlesini kaydet. Kullanıcının yerine onay uydurma veya sırf `build` engelini aşmak için belge oluşturma.
8. Onaylı planı `build` ile ayrı pakete derle; dosya/ID/localization/asset bağlantılarını incele. Kullanıcı etkin moda eklenmesini istemişse `install` çalıştır. `install` tek başına da onayı denetler; kurulumdan önce `build` çıktısını gözden geçirmek LLM akışının parçasıdır.
9. `check <namespace> --plan <plan>` çalıştır; kullanılan Atlas bağlamını aynı `--context` ile ver. Kullanıcıya kurulan dosyaları, seçilen varsayımları ve test kapsamını anlat. Oyun motorunda çalıştırmadığın pakete “oyunda doğrulandı” deme.

Sohbet onayını kaydetme, **yalnız kullanıcı o önizlemeyi onayladıktan sonra**:

```sh
.venv/bin/python tools/flavor/flavor.py approve flavor/projects/hikaye/plan.yml \
  --review build/flavor/ve_hikaye/review/review.json \
  --user-confirmation 'Kullanıcının bu diyagrama verdiği gerçek onay cümlesi ve konuşma bağlamı' \
  --out build/flavor/ve_hikaye/approval.json
```

Bu kayıt kimlik doğrulama/elektronik imza sistemi değildir; süreç kaydı ve sürüm kilididir. Onay notunda değişiklik talebi varsa bunu tamamlanmış onay sayma: önce planı düzelt, yeniden önizle. UI onay notları da bu şekilde okunmalıdır.

## Atlas ile birlikte çalışmak

Atlas başlangıç dünyasını; Flavor oyun sırasında yaşanacak hikâyeyi yönetir. Atlas'tan flavor içinde Python modülü çağırma veya Atlas çıktılarına event kodu ekleme.

1. `tools/LLM_SCENARIO_WORKFLOW.md` ile V2 başlangıç dünyasını hazırla.
2. **Ülke filtresi kullanmadan tam rapor** üret:

```sh
.venv/bin/python tools/tgc.py scenario report DUNYA.yml --out build/world-context.json
.venv/bin/python tools/flavor/flavor.py validate HIKAYE.yml --context build/world-context.json
.venv/bin/python tools/flavor/flavor.py preview HIKAYE.yml --context build/world-context.json --open
```

3. Rapordaki yeni ülke etiketleri flavor planında kullanılabilir. Toprağı kalmayan ülkeye flavor düğümü yazmak hata verir. Raporun dosya özeti onaya bağlanır; yeni rapor yeni onay gerektirir.
4. Bağlam gelecekteki dünya koşullarını simüle etmez. Örneğin bir eyalet sonradan fethedilebileceği için `owns_state` tetikleyicisi başlangıçta yanlışsa plan otomatik reddedilmez. Ülke başkentleri, kanun/teknoloji başlangıcı ve bölgenin din/kültür dağılımını tam rapordan ayrıca incele.
5. **Nihai flavor önizlemesi ve onayından önce** referans verilen yeni ülkelerin Atlas çıktısını etkinleştir ve Atlas `check` çalıştır. Erken flavor diyagramı yeni ülkeleri yalnız rapordan görebilir; Atlas kurulumuyla gerçek tanım dosyaları eklenince kaynak özeti değişir ve erken onay geçersiz olur. Bu durumda önizlemeyi yenile ve o son sürümün onayını al; ardından Flavor `build`, `install`, `check` uygula. Bağlamda var ama etkin modda henüz tanımlanmamış ülkeye kurulum araç tarafından engellenir.
6. Mevcut vanilla karakter/journal/event içerikleri bu araçla otomatik silinmez. BIC gibi ülkeyi kaldırınca eski İngiliz/Hindistan olaylarının ne olacağını ayrıca tasarla. Yeni flavor eklemek o içeriği kendiliğinden temizlemez.

## Tetikleme ve bağlam için karar kuralları

- Her düğüm tek bir açık ülke alıcısına sahiptir. Kültür ve din alanları ülke birincil kültürü/resmî dini ile pop kültürü/dini arasında ayrılır.
- Otomatik giriş için `monthly` veya `yearly` seç. Başlangıç günü garantisi verme; aylık giriş koşulu sağlandıktan sonraki uygun pulse ve ek 1 günlük yönlendirme gecikmesinde gelir. Dar tarih pencereleri pulse arasında kaçabilir.
- Bir eventin yalnız trigger'ı olması onu başlatmaz. En az bir `entry` ve bütün düğümlere uzanan bağlantı gerekir.
- Seçenek hedefleri ilgili alıcının ülke kapsamına geçer. Zaman alan bağlantılarda önce pending işaretlenir; teslimde koşullar yeniden okunur. Koşul artık uygun değilse bağlantı atlanır. Alternatif kurtarma dalı isteniyorsa bunu anlatının ayrı bir giriş/günlük yolu olarak tasarla.
- Düğümler alıcı ülke başına tek kullanımlıdır. Çoklu giriş “ilk geçerli teslim” anlamına gelir; bütün ebeveynlerin bitmesini bekleyen bir birleşme değildir. AND gereksinimlerini açık değişken/trigger koşullarıyla ifade et; geç gelen dal için teslim anını tasarla.
- En az bir koşulsuz ve pozitif AI ağırlıklı varsayılan seçenek zorunludur. Koşullu seçenek AI ağırlığı, o seçeneğin hiç erişilebilir olacağının kanıtı değildir.
- Günlük complete/fail/timeout yollarını ayrı tasarla. Aynı gün doğru olabilen koşullar için motorun değerlendirme sırasını varsayma. İlerleme çubuğu varsa hem hedef hem `complete` koşulu gerekir.
- Ağır geniş scope taramalarını sık pulse'a ekleme. Bu sürüm country pulse'larına ayrı isimli on_action ekler; vanilla effect bloklarını değiştirmez. Giriş filtresi yalnız ilgili ülkelerde çalışır.

## GFX kuralları

Önce gerçek medya alias'ı ve DDS simgesi seç. `catalog media` çıktısındaki dosya ve fallback ilişkisini kontrol et. Görsel anlatının kültür/coğrafya/dönemine uymalı; teknik olarak bulunması anlatıya uygun olduğu anlamına gelmez.

Yeni resim/video üretimi bu CLI'ın görevi değildir. Kullanılabilir görüntü araçlarıyla görsel üretebilir, gerçek DDS simgesi veya uygun Bink 2 videosu hazırlayabilirsin. Yalnız dosya uzantısını değiştirerek PNG'yi DDS/BK2 gibi gösterme. Video önizleme posteri, oyundaki videonun yerine geçmez. Poster/ikon/medya değişiklikleri onayı geçersiz kılar.
