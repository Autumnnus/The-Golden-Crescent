# LLM ile harita ve senaryo geliştirme

Harita kaynağı, oyunun kurulu sürümünün gerçek `provinces.png` ve state/history
verileridir. Üzerine `world/` uygulanır. Oyun açılmaz, API anahtarı gerekmez.
Atlas bir 1836 kaynak önizlemesidir; save, olay zinciri veya ekonomi simülatörü değildir.

## Hazırlık

Python **3.10+** gerekir. Sistem Python'u eskiyse Python 3.11+ seçin.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
```

Windows'ta `py -3.11 -m venv .venv`, ardından
`.venv\Scripts\python -m pip install -r tools/requirements.txt` kullanın.
Aşağıdaki komutlarda Windows için Python yolunu buna göre değiştirin.
Oyun özel bir dizindeyse `VIC3_GAME_DIR` değişkenini oyunun `game` klasörüne ayarlayın.

## Önerilen döngü

1. **Gerçek kimlikleri edin.** İlgili bölgeyi katalogla; kullanıcının anlattığı
   yerleri `find` ve `show` ile doğrula. Ülke, STATE kimliği veya il hex kodu uydurma.
2. **Referansı çiz.** Eyaletleri ve komşularını haritada incele.
3. **Senaryoyu ayrı bir JSON/YAML dosyası olarak yaz.** `world/` henüz değişmez.
4. **Önizle ve karşılaştır.** Atlası, siyasi PNG'yi ve değişim haritasını üret.
   Hatalı sahiplikte araç çıkış kodu 2 verir; hataları gider.
5. **Sonuçları kullanıcıya göster.** HTML etkileşim içindir; JSON LLM bağlamıdır;
   PNG raporlara veya sohbete eklenebilir.
6. **Senaryonun moda uygulanması istendiğinde** taslağın `countries` ve `states`
   kayıtlarını ilgili `world/` YAML'larıyla birleştir, `build` ve `check` çalıştır.
   Mevcut eyalet tanımını düzenle; aynı STATE kimliğini yeni dosyada tekrar tanımlama.

```bash
.venv/bin/python tools/tgc.py catalog --region 08_middle_east --out build/context.json
.venv/bin/python tools/tgc.py map --mode reference --region 08_middle_east
.venv/bin/python tools/tgc.py find Erzurum
.venv/bin/python tools/tgc.py show STATE_ERZURUM

.venv/bin/python tools/tgc.py atlas --scenario tools/examples/ve_atlas_scenario.yml
.venv/bin/python tools/tgc.py map --scenario tools/examples/ve_atlas_scenario.yml --region STATE_ERZURUM --data
.venv/bin/python tools/tgc.py map --scenario tools/examples/ve_atlas_scenario.yml --mode changes --region 08_middle_east
```

`--region` değerleri: `world`, `STATE_ERZURUM`, `Erzurum`, `08_middle_east`,
`TUR`, `country:TUR`, `world/_aliases.yml` içindeki bir ad veya virgülle ayrılmış
seçimler. Eyalet odağı yalnızca **kara komşularını** ekler; bütün komşu denizi
kadraja almaz. Ülke odağı o ülkenin tüm paylarının bulunduğu eyaletleri kapsar.
Harita yatayda dünya kenarını sarmalamaz; uzak koloniler geniş kadraj oluşturabilir.

`catalog` bir JSON nesnesi döndürür; önbellek oluşturma mesajları stderr'e gider.
Daha az token için tüm dünya yerine ilgili bölgeyi seç. `countries` görünür
sahipleri ve senaryoda tanımlanan ülkeleri, `country_tags` bilinen tüm etiketleri
içerir. `owners[].provinces`, `neighbors`, `impassable`, `source`, kaynaklar ve
karşılaştırma bilgileri gerçek kimliklerin bağlamıdır. Raster piksel verisi JSON
bağlamına eklenmez. Atlasın yanındaki JSON oluşturma anının fotoğrafıdır;
tarayıcıdaki değişikliklerden sonra **LLM bağlamını indir** düğmesini kullan.

## Senaryo biçimi — sürüm 1

```yaml
version: 1
title: Doğu Anadolu Mutabakatı
description: İsteğe bağlı senaryo özeti
countries:
  ZZT:
    name: Erzurum Confederation
    name_tr: Erzurum Konfederasyonu
    color: [224, 180, 93]
    country_type: recognized
    tier: principality
    cultures: [turkish, armenian]
    religion: sunni
    capital: ERZURUM
    phase: "2"
states:
  STATE_ERZURUM:
    split:
      - owner: ZZT
        provinces: [x895074, x4F6E8F, xC01080]
      - owner: TUR
        rest: true
    phase: "2"
```

- Ülke alanları mevcut `world/` tanımıyla birleştirilir; verilmemiş alanlar korunur.
  `world/` içinde olmayan ülkeler için generator'ın vanilla üzerine uyguladığı
  Country varsayılanları geçerlidir. Harita için yeni ülkenin tag, ad ve rengi yeter;
  oyuna aktarımda kültür, başkent ve diğer gerekli tanımlar da tamamlanmalıdır.
- Eyalet kaydı **önceki sahiplik planını değiştirir**; `owner` veya `split` kullan.
  Eyalet alanları `tools/README.md` ile aynıdır. İl ataması mevcut payları korur.
- `rest: true` tek bir payda olabilir. Normal illerin tamamı atanmalıdır. Geçilemez
  iller ayrı renkle belirtilir; `rest` bunları normalde ülkeye katmaz. Tamamı
  geçilemez olan bir eyalette generator'ın mevcut özel kuralı geçerlidir.
- Ülke/eyalet kimliği, yanlış eyaletteki il, tekrarlanan il, açıkta kalan il,
  yinelenen JSON/YAML anahtarı, bozuk renk ve desteklenmeyen alanlar reddedilir.
- `phase` varsa eyaletin fazı, yoksa ülkenin fazı kullanılır. Renkler kararlıdır.
- `religion` katmanı **sahibin devlet dinini** gösterir; nüfusun çoğunluk dini değildir.
- `changes` yalnızca **il sahipliği değişimini** gösterir; ad, renk, kültür veya din
  değişimi toprak değişimi sayılmaz.
- Varsayılan `--baseline world` mevcut modu karşılaştırır. Mod ile vanilla arasındaki
  fark için `--baseline vanilla` kullan. Senaryo her iki durumda da mevcut `world/`
  üzerine uygulanır; baseline yalnızca karşılaştırmanın başlangıcını belirler.
- `world/state_regions` içindeki `provinces`/`impassable` geometri değişimleri
  desteklenmiyorsa araç açık hata verir. Yanlış bir vanilla sınırı sessizce çizilmez.
- Kaynak sahipliği doğrulaması oyun doğrulamasının yerine geçmez. Tarihsel vanilla
  veri tutarsızlıkları notlarda görünür; `build` ve `check` oyun kurallarını denetler.

## Tarayıcıdaki atlas

```bash
.venv/bin/python tools/tgc.py atlas
```

`build/maps/atlas_world.html` dosyasını tarayıcıda aç. Sunucu, CDN ve ağ bağlantısı
gerekmez. HTML'nin yanında `atlas_world.json` üretilir.

- Haritadan veya listeden eyalet seç. Shift+tık ile çoklu seçim yap.
- İl açılır listesinden kesin hex kimliğini seç; ülke etiketini yazıp **İli ata**
  veya **Eyaleti ata** kullan. İle tıklamak da o hex kimliğini seçer.
- Katmanlar: siyasi, referans, devlet dini, faz, değişim. Sınırlar ülke/eyalet/il
  düzeyinde seçilebilir. Referans renkleri siyasi aidiyet anlamına gelmez.
- Sürükle/tekerlek ile gez. Klavye: harita odaktayken oklar, `+`, `-`, `0`.
  Dizindeki düğmeler ve `Sığdır` sürüklemeye alternatif sağlar.
- Önce/sonra sürgüsünde solda baseline'ın siyasi haritası, sağda seçili senaryo
  katmanı görünür. Etiketler ölçekten bağımsız okunur.
- Geri al / yinele ve Ctrl/Cmd+Z desteklenir. Başlangıca dönme de geri alınabilir.
- JSON senaryosu aç/indir; CLI hem JSON hem YAML okur. Tarayıcı yalnızca JSON alır.
- Tarayıcı kaydı bu atlasın veri sürümüne özgüdür. Kaydın engellendiği tarayıcılarda
  indirme kullan. HTML dosyası değişmez; kalıcı/paylaşılabilir sonuç için JSON indir.
- Atlas rasteri varsayılan en çok 4096 piksel genişliğindedir. Çok küçük iller
  örneklemede görünmeyebilir; kesin seçim için il listesini, ayrıntı için bölgesel
  atlası veya `--width 8192` kullan. CLI'deki kimlikler tam çözünürlükten gelir.
- PNG indirme tam haritayı dışa aktarır; ekrandaki pan/zoom kırpmasını uygulamaz.
  Paylaşım için başlık/lejant içeren CLI `map` çıktısı da kullanılabilir.

## Önbellek ve doğrulama

İlk geometri üretimi pahalıdır; sonraki çalıştırmalar mmap ile okunur. Bölge
kırpma ve ölçekleme RGB boyamadan önce yapılır. Harita için nüfus/bina dönüşümleri
çalıştırılmaz. Geometri önbelleği görüntü yolu/boyutu/zamanı, province-state eşlemesi,
sıralama ve biçim sürümüyle doğrulanır. Eksik adjacency dosyası yeniden üretimi tetikler.
Oyun yamasından sonra vanilla indeksini `index`, ardından geometriyi `geo --force`
ile yenile; indeks vanilla'nın bütün dosyalarını her çizimde yeniden taramaz.

```bash
.venv/bin/python tools/tgc.py selftest
.venv/bin/python tools/tgc.py check
.venv/bin/python -m unittest discover -s tools -p test_atlas.py -v
```

Mevcut `selftest` geçici world tanımları ve üretilen oyun dosyaları üzerinde çalışır,
sonunda bunları geri toplar; aynı anda bir build veya harita önizlemesi çalıştırma.
`test_atlas.py` sahiplik, çizim ve önbellek için sentetik, dünya dosyalarına yazmayan testlerdir.
