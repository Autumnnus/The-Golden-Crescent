# Plan sözleşmesi · version 1

Çalışan tam örnek: `tools/flavor/examples/academy.yml`. UTF-8 YAML veya JSON kullanılır. Yinelenen anahtarlar, YAML alias'ları ve bilinmeyen alanlar reddedilir. Oyun metinleri için `tr` ve `en` çevirileri zorunludur.

## Üst yapı

```yaml
version: 1
namespace: ve_hikaye
title: Önizlemenin başlığı
summary: Hikâyenin amacı ve kapsamı.
assumptions: [Açık varsayımlar]
variables: {destek: 0, mektup_geldi: null, aylar: 0}
modifiers:
  itibar:
    title: {tr: Akademinin itibarı, en: The Academy's Renown}
    values: {country_prestige_add: 15}
nodes: {} # Gerçek planda en az bir bağlı düğüm gerekir.
```

Namespace `ve_` ile başlar, en fazla 32 karakterdir. Yerel kimlikler küçük harf/rakam/alt çizgi kullanır. Paket 1–150 düğüm içerir. `variables` ülke bazında ve paket namespace'iyle saklanır; sayısal varsayılanlar ilk kullanımda atanır. `null` değişkeni ayarlamaz; `has_variable` ile flag gibi kullanılabilir. Değişkenler ülke arasında otomatik paylaşılmaz.

Yerel modifier'larda bu sürüm `country_prestige_add`, `country_authority_add`, `country_bureaucracy_add` destekler. Diğer mekanikler için gerçek kaynak örneğiyle yeni destek eklenmelidir.

## Event

```yaml
nodes:
  dilekce:
    kind: event
    number: 1
    country: EGY
    title: {tr: Bir dilekçe, en: A Petition}
    description: {tr: Saraya bir dilekçe ulaştı., en: A petition has reached the court.}
    flavor: {tr: Mürekkebi hâlâ ıslaktı., en: The ink was still wet.}
    context: Neden bu ülke, bu tarih ve bu katılımcılar?
    entry: {pulse: monthly}
    trigger: {after: '1836.2.1', owns_state: STATE_LOWER_EGYPT}
    icon: gfx/interface/icons/event_icons/event_newspaper.dds
    media: {alias: middleeast_engineer_blueprint}
    immediate: []
    options:
      - id: kabul
        text: {tr: Kabul edelim., en: Accept.}
        default: true
        ai_weight: 3
        effects: [{set_variable: {name: destek, value: 1}}]
        next: [{to: akademi, delay_days: 1}]
```

`number` 1–999999 arasında ve paket içinde benzersizdir; event ID'si `namespace.number` olur. `entry` yalnız kendiliğinden başlayan düğümlere yazılır; diğerleri `next` ile ulaşılır. `trigger` yoksa alıcı ülke, varlık ve tek kullanım kontrolleri yeterlidir. Her düğümde anlatısal `context` zorunludur.

1–6 seçenek bulunur. Tam biri koşulsuz `default: true` ve pozitif `ai_weight` taşımalıdır. Diğer seçeneklerde `when` koşulu kullanılabilir. `immediate` sahne açılınca; `effects` ilgili seçenek seçilince çalışır. Bağlantılarda gecikme 1–36500 gündür; belirtilmezse 1 gün. Hedef ülke, hedef düğümün `country` alanından gelir.

Her düğüm alıcı ülke başına bir kez çalışır. Yeniden oynatılan/döngülü hikâyeler bu sürümde desteklenmez. Kimlikleri değiştirmenin eski kayıt dosyalarında migrasyon etkisi vardır; otomatik save migrasyonu yapılmaz.

## Günlük

```yaml
nodes:
  akademi:
    kind: journal
    country: EGY
    title: {tr: Bir okul kuralım, en: Build a School}
    description: {tr: Hazırlığı ve reformu tamamlayın., en: Complete the preparations and reform.}
    context: Desteklenen dilekçenin uygulanma süreci.
    trigger: {variable: {name: destek, op: '=', value: 1}}
    complete: {has_law: law_public_schools}
    fail: {not: {owns_state: STATE_LOWER_EGYPT}}
    timeout_days: 730
    progress: {variable: aylar, goal: 12, monthly_increment: 1}
    on_complete:
      effects: [{add_modifier: {name: itibar, days: 1825}}]
      next: [{to: acilis, delay_days: 5}]
    on_fail: {effects: [], next: []}
    on_timeout: {effects: [], next: []}
```

`complete` zorunludur. `fail`, `timeout_days`, `progress` ve sonuç blokları isteğe bağlıdır. `on_fail` için fail, `on_timeout` için süre gerekir. Süre yoksa açık kalma olasılığı not edilir. Aynı complete ve fail koşulu reddedilir; bütün mantıksal çelişkiler çözümlenmez.

Günlükler açık `add_journal_entry` yoluyla başlar; kendiliğinden possible/is_shown taramasına dayanmaz. `group` varsayılanı gerçek `je_group_technology` tanımıdır, katalogdaki başka grup seçilebilir. Varsayılan simge event gazete DDS'sidir.

İlerleme çubuğu kullanılırsa belirtilen değişken açılışta sıfırlanır, günlük aktifken aylık pulse'ta artırılır. Aynı değişken iki günlükte ilerleme sayacı olamaz. Tamamlama için **çubuk hedefi VE complete koşulu** gerekir. Düğümün `immediate` işlemleri sıfırlamadan sonra çalışır. Bu çubuk ekonomik yatırım veya gerçek öğrenci sayısı simülasyonu değildir.

## Koşullar

Aynı nesnedeki alanlar AND anlamına gelir. `all: [...]`, `any: [...]`, `not: {...}` ile gruplandırılır. Boş koşul yerine `always: true` yaz.

| Alan | Değer / anlam |
|---|---|
| `always` / `is_player` | Boolean |
| `after` | `'1836.2.1'`, dahil başlangıç tarihi |
| `before` | `'1860.1.1'`, hariç bitiş tarihi |
| `has_law` | `law_public_schools`; ülkenin tam kanunu |
| `technology` | `academia`; ülkenin araştırılmış teknolojisi |
| `primary_culture` | `misri`; ülkenin birincil kültürlerinden biri |
| `state_religion` | `sunni`; ülkenin resmî dini |
| `has_culture_pop` | `misri`; ülkede bu kültürde en az bir pop |
| `has_religion_pop` | `sunni`; ülkede bu dinde en az bir pop |
| `owns_state` | `STATE_LOWER_EGYPT`; eyaletin en az bir payına sahiplik |
| `has_building` | Gerçek bina ID'si; ülkede bina bulunması |
| `has_variable` | Planın tanımlı değişken adı |
| `variable` | `{name: destek, op: '>=', value: 1}`; önce varlık denetlenir |

Karşılaştırmalar `= != > < >= <=` destekler. Bağımsız nesne içindeki tarih aralığı kontrol edilir; keyfî script mantığının tamamı için bir SAT çözücüsü yoktur. Pop oranı/bina seviyesi gibi daha ileri koşulları bu alanlardan uydurma: kaynakla doğrulanmış yeni DSL işlemi gerekir.

## Etkiler

Her liste öğesinde tek işlem bulunur. Effects alanında koşullar değil bu işlemler yazılır:

```yaml
effects:
  - set_variable: {name: destek, value: 1}
  - remove_variable: mektup_geldi
  - add_modifier: {name: itibar, days: 365}
  - remove_modifier: itibar
  - relations: {country: PER, value: 10}
  - add_primary_culture: turkish
  - state_religion: sunni
  - activate_law: law_public_schools
  - add_technology: academia
  - if:
      when: {is_player: true}
      then: [{set_variable: {name: destek, value: 2}}]
      else: []
```

Modifier adı yerel `modifiers` kaydı veya gerçek kaynak ID'si olabilir. Mevcut modifier yalnız ülke modifier alanları taşıyorsa kullanılabilir; kapsamı belirsiz karakter/eyalet/bina modifier'ı reddedilir. Süreli etkiler 1–36500 gün arasındadır. Relations alıcısı yoksa işlem atlanır.

Kanun ve teknoloji işlemleri zorunlu araştırma/kanun şartlarını veya ekonomi dengesini kendiliğinden çözmez; gelecek tarihteki uygunluğu `trigger` / `when` ile belirt. Bu komutları bir başlangıç dünyası düzenleyicisi gibi kullanma; başlangıç listeleri Atlas'a aittir.

## Görseller

```yaml
# Oyunla gelen görünüm:
icon: gfx/interface/icons/event_icons/event_map.dds
media: {alias: middleeast_engineer_blueprint}

# Yerel simge ve mevcut video için hazırladığın önizleme posteri:
icon: {file: assets/academy_icon.dds}
media: {alias: middleeast_engineer_blueprint, poster: assets/academy_preview.png}

# Hazır gerçek Bink 2 videon varsa:
media:
  video: assets/academy.bk2
  fallback: middleeast_engineer_blueprint
  poster: assets/academy_preview.png
```

Yerel dosyalar planın kendi klasörü altında bulunmalı. DDS simgesi Pillow ile açılıp okunur. Bink 2 video başlığı denetlenir; tam codec decode testi yapılmaz. Özel video için kaynakta var olan fallback zorunludur. Derleyici yeni medya alias'ını ve paket namespace'i altında asset dosyasını birlikte üretir. Mevcut alias'ların fallback zincirleri ve fiziksel dosyaları kontrol edilir.

Tarayıcı Bink videoyu oynatmaz. Poster varsa onu, yoksa gerçek oyun simgesini gösterir ve bunu açıkça etiketler. PNG poster oyuna kurulmaz. PNG/JPEG'yi uzantı değiştirerek oyun videosu yapma; bu araç video dönüştürücüsü değildir.

## Metinler ve scope sınırları

Oyun localization metinleri UTF-8 BOM ile, doğru dil başlıkları ve namespace anahtarlarıyla yazılır. Tırnak/ters eğik çizgi/satır sonları escape edilir. Bu sürüm düz metin destekler; `[Scope.GetName]` ve `$LOCALIZATION$` gibi dinamik ifadeler belirsiz scope bağlantısı üretmemek için reddedilir. Ülke alıcıları sabittir; dinamik ülke/karakter seçimi, saved scope taşıma, karakter portreleri ve özel event GUI'leri bu sözleşmeye dahil değildir.
