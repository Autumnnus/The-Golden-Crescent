> **Senaryo için güncel kaynak:** [sürüm 2 dünya tasarımı](../scenario/README.md). Bu arşivdeki ülke listeleri, bağlılıklar, din dağılımları ve üretim sırası yeni senaryonun kanonu değildir; [çelişki/karar kaydı](../scenario/tutarlilik_denetimi.md) bunların nasıl değiştiğini açıklar.

> TARİHSEL ARŞİV — Bu belge eski yeniden kurulum incelemesini korur; güncel dosya yolları veya silme talimatı değildir. Buradaki reset/clean/discard işlemlerini uygulamayın. Güncel düzen için ../../README.md ve ../TOOLS.md dosyalarını okuyun.

# The Golden Crescent — Yeniden Kurulum Planı

Bu belge **tek başına yeterli olacak şekilde** yazıldı. Discard sonrası `tools/`
ve `world/` de gideceği için, burada hem öğrenilen motor kuralları, hem araç
mimarisi, hem de kurulacak dünyanın tam ülke listesi var.

---

## ⚠ Önce bunu oku

Bu dosya **untracked**'dir. `git checkout .` veya `git reset --hard` ona
dokunmaz, ama **`git clean -fd` siler.** Discard ederken `git clean` kullanacaksan
önce bu dosyayı repo dışına kopyala. Bir kopyası şurada duruyor:

```
Victoria 3\TGC_YENIDEN_KURULUM.md
```

---

## 0. Neden yeniden kuruyoruz

Teknik sebep tek bir hataydı ve bulundu (§3). Asıl sebep süreçti:

> **Altı kıta, 171 ülke, 675 state ve dört yeni din, oyun bir kez bile
> başarıyla açılmadan üst üste yazıldı.**

Hata ortaya çıktığında onu üretebilecek yüzlerce değişiklik birikmişti. Dokuz
crash ve dört gün tek bir sebebi ayıklamaya gitti. Yeni planın tek kuralı budur:

> **Her fazın sonunda oyun açılır. Açılmıyorsa bir sonraki faza geçilmez.**

Bir faz 20 state ekliyorsa ve oyun çöküyorsa, şüpheli 20 state'tir — 675 değil.

---

## 1. Discard sonrası elde ne kalıyor

Commit'lerde **yalnızca 19 dosya** var. Bunlardan işe yarayan ikisi:

| Dosya | Durum |
|---|---|
| `senaryo.md` | **Korunur.** Senaryonun ana metni. |
| `states.md` | **Korunur.** Eski state notları. |
| `.idea/*`, `.metadata/metadata.json` | Korunur. metadata temiz (`replace_paths` yok). |

Kalan 11 commit'li dosya **araç öncesi, yarım kalmış içerik** ve **silinmeli**:

```
common/country_definitions/tgc_balkans.txt
common/history/states/tgc_balkans_states.txt
common/history/states/tgc_central_asia_siberia_states.txt
common/history/states/tgc_east_europe_states.txt
common/history/states/tgc_india_states.txt
common/history/states/tgc_middle_east_states.txt
common/history/states/tgc_north_america_states.txt
common/history/states/tgc_south_europe_states.txt
common/history/states/tgc_west_europe_states.txt
localization/english/replace/countries_l_english.yml
localization/english/tgc_countries_l_english.yml
```

**Neden silinmeli:** commit'li `metadata.json`'da `replace_paths` yok. O yüzden
bu state dosyaları vanilla'yı ezmiyor, vanilla'nın **üstüne ekleniyor** — aynı
state iki kez sahipleniliyor. `tgc_balkans.txt` ise `REPLACE_OR_CREATE` öneki
taşımadığı için vanilla tag'lerini ezemez, sessizce atılır. İkisi de aracın
çözmek için yazıldığı hataların ta kendisi.

**Kaybedilecekler (bilinçli karar):** `tools/`, `world/`, `senaryo_amerika.md`,
`senaryo_afrika.md`, `CLAUDE.md`, `_vic3-modding-guide/`. Amerika ve Afrika
kurgusunun özeti Faz 7 ve Faz 8'de, ülke listesi §6'da duruyor.

---

## 2. Motor kuralları

Belgenin en değerli kısmı. Hepsi oyunla doğrulandı; hiçbiri tahmin değil.

### 2.1 `replace_paths` — en tehlikeli ayar

`.metadata/metadata.json` → `game_custom_data.replace_paths`, listelenen dizinin
**vanilla içeriğini tamamen siler**.

- Mod o dizini doldurmuyorsa, o içerik dünyada **hiç kalmaz**.
- Bir kez `common/history/military_formations` ve `common/history/characters`
  buraya "kendi içeriğimiz yazılana kadar" diye eklendi, içerik hiç yazılmadı.
  Sonuç: **hiçbir ülkenin ordusu ve hiçbir ülkenin hükümdarı olmayan dünya.**
- Kural: bir dizin buraya ancak mod onu gerçekten dolduruyorsa eklenir.

Yalnızca üretilen üç dizin listelenmeli:

```json
"replace_paths": [
  "common/history/states",
  "common/history/pops",
  "common/history/buildings"
]
```

### 2.2 Her dizinin override semantiği farklı — genelleme yapma

| Dizin | Mekanizma |
|---|---|
| `common/history/{states,pops,buildings}` | **Çalıştırılan script.** Farklı isimli dosyalar birbirini ezmez, **hepsi çalışır**. Vanilla'yı susturmanın tek yolu `replace_paths`. |
| `common/history/{diplomacy,military_formations,countries,population}` | Çalıştırılan script, ama **aynı isimli dosya vanilla'yı değiştirir**. Süzülmüş kopya yazmanın doğru yolu; `replace_paths` gerekmez. |
| `common/country_definitions` | **Keyed veritabanı.** Farklı dosyada aynı anahtar **sessizce atılır** (`Duplicated key TUR will not be created`). `REPLACE_OR_CREATE:TAG` öneki şart. |
| `common/coat_of_arms` | Keyed veritabanı ama `REPLACE_OR_CREATE` **yok**. Vanilla "sonra yüklenen kazanır"a güveniyor → dosya adı `zzz_` ile başlamalı. |
| `common/on_actions` | Keyed veritabanı, **birleşmez**. Kendi dosyanda `on_game_started_after_lobby` tanımlarsan sessizce atılır. JE eklemek için `common/history/countries` kullan. |
| `map_data/state_regions` | Ne biri ne öbürü. Tek state değişse bile **o vanilla dosyanın tamamı** yeniden üretilmeli. |

### 2.3 `decentralized` ülkeler — crash'in sebebi buydu

- **Bina yazılamaz.** Vanilla'nın tüm kurulumunda decentralized bir ülkeye ait
  tek bir bina yoktur (sayıldı: tam sıfır). Motor bu ülkeler için bina ve inşaat
  yapılarını **hiç tahsis etmez**; yazmak tahsis edilmemiş diziye yazmaktır ve
  açılışta `0xC0000005` **yazma** ihlaliyle çöker. Hiçbir log satırı sebebi
  söylemez.
- **Tuzak:** bir state decentralized bir ülkeye geçtiğinde `buildings: inherit`
  vanilla'nın binalarını olduğu gibi kopyalar. Üretici bunu elemeli.
- Pop **verilebilir** — vanilla 154 decentralized ülkeye pop veriyor, normaldir.
- Teknoloji **verilebilir** — vanilla ~150 tanesine veriyor.
- Journal entry **verilemez** (`has_events = no`).

### 2.4 Tabiiyet tipi `country_type`'a bağlı

| Metbu `country_type` | Geçerli `subject_type` |
|---|---|
| `unrecognized` | `vassal`, `tributary` |
| `recognized` | `puppet`, `protectorate`, `personal_union` |
| `colonial` | `colony`, `dominion` |

Yanlış eşleşme sessizce çalışmaz.

### 2.5 Başkent zorunlu ve doğrulanmalı

- Toprağı olan **her** ülkenin başkenti, sahip olduğu bir state olmalı. Değilse
  `Event target link 'capital' returned an invalid object` ve crash riski.
- Yalnızca kendi ülkelerin için değil, **yeniden dağıtımın etkilediği vanilla
  ülkeleri için de**. Bir kez 19 ülkede bu hata vardı.
- Vanilla `common/history/countries` içindeki `set_capital` / `set_market_capital`
  çağrıları da denetlenmeli — `country_definitions` denetimi onları görmez.
  Örnek: `CHI`'nin pazar başkenti Guangdong, senaryoda `YUE`'nin oluyor.

### 2.6 Topraksız ülke = diplomasi çöküşü

Yeniden dağıtım vanilla'nın birçok ülkesini topraksız bırakır (ABD, Meksika,
Brezilya, İspanya, Portekiz, Prusya, Doğu Hindistan Şirketi...). Vanilla hâlâ
onlar arasında ilişki kurmaya çalışır:

```
[pdx_assert.cpp:637]: Assertion failed:
Attempted to create relations for invalid countries!
```

Diplomasi üreticisi **her kaydın iki tarafının da toprağı olduğunu** doğrulamalı.
Bir kez 113 kayıt 23 ölü ülkeye işaret ediyordu.

`add_liberty_desire` tabiiyet paktı olmayan ülkede çalışmaz
(`Subject Pact not found`) — pakt düşerse liberty satırı da düşmeli.

### 2.7 Yeni dinler motorda ikinci sınıf

Vanilla'nın 17 dini için motor `state_<din>_standard_of_living_add` modifier
tipini otomatik üretir; **moddan eklenen dinler için üretmez.** O yüzden:

- `<din>_standard_of_living_modifier_positive` / `_negative` static modifier'ları
  **tanımlanmalı** (yoksa `Missing religion sol static modifier`),
- ama **gövdeleri boş olmalı** — `state_<din>_standard_of_living_add` kullanmak
  `Unknown modifier type` verir.

Dinlerin kendisi crash sebebi değil; daraltmayla elendi.

### 2.8 `unlisted: inherit` pop dönüşümünü atlar

Kaynakta **yazmayan** bir state vanilla pop'larını **ham** alır; ülkenin
`religion_split` / `culture_map` dönüşümü uygulanmaz. Britanya'nın %66 Protestan
kalmasının sebebi buydu. Dönüşüm isteniyorsa state açıkça listelenmeli.

### 2.9 Diğer notlar

- Teknoloji **toplamalıdır** (`add_technology_researched`): yükseltmek güvenli,
  düşürmek imkânsız. Okuryazarlık **atamadır** (`set_pop_literacy`): vanilla ile
  yarışır, aynı isimli dosya ile ezilmeli.
- Vanilla `dynamic_country_names` ülke adını ezer (`dyn_c_iran`,
  `dyn_c_great_qing`, `dyn_c_ottoman_empire`). En temiz çözüm localization
  anahtarını ezmek.
- `add_prestige` diye bir efekt **yok**; prestij yalnızca modifier ile verilir.
- JE açıklama anahtarı `_reason`'dır, `_desc` değil.
- Armasız ülke crash **etmez** — vanilla `03_random.txt` ile rastgele üretir.
- Tag çakışmasına dikkat: `DYB` vanilla'da Avustralya aborjin tag'idir
  (Diyarbakır sanıp kullanınca haritada "Dyribal" çıktı). Kürt/Musul için `KUR`.
- **Vanilla'nın kendi verisinde de tutarsızlık var** (aynı province iki ülkede,
  olmayan binaya sahiplik). Vanilla'da olan bir şey hata değildir; her bulguyu
  **vanilla ile karşılaştır** — yoksa saatler yanlış izde geçer.

---

## 3. Crash teşhisi — tekrar lazım olacak

Log'lar sebebi söylemedi. Sebep minidump'tan çıktı.

1. `crashes/<klasör>/minidump.dmp` → **Exception stream (tip 6)**:
   - `ExceptionCode` → `0xC0000005` erişim ihlali
   - `ExceptionInformation[0]` → `0` okuma / `1` **yazma**
   - `ExceptionInformation[1]` → erişilmeye çalışılan adres
2. **ModuleList (tip 4)** ile `victoria3.exe` tabanını al, crash adresinden çıkar
   → **RVA**. Aynı RVA = aynı hata. (Bizimki hep `0xC03167` idi.)
3. **MemoryList (tip 5)** + thread context ile register'ları oku; hangi dizinin
   hangi ofsetine yazıldığını gör.

Ayrımı yapan tespit şuydu: **null pointer değil, geçerli bir dizi tabanına sabit
ofsetle yazma.** Yani "bozuk veri" değil, "taşıyamayacak yere yazılmış geçerli
veri" — ve doğrudan decentralized binalara götürdü.

Bu script'i erken yaz: `tools/crashinfo.py`.

### Yol üstünde bulunan diğer gerçek hatalar

| Hata | Belirti |
|---|---|
| Boş `replace_paths` | Ordusuz, hükümdarsız dünya |
| Topraksız ülkelere diplomasi | `invalid countries` assert'i |
| 19 ülkede geçersiz başkent | `capital returned an invalid object` |
| Bina sanitizer'ı sahipsiz blok bırakıyordu | 360 script hatası |
| Geçersiz din modifier tipleri | 8 `Unknown modifier type` |
| `DYB` tag çakışması | Diyarbakır "Dyribal" görünüyordu |

---

## 4. Araç mimarisi — yeniden kurulacak

Elle yazılan oyun dosyaları yönetilemez hale geldi; kaynak-üretici mimarisi
doğruydu ve tekrar kurulmalı.

```
world/*.yml  --( python tools/tgc.py build )-->  common/history/{states,pops,buildings}
                                                 common/country_definitions/
                                                 common/history/{diplomacy,military_formations}
                                                 localization/
```

**Komutlar:** `build` (üret), `check` (doğrula), `find <ad>` (state ara),
`show <state>` (state incele), `map --mode political|reference` (harita çiz),
`index` / `geo` (vanilla'dan önbellek üret).

**`world/` şeması:**

```yaml
# world/states/04_subsaharan_africa.yml
STATE_ZULULAND: {owner: ZUL, pops: inherit, buildings: inherit}
STATE_MERZ:                       # bölünmüş state
  split:
    - {owner: KHO, provinces: [x6598F7, x6CF557]}
    - {owner: BUK, rest: true}
  pops: inherit
  buildings: inherit
```

```yaml
# world/countries/tgc_rum.yml
TUR:
  color: [40, 84, 160]
  country_type: recognized        # recognized|unrecognized|colonial|decentralized
  tier: empire                    # empire|kingdom|grand_principality|principality|city_state|hegemony
  cultures: [turkish]
  religion: mujtahidiyya
  tech_tier: 1
  literacy: high
  capital: STATE_EASTERN_THRACE
  name: Empire of Rum
  adjective: Rumi
  name_tr: "Rûm İmparatorluğu"
  religion_map: {sunni: mujtahidiyya}          # vanilla dinini çevir
  religion_split: {orthodox: {mujtahidiyya: 0.35, orthodox: 0.65}}
  culture_religion_split: {...}                # yerleşimci/yerli ayrı dağılım
  overlord: TUR                                # tabiiyse
  subject_type: puppet
  liberty_desire: 15
```

**`check` en baştan şunları doğrulamalı** (hepsi gerçek crash'ten öğrenildi):

1. Toprağı olan her ülkenin başkenti sahip olduğu bir state mi
2. Diplomasi kayıtlarının iki tarafı da toprağa sahip mi
3. `decentralized` ülkeye bina yazılmış mı
4. `replace_paths`'te beyan edilip modda boş bırakılmış dizin var mı
5. `subject_type` ↔ `country_type` uyumu
6. Aynı province birden fazla sahipte mi
7. Kültür / din / pop_type / bina / production method gerçekten var mı
8. Yinelenen localization anahtarı var mı

---

## 5. Faz planı

Her fazın sonunda değişmez iki adım:

```bash
python tools/tgc.py build && python tools/tgc.py check
```

**ve oyunu aç.** `check` 0 hata vermeli **ve** oyun 1836'ya girmeli. İkisinden
biri olmuyorsa faz bitmemiştir.

| Faz | Kapsam | Ülke |
|---|---|---|
| 0 | Temiz zemin, araç iskeleti | — |
| 1 | Dört mezhep + modifier'lar | — |
| 2 | Çekirdek dört devlet | 4 |
| 3 | Balkanlar, Anadolu, Ortadoğu | 25 |
| 4a | Avrupa: Batı | 19 |
| 4b | Avrupa: Orta ve Güney | 16 |
| 5 | Rusya, Kafkasya, Orta Asya | 15 |
| 6 | Hindistan, Doğu/Güneydoğu Asya | 20 |
| 7 | Afrika | 19 |
| 8 | Amerika | 36 |
| 9 | Diplomasi ağı | — |
| 10 | Ordular, teknoloji, nüfus | — |
| 11 | Armalar, localization | — |
| 12 | Flavor (Üç Minber, JE, event) | — |

Faz ayrıntıları görev listesinde (`/tasks`) duruyor; her görev kendi kabul
kriterini ve o faza özgü motor tuzağını taşıyor.

### Faz 7 ve 8 için kurgu özeti

`senaryo_afrika.md` ve `senaryo_amerika.md` silineceği için özet:

**Afrika.** Sahel'de taklidiyye devletleri (Sokoto, Bornu, Massina, Segu, Wadai,
Darfur) — Kahire'nin nüfuz alanı. Gine Körfezi ve Doğu Afrika'da animist krallıklar
(Aşanti, Oyo, Kongo, Buganda, Merina, Zulu, Xhosa, Basotho, Namaqua). Habeşistan
bölünmüş (Begemder, Şewa). Kuzey Afrika Mısır kufesinde (Cezayir, Tripolitanya,
Tunus, Fas). Umman bağımsız ve İngiltere'ye rakip. Endülüs'ün tek Afrika kolonisi
Gine (`AGU`).

**Amerika.** Katolikler bu evrende Amerika'ya **hiç ulaşmadı**; Müslümanlar ilk
gitti — Katolik nüfus yalnızca yerleşimci kültürlerinde ve düşük oranda olmalı.
Endülüs kolonileri büyük ve bağımsızlık eğilimli (Yeni Endülüs/Meksika, Yeni
Sevilla/Kolombiya, İnci Adaları/Küba). Fas Brezilya ve Arjantin'de. Rûm'un tek
üssü Florida'da Yeni Bursa. Doğu kıyısı İngiliz/Hollandalı/bağımsız
(New England, Virginia, New Netherland, Pennsylvania). Kuzey Kanada İskandinav
(Vinland, Nya Norrland). **Şili, ABD batısı ve Alaska kolonileşmemiş.** İç
kesimler yerli konfederasyonları — çoğu `decentralized`, yani §2.3 burada kritik.

---


---

## 7. Faz ayrıntıları

Her fazın sonunda: `python tools/tgc.py build && python tools/tgc.py check`
**ve oyunu aç.**

### Faz 0 — Temiz zemin ve araç iskeleti
§1'deki 11 commit'li dosyayı sil. `metadata.json` zaten temiz — `replace_paths`
yalnızca gerçekten üretilen dizinler eklendikçe doldurulacak. `tools/` iskeletini
kur (§4): `index`, `geo`, `build`, `check`, `find`, `show`, `map`. `crashinfo.py`
de burada yazılsın (§3).
**Kabul:** mod yüklüyken oyun vanilla gibi 1836'ya giriyor. Karşılaştırma noktası budur.

### Faz 1 — Altyapı: dinler ve iskeletler
Dört mezhep (`common/religions`): mujtahidiyya, irfaniyya, taklidiyya, hikmatiyya.
Her biri için `<din>_standard_of_living_modifier_positive/_negative` — **gövdesi boş**
(§2.7). `zzz_tgc_coats.txt` ve localization iskeletleri. Hiçbir sahiplik değişmez.
**Kabul:** oyun açılıyor, harita tamamen vanilla, log'da `Missing religion sol` ve
`Unknown modifier type` yok.

### Faz 2 — Çekirdek dört devlet
TUR, PER, EGY, ANL. Tanım + başkent + din + kültür + teknoloji + çekirdek state'ler.
Tabiiyet yok, diplomasi yok.
**Kabul:** dördü haritada doğru yerde ve doğru dinde.

### Faz 3 — Balkanlar, Anadolu, Ortadoğu
İlk kez tabiiyet devreye giriyor → §2.4. Balkan kuklaları BOS/ALB/BUL (Müslüman
yönetici + Hristiyan köylü, `religion_split` ile). Atabeylikler ADN/ERZ. Üç tampon
SYR/KUR/BSR. İran federasyonu AZB/KHO/KRM/LUR/MAZ/ARB + KHI/BUK. Arabistan
HDJ/JAB/NEJ/PAL.
**Kabul:** tabiiyet ağacı oyunda doğru; check tabiiyet kurallarında 0 hata.

### Faz 4a — Avrupa: Batı
FRA (Paris Krallığı) + AQU/BRI/BUR/OCC/PRO vassalları. İberya: **"İspanya" diye
devlet yok** — CAS, AGN, GLI, NAV. GBR (**tamamen Katolik**), SCO, NET.
Kalmar: SWE + DEN/NOR/FIN.
Geç Reform: Protestanlık yalnızca İskandinavya ve kuzey Almanya'da; oralarda bile
nüfusun ~üçte biri Katolik. Dönüşümün uygulanması için state'ler **açıkça
listelenmeli** (§2.8).
**Kabul:** Protestan/Katolik dağılımı haritada beklendiği gibi.

### Faz 4b — Avrupa: Orta ve Güney
Katolik kutup BAV (imparatorluk tacı), AUS (küçültülmüş arşidüklük), BOH, WUR,
BAD, RHE, SWI. Protestan kutup SAX, BAN (**Prusya hiç kurulmadı**, Brandenburg
seçmen prensliği kaldı), HAN, HEK, ANH, MEC, POM, SCH. İmparatorluk tabiiyet ağacı
değil, **ilişkiler** üzerinden kurulur — Bavyera unvanı tutar ama prensleri tabi
yapmaz.
İtalya: SIC Sicilya Emirliği + boğazda küçük Rûm şehri, Sardinya Rûm'un, NAP, PAP.
Doğu: PLC, MOL (Polonya'ya bağlı), HUN, TRS (küçük Müslüman kısım), WAL (Rûm'a
bağlı Müslüman).

### Faz 5 — Rusya, Kafkasya, Orta Asya
RUS Moskova Büyük Prensliği (**Rusya birleşmedi**) + NOV/MRD/MRI vassalları.
TAR Büyük Tatar Hanlığı (**Kazak Hanlığı yok**, ona katıldı). CRI, CIR, DAG, GEO,
KLM. XIN Uygur Hanlığı. KHI ve BUK İran'a federe. Sibirya'da vanilla halkları
bozulmadan kalmalı.

### Faz 6 — Hindistan, Doğu ve Güneydoğu Asya
MUG Gurkani + MAR, BGL, AWA, HYD, MYS, PAN, NEP, TIB. Çin **beşe bölünmüş**:
CHI, JGN, SHU, YUE, MCH. Güneydoğu Asya yalnızca hafif dokunuş: ACE, JOH, SUL,
TND, BCE.
**Dikkat:** CHI'nin vanilla pazar başkenti Guangdong artık YUE'nin →
`chi - china.txt` aynı isimle ezilmeli (§2.5).

### Faz 7 — Afrika
**İlk decentralized-yoğun faz — §2.3 burada kritik.** İçerik ve kurgu §5'te.
**Kabul:** check decentralized-bina kuralında 0 hata.

### Faz 8 — Amerika
En çok yeni tag burada, çoğu decentralized → §2.3 yine geçerli. Kurgu §5'te.
**Kabul:** kolonilerde din dağılımı doğru (Katolik oranı düşük ve yalnızca
yerleşimci kültürlerinde).

### Faz 9 — Diplomasi ağı
Rakiplikler, ilişkiler, kalan tabiiyetler. §2.6 zorunlu. `common/history/diplomacy`
**aynı vanilla dosya adlarıyla** yazılmalı — history'de "paktı kaldır" efekti yok,
vanilla'nın senaryoya aykırı paktlarını ancak dosyayı ezerek susturabilirsin.
**Kabul:** üç dosyada topraksız ülkeye 0 referans.

### Faz 10 — Ordular, teknoloji, nüfus
Vanilla `military_formations` dosyalarının **aynı isimle** süzülmüş kopyaları:
topraksız ülkelerin blokları ve ülkenin sahip olmadığı state'e yerleştirilmiş
birlikler atılır; birliği kalmayan teşekkül düşer. **`replace_paths` kullanma**
(§2.1). `common/history/characters` vanilla'ya bırakılır — hiç state referansı
taşımıyor. Teknoloji toplamalı, okuryazarlık atama (§2.9).

### Faz 11 — Armalar ve localization
87 arma, `zzz_` önekli dosya (§2.2). Türkçe/İngilizce isimler, `dyn_c_*` ezmeleri
(§2.9). Yinelenen localization anahtarı olmamalı.

### Faz 12 — Flavor
**En son.** Üç Minber krizi, ana devlet hedefleri, scripted trigger/value'lar,
game concept'ler. JE'ler `common/history/countries` altından eklenir (§2.2).
decentralized ülkeye JE verilemez (§2.3).

## 6. Kurulacak dünya — tam ülke listesi

171 ülke. `tek` = teknoloji kademesi (1 en ileri), `okur` = okuryazarlık.
Başkentler `STATE_` öneki atılmış halde.

### Faz 2 — Çekirdek

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `ANL` | State of al-Andalus | LOWER_ANDALUSIA | hikmatiyya | spanish | 1 | very_high | — |

### Faz 2-3 — Rûm ve tabiileri

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `ADN` | Atabegate of Adana | ADANA | mujtahidiyya | turkish | 3 | middling | tributary → TUR |
| `ALB` | Emirate of Albania | ALBANIA | mujtahidiyya | albanian | 3 | low | vassal → TUR |
| `BOS` | Emirate of Bosnia | BOSNIA | mujtahidiyya | bosniak | 3 | middling | vassal → TUR |
| `BSR` | Emirate of Iraq | BASRA | irfaniyya | mashriqi | 3 | middling | protectorate → TUR |
| `BUL` | Emirate of the Danube | BULGARIA | mujtahidiyya | bulgarian | 3 | middling | vassal → TUR |
| `ERZ` | Atabegate of Erzurum | ERZURUM | mujtahidiyya | turkish, armenian, greek | 3 | middling | tributary → TUR |
| `KUR` | Emirate of Kurdistan | MOSUL | mujtahidiyya | kurdish | 4 | low | protectorate → TUR |
| `SYR` | Emirate of Damascus | SYRIA | taklidiyya | mashriqi | 3 | middling | protectorate → TUR |
| `TUR` | Empire of Rum | EASTERN_THRACE | mujtahidiyya | turkish | 1 | high | — |
| `YEN` | New Bursa | FLORIDA | mujtahidiyya | turkish | 3 | middling | colony → TUR |

### Faz 2-3 — İran Konfederasyonu

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `ARB` | Emirate of Khuzestan | KHUZESTAN | irfaniyya | mashriqi | 3 | low | tributary → PER |
| `AZB` | Khanate of Tabriz | TABRIZ | irfaniyya | azerbaijani | 2 | high | tributary → PER |
| `BUK` | Emirate of Bukhara | UZBEKIA | mujtahidiyya | uzbek, tajik | 3 | middling | tributary → PER |
| `KHI` | Khanate of Khiva | KHIVA | mujtahidiyya | uzbek, turkmen | 3 | low | tributary → PER |
| `KHO` | State of Khorasan | KHORASAN | irfaniyya | persian | 2 | high | tributary → PER |
| `KRM` | Emirate of Kerman | KERMAN | irfaniyya | persian | 3 | middling | tributary → PER |
| `LUR` | Luristan | LURISTAN | irfaniyya | luri | 3 | low | tributary → PER |
| `MAZ` | Shahdom of Mazandaran | MAZANDARAN | irfaniyya | mazanderani | 3 | middling | tributary → PER |
| `PER` | Shahdom of Isfahan | ISFAHAN | irfaniyya | persian | 1 | very_high | — |

### Faz 2-3 — Mısır kufesi

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `EGY` | Sultanate of Egypt | LOWER_EGYPT | taklidiyya | misri | 2 | middling | — |
| `HDJ` | Sharifate of Hejaz | HEDJAZ | taklidiyya | bedouin | 4 | low | tributary → EGY |
| `JAB` | Emirate of Jabal Shammar | HAIL | taklidiyya | bedouin | 5 | baseline | — |
| `MAS` | Emirate of Algiers | ALGIERS | sunni | maghrebi | 4 | low | — |
| `MOR` | Sultanate of Morocco | FEZ | taklidiyya | maghrebi | 3 | low | — |
| `NEJ` | Emirate of Nejd | NEJD | taklidiyya | bedouin | 5 | baseline | — |
| `PAL` | Emirate of Jerusalem | PALESTINE | taklidiyya | mashriqi | 4 | low | — |
| `TRI` | Emirate of Tripolitania | TRIPOLI | taklidiyya | maghrebi, bedouin | 4 | baseline | — |
| `TUN` | Beylik of Tunis | TUNISIA | taklidiyya | maghrebi | 4 | low | — |

### Faz 4a — Avrupa: Batı

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `AGN` | Crown of Aragon | ARAGON | catholic | catalan | 3 | middling | — |
| `AQU` | Aquitaine | AQUITAINE | catholic | occitan | 4 | low | vassal → FRA |
| `BRI` | Brittany | BRITTANY | catholic | breton | 4 | low | vassal → FRA |
| `BUR` | Burgundy | BURGUNDY | catholic | french | 3 | middling | vassal → FRA |
| `CAS` | Kingdom of Castile | OLD_CASTILE | catholic | spanish | 4 | low | — |
| `FRA` | Kingdom of Paris | ILE_DE_FRANCE | catholic | french | 3 | middling | — |
| `GBR` | Great Britain | HOME_COUNTIES | catholic | british, scottish | 1 | high | — |
| `GLI` | Kingdom of Galicia | GALICIA | catholic | galician, portuguese | 4 | low | — |
| `HUN` | Kingdom of Hungary | CENTRAL_HUNGARY | catholic | hungarian | 4 | low | — |
| `MOL` | Principality of Moldavia | MOLDAVIA | orthodox | romanian | 4 | low | vassal → PLC |
| `NAP` | Kingdom of Naples | CAMPANIA | catholic | south_italian | 4 | low | — |
| `NAV` | Navarre | BASQUE_COUNTRY | catholic | basque | 5 | low | — |
| `NET` | Netherlands | HOLLAND | catholic | dutch | 2 | high | — |
| `OCC` | Occitania | LANGUEDOC | catholic | occitan | 4 | low | vassal → FRA |
| `PAP` | Papal States | LAZIO | catholic | north_italian, south_italian | 4 | middling | — |
| `PRO` | Provence | PROVENCE | catholic | occitan | 4 | low | vassal → FRA |
| `SCO` | Kingdom of Scotland | LOWLANDS | catholic | scottish, scottish_gaelic | 2 | high | — |
| `SIC` | Emirate of Sicily | SICILY | mujtahidiyya | maltese, south_italian | 3 | middling | — |
| `WAL` | Emirate of Wallachia | WALLACHIA | mujtahidiyya | romanian | 4 | low | vassal → TUR |

### Faz 4b — Almanya

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `ANH` | Anhalt | ANHALT | protestant | north_german | 4 | middling | — |
| `AUS` | Archduchy of Austria | AUSTRIA | catholic | south_german | 4 | low | — |
| `BAD` | Baden | BADEN | catholic | south_german | 4 | middling | — |
| `BAN` | Electorate of Brandenburg | BRANDENBURG | protestant | north_german | 4 | middling | — |
| `BAV` | Kingdom of Bavaria | BAVARIA | catholic | south_german | 3 | middling | — |
| `BOH` | Kingdom of Bohemia | BOHEMIA | catholic | czech, south_german | 3 | middling | — |
| `HAN` | Kingdom of Hannover | HANNOVER | protestant | north_german | 3 | high | — |
| `HEK` | Hesse | HESSE | protestant | north_german | 4 | middling | — |
| `MEC` | Mecklenburg | MECKLENBURG | protestant | north_german | 5 | middling | — |
| `POM` | Pomerania | POMERANIA | protestant | north_german | 5 | middling | — |
| `RHE` | Rhineland | NORTH_RHINE | catholic | north_german | 3 | middling | — |
| `SAX` | Kingdom of Saxony | SAXONY | protestant | north_german | 3 | high | — |
| `SCH` | Schleswig-Holstein | SCHLESWIG_HOLSTEIN | protestant | north_german, danish | 4 | high | — |
| `SWI` | Switzerland | WEST_SWITZERLAND | catholic | alemannic, francoprovencal | 3 | high | — |
| `WUR` | Kingdom of Wurttemberg | WURTTEMBERG | catholic | south_german | 4 | middling | — |

### Faz 4b — Lehistan

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `PLC` | Polish-Lithuanian Commonwealth | MAZOVIA | catholic | polish, lithuanian | 2 | high | — |

### Faz 5 — Rusya ve Kalmar

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `DEN` | Denmark | ZEALAND | protestant | danish | 2 | very_high | personal_union → SWE |
| `FIN` | Grand Duchy of Finland | UUSIMAA | protestant | finnish, swedish | 3 | high | vassal → SWE |
| `MRD` | Mordvin Principality | TAMBOV | orthodox | mordvin | 5 | very_low | vassal → RUS |
| `MRI` | Mari Principality | CHUVASHIA | orthodox | mari | 5 | very_low | vassal → RUS |
| `NOR` | Norway | EASTERN_NORWAY | protestant | norwegian | 3 | high | personal_union → SWE |
| `NOV` | Republic of Novgorod | NOVGOROD | orthodox | russian | 4 | low | vassal → RUS |
| `RUS` | Grand Principality of Moscow | MOSCOW | orthodox | russian | 4 | very_low | — |
| `SWE` | Kalmar Union | SVEALAND | protestant | swedish | 2 | very_high | — |

### Faz 5 — Kafkasya ve Tatarlar

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `CIR` | Circassian Confederation | KUBAN | sunni | circassian | 4 | baseline | — |
| `CRI` | Crimean Khanate | CRIMEA | sunni | tatar | 3 | middling | — |
| `DAG` | Imamate of Dagestan | DAGESTAN | sunni | north_caucasian, chechen | 4 | baseline | — |
| `GEO` | Kingdom of Georgia | GREATER_CAUCASUS | orthodox | georgian, armenian | 3 | low | — |
| `KLM` | Kalmyk Khanate | KALMYKIA | gelugpa | kalmyk | 5 | baseline | — |
| `TAR` | Great Tatar Khanate | KAZAN | sunni | tatar, bashkir, kazak | 3 | middling | — |

### Faz 5 — Uygur

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `XIN` | Uyghur Khanate | TIANSHAN | mujtahidiyya | uighur, han | 2 | high | — |

### Faz 6 — Hindistan ve Güneydoğu Asya

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `ABU` | Emirate of Abu Dhabi | ABU_DHABI | sunni | bedouin | 5 | baseline | — |
| `ACE` | Sultanate of Aceh | ACEH | taklidiyya | sumatran | 5 | low | — |
| `AWA` | Awadh | AWADH | sunni | avadhi | 4 | low | — |
| `BGL` | Sultanate of Bengal | EAST_BENGAL | sunni | bengali | 3 | low | — |
| `HYD` | Hyderabad | HYDERABAD | sunni | deccani | 4 | low | — |
| `JOH` | Sultanate of Johor | MALAYA | sunni | malay | 5 | low | — |
| `MAR` | Maratha Confederation | BOMBAY | hindu | marathi, gujarati | 3 | low | — |
| `MUG` | Gurkani Empire | DELHI | mujtahidiyya | hindustani, panjabi | 2 | middling | — |
| `MYS` | Kingdom of Mysore | MYSORE | hindu | kannada | 4 | low | — |
| `NEP` | Kingdom of Nepal | HIMALAYAS | hindu | nepali | 5 | low | — |
| `PAN` | Sikh State | HILL_PUNJAB | sikh | panjabi | 3 | low | — |
| `SUL` | Sultanate of Sulu | MINDANAO | sunni | moro | 5 | baseline | — |
| `TIB` | Tibet | LHASA | gelugpa | tibetan | 6 | low | — |
| `TND` | Rajahnate of Tondo | LUZON | sunni | tagalog, visayan | 5 | baseline | — |
| `UNT` | Maori Confederation | NORTH_ISLAND | animist | maori | 6 | baseline | — |

### Faz 6 — Çin

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `CHI` | Northern Chinese Empire | BEIJING | confucian | han, manchu | 4 | low | — |
| `JGN` | Republic of Jiangnan | NANJING | confucian | han | 2 | middling | — |
| `MCH` | Khanate of Manchuria | SOUTHERN_MANCHURIA | confucian | manchu | 4 | low | — |
| `SHU` | Kingdom of Shu | SICHUAN | confucian | han | 4 | low | — |
| `YUE` | Yue Confederation | GUANGDONG | confucian | yue, hakka | 3 | low | — |

### Faz 7 — Afrika

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `AGU` | Andalusian Guinea | IVORY_COAST | hikmatiyya | kissi, akan | 5 | baseline | colony → ANL |
| `ASH` | Ashanti Empire | GOLD_COAST | animist | akan | 5 | baseline | — |
| `BGM` | Begemder | GONDER | oriental_orthodox | amhara, tigray | 5 | low | — |
| `BOR` | Sultanate of Bornu | BORNU | taklidiyya | kanuri | 5 | low | — |
| `BST` | Basotho Kingdom | VRYSTAAT | animist | sotho | 6 | baseline | — |
| `BUG` | Buganda | UGANDA | animist | baganda | 5 | baseline | — |
| `DFR` | Sultanate of Darfur | DARFUR | taklidiyya | fur, bedouin | 5 | baseline | — |
| `KON` | Kingdom of Kongo | BAS_CONGO | animist | bakongo | 5 | baseline | — |
| `MAD` | Kingdom of Merina | NORTH_MADAGASCAR | animist | malagasy | 5 | baseline | — |
| `MSN` | Massina Empire | EASTERN_MALI | taklidiyya | fulbe | 5 | low | — |
| `NAM` | Namaqua | NAMAQUALAND | animist | khoisan | 6 | baseline | — |
| `OMA` | Sultanate of Oman | OMAN | ibadi | swahili, bedouin | 4 | low | — |
| `OYO` | Oyo Empire | YORUBA_STATES | animist | yoruba | 5 | baseline | — |
| `SGU` | Segu | WESTERN_MALI | taklidiyya | bambara | 5 | baseline | — |
| `SHW` | Shewa | OROMIA | oriental_orthodox | amhara, oromo | 5 | low | — |
| `SOK` | Sokoto Caliphate | HAUSALAND | taklidiyya | hausa, fulbe | 4 | low | — |
| `WAD` | Wadai | WADDAI | taklidiyya | fur | 5 | baseline | — |
| `XHO` | Xhosa Confederacy | EASTERN_CAPE | animist | xhosa | 6 | baseline | — |
| `ZUL` | Zulu Kingdom | ZULULAND | animist | zulu | 5 | baseline | — |

### Faz 8 — Amerika

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `APC` | Apache | ARIZONA | animist | apache | 6 | baseline | — |
| `ARP` | Arapaho | COLORADO | animist | siouan | 6 | baseline | — |
| `ATB` | Athabaskan Peoples | ALASKA | animist | athabaskan | 7 | baseline | — |
| `BCE` | Kingdom of Kandy | CEYLON | theravada | sinhala | 5 | low | — |
| `BNN` | Bannock | IDAHO | animist | paiute | 6 | baseline | — |
| `BOL` | Kingdom of Charcas | LA_PAZ | animist | quechua, south_andean | 5 | low | — |
| `CHE` | Cherokee Nation | TENNESSEE | animist | cherokee | 5 | low | — |
| `CMN` | Comanche | TEXAS | animist | paiute | 6 | baseline | — |
| `CRK` | Muscogee Confederacy | GEORGIA | animist | muskogean | 6 | baseline | — |
| `CTW` | Choctaw Nation | MISSISSIPPI | animist | muskogean | 6 | baseline | — |
| `ECU` | Kingdom of Quito | ECUADOR | animist | north_andean, quechua | 5 | low | — |
| `GNI` | Guarani Confederacy | ALTO_PARAGUAY | animist | guarani | 6 | baseline | — |
| `ILL` | Great Lakes Federation | ILLINOIS | animist | algonquian | 5 | baseline | — |
| `IRO` | Haudenosaunee Confederacy | OHIO | animist | iroquoian | 5 | baseline | — |
| `LKT` | Lakota | SOUTH_DAKOTA | animist | dakota | 6 | baseline | — |
| `MAP` | Mapuche State | SANTIAGO | animist | patagonian | 5 | baseline | — |
| `MAY` | Maya Confederation | YUCATAN | animist | mayan | 5 | baseline | tributary → NAN |
| `MBZ` | Moroccan Brazil | RIO_DE_JANEIRO | taklidiyya | brazilian, maghrebi, afro_brazilian | 4 | low | colony → MOR |
| `MPL` | Moroccan Plate | BUENOS_AIRES | taklidiyya | platinean, maghrebi | 4 | low | colony → MOR |
| `NAN` | New Andalusia | MEXICO | hikmatiyya | nahua, spanish, mexican | 4 | low | dominion → ANL |
| `NEN` | New England | MASSACHUSETTS | protestant | yankee | 3 | high | colony → GBR |
| `NNL` | New Netherland | NEW_YORK | protestant | dutch | 3 | high | colony → NET |
| `NPU` | Kingdom of Cusco | LIMA | animist | quechua, south_andean | 5 | low | — |
| `NSV` | New Seville | CUNDINAMARCA | hikmatiyya | north_andean, spanish | 5 | low | colony → ANL |
| `NW1` | Nya Norrland | NUNAVUT | protestant | norwegian, inuit | 5 | low | colony → SWE |
| `OJI` | Cree Confederacy | MANITOBA | animist | cree | 6 | baseline | — |
| `PAT` | Tehuelche | PATAGONIA | animist | patagonian | 6 | baseline | — |
| `PEN` | Republic of Pennsylvania | PENNSYLVANIA | protestant | north_german, dutch | 3 | high | — |
| `PRA` | Amazonian Peoples | AMAZONAS | animist | amazonian, tupinamba | 7 | baseline | — |
| `PRL` | Pearl Islands | WESTERN_CUBA | hikmatiyya | caribeno, afro_caribeno | 4 | low | colony → ANL |
| `PWN` | Pawnee | NEBRASKA | animist | caddoan | 6 | baseline | — |
| `SEQ` | Sequoyah | OKLAHOMA | animist | cherokee, siouan | 5 | baseline | — |
| `SLS` | Salish Peoples | OREGON | animist | salish | 6 | baseline | — |
| `SW1` | Vinland | QUEBEC | protestant | swedish, franco_canadian | 4 | middling | colony → SWE |
| `UTE` | Great Basin Peoples | UTAH | animist | paiute | 6 | baseline | — |
| `VRG` | Virginia | VIRGINIA | protestant | dixie | 4 | middling | colony → GBR |

### Faz * — Başkent onarımları

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `AJJ` | — | EAST_SAHARA | — | tuareg | — | — | — |
| `BEL` | — | WALLONIA | catholic | wallonian, flemish | — | — | — |
| `DGR` | — | MEKONG | — | khmer | — | — | — |
| `DLM` | — | MAURITANIA | — | bidan | — | — | — |
| `FER` | — | OKHOTSK | — | siberian | — | — | — |
| `FTR` | — | MAURITANIA | — | fulbe | — | — | — |
| `KKI` | — | MANDALAY | — | kachin | — | — | — |
| `KNG` | — | VOLTA | — | kru | — | — | — |
| `KRI` | — | TASMANIA | — | aborigine | — | — | — |
| `KRU` | — | LIBERIA | — | kru | — | — | — |
| `MDK` | — | LIBERIA | — | mande | — | — | — |
| `MNC` | — | ZAMBEZI | — | shona | — | — | — |
| `RGB` | — | TIMBUKTU | — | bidan | — | — | — |
| `TEK` | — | SAHARA | — | berber | — | — | — |
| `TID` | — | CELEBES | — | moluccan | — | — | — |
| `TRS` | — | NORTHERN_TRANSYLVANIA | catholic | szekely, hungarian, romanian | — | — | — |

### Faz * — Diğer

| tag | ad | başkent | din | kültür | tek | okur | tabiiyet |
|---|---|---|---|---|---|---|---|
| `CKC` | — | CHUKOTKA | — | siberian | — | — | — |
