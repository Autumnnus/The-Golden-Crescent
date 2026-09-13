# Faz 1B.1 — Rûm nüfus, eğitim ve kurum önizlemesi

**13 Eylül 2026. Statik tasarım önizlemesi; oynanabilir sürüm değildir.**

Faz 1A'nın 41 eyaletlik sınır ve diplomasi planını içerir. Bu alt faz yalnız Rûm'un doğrudan yönettiği 25 eyalet payını işler. Bağlı devletlerin nüfusu ve Yeni Bursa 27 milyon hedefinin dışındadır. Diğer 452 ülkenin raporu değişmedi.

## Kullanım

Mod kökünde:

```sh
python3 scripts/tools.py atlas preview --scenario scenarios/atlas/phase01b_rum_demography/scenario.json --region RUM,BOS,ALB,BUL,ADA,ERZ,TRB,KUR,BSR,SYR,LEB,PAL,KUW --out build/maps/phase01b-rum.html
```

Kaynak [scenario.json](scenario.json), nüfus kararları [population-plan.json](population-plan.json). Önizleme `build/maps/phase01b-rum.html`. Bu dosya kümülatiftir; 1A'yı ayrıca üzerine uygulamayın.

## Nüfus ve eğitim

25–29 milyon yazılı hedefinin ortası olan **27 milyon** seçildi. Bölgesel yerleşim ağırlıkları bu toplama normalize edildi; bunlar alternatif dünya için yapımcı kararlarıdır, tarihsel nüfus sayımı değildir. Nüfus ağırlıklı okuryazarlık girdisi **%40,18**; hedef %38–44 içindedir. Motorun başlangıç/ilerleme sonucunun ölçümü değildir.

Kültür/din için yeni oranlar uydurulmadı: mevcut ortak nüfus grupları oransal ölçeklenir. Bu, nihai alternatif dünya demografisi değildir. Özellikle eski Britanya/Malta ve köle nüfusu izleri sonraki demografi düzeltmesinde ele alınmalı; bir halkı silerek kölelik temizlenmez. Paylaşılan Adana, Basra, Trabzon ve Erzurum'da değerler yalnız RUM payına uygulanır.

| Eyalet/pay | Nüfus | Eğitim girdisi | Gerekçe |
|---|---:|---:|---|
| STATE_MALTA / RUM | 173,000 | %46 | Deniz ikmali ve yerel zanaat; sınırlı ada taşıma kapasitesi |
| STATE_EASTERN_THRACE / RUM | 2,876,000 | %56 | Başkent, basım ve yüksek eğitim; çevre kırsal alan dahil |
| STATE_CRETE / RUM | 384,000 | %34 | Ada tarımı, kıyı zanaatı ve deniz geçişi |
| STATE_WEST_AEGEAN_ISLANDS / RUM | 173,000 | %40 | Küçük limanlar ve ticaret okuryazarlığı |
| STATE_EAST_AEGEAN_ISLANDS / RUM | 240,000 | %42 | Anadolu limanlarıyla üretim ve ticaret bağları |
| STATE_ATTICA / RUM | 1,151,000 | %43 | Kent zanaatı, liman ve bölgesel idare |
| STATE_THESSALIA / RUM | 1,438,000 | %29 | Tahıl ve kırsal nüfus; okul ağı kentlerin gerisinde |
| STATE_SKOPIA / RUM | 959,000 | %27 | Kara ticaret geçişi; dağ/kır eğitimine erişim sınırlı |
| STATE_MACEDONIA / RUM | 1,342,000 | %43 | Selanik ticareti, basım ve kırsal hinterlant |
| STATE_WESTERN_THRACE / RUM | 863,000 | %32 | Tarımsal ve transit kuşak |
| STATE_IONIAN_ISLANDS / RUM | 288,000 | %43 | Denizcilik ve çok dilli ticaret ağı |
| STATE_PELOPONNESE / RUM | 623,000 | %30 | Tarım ve yerel zanaat ağırlığı |
| STATE_CYPRUS / RUM | 336,000 | %36 | Levant ticareti ve ada tarımı |
| STATE_ALEPPO / RUM | 1,534,000 | %42 | Kent imalatı, Antakya/Lazkiye ticareti ve gıda hinterlandı |
| STATE_BAGHDAD / RUM | 1,438,000 | %47 | Korunmuş akademiler, sulama, nehir ticareti ve kent üretimi |
| STATE_DEIR_EZ_ZOR / RUM | 479,000 | %23 | Fırat geçişi ve sınırlı su/yerleşim kapasitesi |
| STATE_BASRA / RUM | 575,000 | %26 | Yalnız Rûm kuzey payı: Nasıriye/Amara tarımı; Basra kenti hariç |
| STATE_HUDAVENDIGAR / RUM | 2,876,000 | %50 | Bursa–Marmara makineleşmesi, işgücü göçü ve teknik okul |
| STATE_AYDIN / RUM | 2,109,000 | %44 | İzmir limanı, iç ova tarımı ve imalat |
| STATE_KONYA / RUM | 1,534,000 | %35 | Tarihî eğitim merkezi ile geniş kırsal kuşağın ortak ortalaması |
| STATE_KASTAMONU / RUM | 1,534,000 | %38 | Ereğli yakıt/liman zinciri ve kırsal hinterlant |
| STATE_ADANA / RUM | 432,000 | %31 | Yalnız Rûm doğu payı: Aintab imalatı ve geçitler; Adana kenti hariç |
| STATE_TRABZON / RUM | 623,000 | %35 | Yalnız Samsun/Ordu batı payı; Trabzon atabeyliği hariç |
| STATE_ERZURUM / RUM | 431,000 | %24 | Yalnız Van payı; yüksek havza, yerel eğitim ve transit bağımlılığı |
| STATE_ANKARA / RUM | 2,589,000 | %34 | İç Anadolu kent ağı, tarım ve bölgesel üretim |

## H1 hukuk eşlemesi

[Hukuk tasarımındaki](../../../docs/scenario/hukuk_ve_kurumlar.md) H1, aşağıdaki 24 genel kanun grubuna çevrildi. Hindistan kastı ve Japonya Edo grupları Rûm'a eklenmedi. Bunlar yerel oyunun gerçek kimlikleridir.

- `law_monarchy`
- `law_wealth_voting`
- `law_appointed_bureaucrats`
- `law_subjecthood`
- `law_freedom_of_conscience`
- `law_professional_army`
- `law_professional_navy`
- `law_interventionism`
- `law_protectionism`
- `law_land_based_taxation`
- `law_tenant_farmers`
- `law_no_colonial_affairs`
- `law_dedicated_police`
- `law_no_home_affairs`
- `law_public_schools`
- `law_charitable_health_system`
- `law_no_workers_rights`
- `law_restricted_child_labor`
- `law_women_own_property`
- `law_no_social_security`
- `law_no_migration_controls`
- `law_censorship`
- `law_anti_strike_laws`
- `law_slavery_banned`

Eğitim kurumu 2, hayır esaslı sağlık 1, profesyonel polis 1. Kanunların gerektirdiği teknolojiler ve öncülleri mevcut geçici tier 4 tabanına eklendi; bu liste sanayi öncüsü Rûm'un nihai teknolojisi değildir. Kurum bütçesi ve dinamik seviye sınırları henüz motor içinde sınanmadı.

`law_subjecthood` imparatorluk aidiyetini; `law_freedom_of_conscience` korunan fakat eşit olmayan dinî toplulukları temsil eder. Osmanlıya özel görünürlük/etkinlik koşulları olan `law_millet_system` kullanılmadı. Resmî `sunni` kimliği Müçtehidî kurumları tek başına temsil etmez. Kamu okulları motor içinde asimilasyon etkisi taşır; vakıf-kamu karma eğitim modelinin eksiksiz özel mekaniği değildir. Servet oyu geniş eşit oy anlamına gelmez. Çocuk işçiliği sınırlaması ulusal güçlü iş güvenliği veya sosyal güvenlik sistemi anlamına gelmez.

### Açık tutarlılık kapısı: 1811 kölelik kaldırılması

`law_slavery_banned` hedef hukuktur. Kaynak kanunun `on_activate` etkisi köleleri serbest bırakır ve 1825 gün süren yakın zamanda kaldırılma değişkeni kurar. Bu nedenle 1836 başlangıcında sadece kanunu etkinleştirmek, 1811 tarihini doğru temsil ettiğinin kanıtı değildir. Devralınmış ham POP dosyalarındaki köle statüsü de bu alt fazda temizlenmedi. Sonraki alt fazın ilk işi kültür/dini koruyarak özgür nüfus temsili ve başlangıç etkisinin tarihsel uyumunu çözmektir. Bu kapı kapanmadan oynanabilirlik onayı verilmez.

## Kontroller ve sınırları

```sh
python3 scripts/tools.py atlas scenario report scenarios/atlas/phase01b_rum_demography/scenario.json --out build/phase01b/report.json
python3 scripts/tools.py atlas scenario build scenarios/atlas/phase01b_rum_demography/scenario.json --out build/phase01b/generated
python3 scenarios/atlas/phase01b_rum_demography/verify.py
```

[verification.json](verification.json) bu revizyonun kabul kaydıdır. Rapor/üretilmiş paket eşitliği, 27 milyon toplamı, 25 bölge girdisi, 452 ülkenin değişmemesi, sınır/diplomasi/binaların korunması, kanun/kurum eşleşmesi ve yeni uyarı bulunmaması denetlendi. Kültür/din marjinallerinde yuvarlama sapması kontrol edildi; ortak kültür-din-meslek grupları bu alt fazda bağımsız yeniden denetlenmedi. Eski dünya uyarıları devam eder. Oyun çalıştırılmadı; crash güvenliği veya gerçek %40,18 okuryazarlık garantisi verilmez.

## Sonraki somut iş — 1B.2

1. Yukarıdaki 1811 özgürleşme kapısını çöz; Rûm ortak kültür/din gruplarını kaynak ve senaryo hedefleriyle incele.
2. Rûm'un tarım–kömür–demir–alet–tekstil–ulaşım zincirini eyaletlere dağıt; kamu yönetimiyle eğitim/sağlık/polisin bürokrasi maliyetini karşıla.
3. Bu üretim tabanına uygun nihai teknoloji, askerî birlik, donanma ve hükümet IG'lerini kur. Kalıcı yapay clout çarpanını varsayılan çözüm yapma.
4. Bölgedeki diğer 12 ülkeye geç; Basra limanı, Trabzon/Tırnova hub'ları ve Nizam bağlılığının geçici mekaniklerini çöz.
5. Eski TUR/GRE/ION olay/scope kalıntılarını ve ardından motor başlangıcını denetle.

`world/` etkinleştirilmedi. Faz 1B bütünü tamamlanmadı; bu kayıt yalnız 1B.1 tasarım girdilerinin kabulüdür.
