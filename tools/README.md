# TGC harita modlama araci

Victoria 3 harita verisini elle `.txt` yazarak degil, okunabilir bir kaynaktan
**uretiyoruz**. Ozet:

```
world/  (sen ve Claude burayi duzenler)   ->   build   ->   common/, map_data/, localization/
```

`common/history/...` altindaki dosyalar **ciktidir**. Elle duzenlersen bir
sonraki `build` onlari ezer.

---

## Kurulum

Bir kerelik:

```bash
python -m pip install pillow numpy pyyaml
```

Vanilla oyun dizini varsayilan olarak
`C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game`.
Farkliysa `VIC3_GAME_DIR` ortam degiskenini ayarla.

Ilk index (vanilla her guncellendiginde tekrarla):

```bash
python tools/tgc.py index
```

```bash
python tools/tgc.py geo
```

---

## Gunluk dongu

```bash
python tools/tgc.py build
```

```bash
python tools/tgc.py check
```

```bash
python tools/tgc.py map --mode political --region region_near_east
```

`check` sifir hata verdiginde oyun dosyalari tutarlidir.

---

## Komutlar

| Komut | Ne yapar |
|---|---|
| `index` | Vanilla state/pop/bina/kultur verisini `build/index.json`'a cikarir |
| `geo` | `provinces.png`'den komsuluk grafigi ve state geometrisi hesaplar |
| `import` | Elle yazilmis eski mod dosyalarini `world/` formatina cevirir (bir kez) |
| `build` | `world/` -> oyun dosyalari |
| `check` | Kaynagi ve ciktiyi dogrular |
| `find <isim>` | State arar: `tebriz`, `Erzurum`, `STATE_BASRA`, `408` |
| `show <state>` | Bir state'in province/nufus/bina/komsu/kaynak dokumu |
| `neighbors <state>` | Komsu state'ler |
| `country <TAG>` | Ulkenin state'leri ve toplam nufusu |
| `regions [filtre]` | Strategic region listesi |
| `map` | Harita PNG'si uretir |

### `map` secenekleri

```bash
python tools/tgc.py map --mode political --region region_balkans
```

- `--mode political` — state'ler sahip ulkenin renginde (mevcut durum)
- `--mode reference` — her state ayri renk + isim (ekran goruntusu referansi)
- `--mode diff` — vanilla'dan farkli olan state'ler turuncu
- `--region` — strategic region adi (`region_near_east`), virgullu state listesi
  (`Konya,Adana,Erzurum`) ya da piksel kutusu (`4800,1100,5400,1500`)
- `--width` — maksimum genislik (varsayilan 2400)
- `--no-labels`, `--no-borders`

---

## `world/` bicimi

### `world/_defaults.yml`

```yaml
unlisted: inherit        # world/states'te olmayan state'ler vanilla halinde kalir
                         # (tam total conversion icin: drop)
pop_scale: 1.0
religion_map:            # global din donusumu
  sunni: mujtahidiyya
culture_map: {}
```

### `world/countries/*.yml`

```yaml
RUM:
  color: [62, 122, 189]        # ya da "hsv{ 0.99 0.7 0.9 }"
  country_type: recognized
  tier: empire
  cultures: [turkish]
  religion: mujtahidiyya       # DEVLET dini (country_definitions -> `religion =`)
  tech_tier: 1                 # 1 = teknolojik cephe, 7 = hicbir sey
  literacy: high               # very_high | high | middling | low | very_low | baseline
  capital: STATE_EASTERN_THRACE
  name: "Empire of Rum"        # localization (english)
  adjective: "Rumi"
  name_tr: "Rûm İmparatorluğu"  # localization (turkish)
  religion_map:                # bu ulkenin miras aldigi tum pop'lara uygulanir
    sunni: mujtahidiyya
  religion_split:              # tek dini birden fazla dine boler (asagi bak)
    orthodox: {mujtahidiyya: 0.35, orthodox: 0.65}
  culture_map: {}
  pop_scale: 1.0

  # Baslangic tabiiyeti (common/history/diplomacy uretimi)
  overlord: TUR                # bu ulke TUR'un tabiisi
  subject_type: vassal         # puppet | vassal | tributary | protectorate |
                               # dominion | colony | personal_union |
                               # crown_land | chartered_company
  liberty_desire: 30           # 0-100, baslangic bagimsizlik istegi
```

`religion:` ile `religion_map:` farkli seylerdir: birincisi **devletin** resmi
mezhebi (oyunun `country_has_state_religion` kontrolu buna bakar), ikincisi
**pop'larin** dini. Ikisi de yazilmali; yalnizca `religion_map` yazarsan pop'lar
donusur ama devlet dini birincil kulturun vanilla dininde kalir - `check` bunu
uyari olarak bildirir.

`religion_split` karma nufuslu eyaletler icindir: kaynak dini olan her pop
verilen oranlarda bolunur, toplam nufus korunur (yuvarlama artigi en buyuk
paya gider). `religion_map`'ten **once** calisir, ciktisi sonra map'ten gecer.
Oranlar toplaminin 1 olmasi gerekmez; kendi icinde normalize edilir.
Ayni alan `world/_defaults.yml` icinde global, `world/states/*.yml` icinde
`pops:` altinda state'e ozel olarak da yazilabilir.

### `world/states/*.yml`

En basit hali — tum state tek ulkeye:

```yaml
STATE_SYRIA: RUM
```

Acik hali:

```yaml
STATE_SYRIA:
  owner: RUM
  homelands: [mashriqi, turkish]
  pops: inherit
  buildings: inherit
```

Bolunmus state:

```yaml
STATE_ALEPPO:
  split:
    - owner: RUM
      provinces: [x0F0BCB, x186A43]
    - owner: EGY
      rest: true          # geri kalan tum province'lar
```

`pops` secenekleri:

```yaml
pops: inherit                        # vanilla pop'lari, sahibin donusum tablolariyla
pops: none                           # hic pop yok
pops:                                # ince ayar
  inherit: true
  scale: 1.2
  religion_map: {sunni: mujtahidiyya}
  culture_map: {turkish: rumi}
pops:                                # tamamen elle
  - {culture: mashriqi, religion: mujtahidiyya, size: 780000}
  - {culture: sephardic, size: 8000}
  - {culture: sudanese, pop_type: slaves, religion: animist, size: 7000}
```

`buildings` secenekleri:

```yaml
buildings: inherit                   # vanilla binalari, sahibi degistirilerek
buildings: none
buildings:
  - {building: building_barracks, levels: 4, owner: country}
  - building: building_millet_farm
    levels: 2
    owner: manor_house
    pms: [pm_simple_organization]
```

Sahipsiz birakmak:

```yaml
STATE_X:
  owner: unowned
```

### `world/state_regions/*.yml` (opsiyonel)

Vanilla state_region tanimini yamalar. Vic3'te bu dosyalar dosya adiyla
degistirildigi icin arac vanilla dosyasinin tamamini yeniden uretir.

```yaml
STATE_SYRIA:
  arable_land: 35
  traits: [state_trait_euphrates_river]
```

### Teknoloji ve okuryazarlik neden farkli mekanizmalarla yaziliyor?

Ikisi de `common/history` altinda ama semantikleri zit:

- **Teknoloji EKLEMELI.** `effect_starting_technology_tier_N_tech` yalnizca
  `add_technology_researched` / `add_era_researched` cagiriyor. Vanilla'nin
  dosyasi da bizimki de calisinca sonuc iki kumenin BIRLESIMI olur ve tier 1
  daha dusuk tier'larin ustkumesi oldugu icin ulke kesin olarak yukselir.
  Bu yuzden kendi dosya adimiz yeter: `tgc_technology.txt`.
  Tersi gecerli degil - bir ulkeyi bu yolla GERILETEMEZSIN. Senaryo Islam
  dunyasini yukseltip Avrupa'yi yerinde biraktigi icin buna ihtiyac yok.
- **Okuryazarlik ATAMA.** `set_pop_literacy` bir deger yaziyor; vanilla'nin
  `tur - ottoman empire.txt` dosyasi da calisiyor ve hangisinin kazanacagi
  yukleme sirasina kalir. Bu yuzden vanilla kaydi olan ulkeler icin o dosyayi
  AYNI ISIMLE yeniden uretiyoruz (dosyalar 3-5 satir, guncelleme riski yok);
  vanilla kaydi olmayanlar `tgc_population.txt`'ye gider.

### `world/_diplomacy.yml`

Baslangic rekabetleri ve iliski degerleri. Tabiiyetler burada degil,
`world/countries/*.yml` icindeki `overlord:` alanindadir.

```yaml
rivalries:
  - [TUR, EGY]                          # cift yonlu yazilir
relations:
  - {between: [TUR, EGY], value: -60}   # -100 .. +100
```

| Bolum | Cikti dosyasi |
|---|---|
| `overlord:` (world/countries) | `common/history/diplomacy/00_subject_relationships.txt` |
| `rivalries` | `common/history/diplomacy/00_rivalries.txt` |
| `relations` | `common/history/diplomacy/00_relations.txt` |

Ucu de vanilla dosyasinin AYNI ISIMLE tam kopyasidir: vanilla okunur, `world/`
icinde tanimli tag'lere dokunan kayitlar atilir, bizimkiler eklenir.
`check` tanimsiz tag, kendisiyle eslesme, tekrar eden cift ve aralik disi
deger hatalarini yakalar.

### `world/_aliases.yml`

Turkce/serbest isimleri state'lere baglar; `find` ve `--region` once buraya bakar.

```yaml
Sam: STATE_SYRIA
Konstantiniyye: STATE_EASTERN_THRACE
```

---

## Vanilla nasil eziliyor?

Tek bir kural yok — mekanizma dizine gore degisiyor. Asagidakilerin hepsi
oyunun kendi loglari, kurulu modlar ve oyun binary'si uzerinden dogrulandi.

| Dizin | Mekanizma | Ciktimiz |
|---|---|---|
| `common/history/states` | `replace_paths` | `tgc_states.txt` |
| `common/history/pops` | `replace_paths` | `tgc_pops_*.txt` |
| `common/history/buildings` | `replace_paths` | `tgc_buildings_*.txt` |
| `common/history/diplomacy` | ayni vanilla dosya adi, tam dosya | `00_subject_relationships.txt` |
| `common/country_definitions` | `REPLACE_OR_CREATE:` oneki | `tgc_countries.txt` |
| `map_data/state_regions` | ayni vanilla dosya adi, tam dosya | `08_middle_east.txt` gibi |
| `localization` | `replace/` klasoru | `replace/tgc_generated_*.yml` |

### `common/history/diplomacy` neden tam dosya?

Burasi da calisan bir history script'i, yani farkli isimli dosyalar birbirini
ezmez. Sorun su: vanilla `c:TUR ?= { ... c:EGY protectorate }` gibi
senaryomuzla celisen paktlar kuruyor ve history'de bir pakti geri alma efekti
yok. Bu yuzden vanilla dosyasini **ayni isimle** yeniden uretiyoruz: vanilla
icerigi okunur, `world/countries` altinda tanimladigimiz herhangi bir tag'e
dokunan paktlar atilir, kendi paktlarimiz eklenir. Ispanya-Kuba gibi ilgisiz
vanilla kurulumlari yerinde kalir; oyun guncellemesinde bayat kopya tasimayiz.
`build` kac vanilla pakt attigini uyari olarak bildirir.

### `common/history/*` neden `replace_paths`?

Bunlar keyed database degil, **calisan history script'leri**. Farkli isimli iki
dosya birbirini ezmez; ikisi de calisir. Yani vanilla'nin `create_state`'i de
bizimki de calisir. Bu teknik olarak "bozulma" degil (log'da duplicate hatasi
yok) ama total conversion icin yanlis: eski sahibin pop'lari ve binalari da
dogar, vanilla'nin geri kalan history'si (`military_formations` gibi) eski
sahiplige gore kurulmaya calisip hata verir.

Cozum `.metadata/metadata.json`:

```json
"game_custom_data" : {
    "multiplayer_synchronized" : true,
    "replace_paths" : [
        "common/history/states",
        "common/history/pops",
        "common/history/buildings"
    ]
}
```

Bu, vanilla'nin o dizinlerini tamamen yok sayar. Boylece kendi dosya
isimlerimizi kullanabiliyoruz ve vanilla kopyasi tasimiyoruz.

> `common/history/military_formations`, `characters`, `countries` hala vanilla'dan
> calisiyor. Sahiplik degisen bolgelerde bunlar hata uretecek; siralari geldiginde
> onlar da `replace_paths` listesine girmeli.

### `common/country_definitions` neden `REPLACE_OR_CREATE:`?

Burasi keyed database. Farkli isimli bir dosyada **duz** duplicate anahtar
yazarsan oyun onu sessizce atar ve vanilla kazanir:

```text
[gamedatabase.h:378]: Duplicated key TUR will not be created from file: common/country_definitions/tgc_balkans.txt:1
```

Anahtarin basina `REPLACE_OR_CREATE:` koyunca kendi dosya adinla override
edebiliyorsun; vanilla varsa uzerine yazar, yoksa olusturur:

```text
REPLACE_OR_CREATE:TUR = {
    color = { 62 122 189 }
    ...
}
```

Avantaji: vanilla'nin dokunmadigimiz ~800 ulkesi kendi dosyalarinda kaliyor.
Oyun guncellemesi onlari degistirdiginde bizde bayat kopya olmuyor.
`build` bunu otomatik ekliyor, `check` eksikse hata veriyor.

### `map_data/state_regions` neden tam dosya?

Harita verisi; `REPLACE_OR_CREATE` desteklenmiyor. Tek bir state'i degistirmek
icin o vanilla dosyasinin tamamini ayni isimle yeniden uretmek gerekiyor —
arac bunu senin icin yapiyor (vanilla'yi okur, yamayi uygular, tam dosyayi yazar).
Bu yuzden `world/state_regions/` yamalarini **sadece gerektiginde** kullan;
her yama bir vanilla dosyasini guncelleme-kirilgan hale getirir.

---

## Guvenlik

Butun yazma islemleri `vic3/paths.py:assert_safe_write()` uzerinden geciyor.
Mod dizini disina — ozellikle vanilla kurulumuna — yazmaya calisan her cagri
`PermissionError` ile durur. Vanilla yalnizca okunur.
