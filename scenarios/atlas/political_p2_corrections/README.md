# P2 — Dördüncü inceleme düzeltmeleri

**25 Eylül 2026 · etkin.** Kullanıcının oyun içi harita incelemesinden sonra yapılan siyasi ve demografik düzeltmeler. Kararlar [plan.yml](plan.yml) dosyasında, sıfat tablosu [adjectives.yml](adjectives.yml) dosyasında ([adjectives.py](adjectives.py) üretir).

## Sınır ve ülke değişiklikleri

| Değişiklik | Ayrıntı |
|---|---|
| **Vologda (`STATE_GALICH`)** | Lehistan → Moskova. Siyasi kart 12, vanilla'daki Kostroma bölgesi "Galich"i Galiçya (Halyç) sanmıştı; Moskova'nın kuzeyinde kopuk bir Lehistan toprağı oluşmuştu. |
| **Kürdistan kaldırıldı** | Diyarbakır → Rûm. `KUR` etiketi Musul'da bağımsız **Musul Emirliği** olarak kalır (ana kültürler Kürt ve Maşriki). Bağdat 1804 garantisi artık Musul Emirliği'ne geçer. |
| **Kuzey Trakya** | Tuna Emirliği → Rûm (doğrudan yönetim). |
| **Paris** | Burgonya'dan Lorraine ve Franche-Comté, Akitanya'dan Poitou-Saintonge alındı. Paris 11,9 → 15,7 M; Burgonya 5,6 M, Akitanya 3,6 M. |
| **Yeni Endülüs** | Río Grande, Durango, Chihuahua, Sinaloa ve Sonora: 2 → 7 state. Merkezsiz Aridoamerika meclisleri (VSR, VDR, VNP, VSO) toprağını yitirdi. |
| **Yeni Gırnata (`VGZ`, yeni koloni)** | Louisiana, Arkansas ve Teksas'ın Caddo payı (Komançi payları kalır). Endülüs'e sömürge şartıyla bağlı. Yeni İşbiliye'nin kademesi, kanunları ve kurumları; Yeni Endülüs'ün 1801 kölelik yasağı. Louisiana'daki vanilla şeker plantasyonu köle yöntemi yerine ücretli emekle çalışır. |
| **İnci Adaları** | Haiti'den Santo Domingo (kanonda Hispanyola İnci Adaları'nın parçası); Haiti bağımsız kalır. |
| **Yeni İşbiliye** | Venezuela'dan Zulia (Maracaibo) ve Miranda (Caracas). Venezuela iç Bolívar'da kalır, başkenti oraya taşındı. |
| **Rûm'un yeni bağlıları** | Sırbistan ve Kırım Hanlığı (özerk bağlılık). Liste [D2 planında](../diplomacy_d2_subjects/plan.yml). |

Sahibi değişen paylar nüfusu, okuryazarlığı, kompozisyonu ve açık sanayisiyle birlikte taşınır. Yeni sahibin teknoloji ve kanunlarına uymayan bina yöntemleri aynı gruptaki kullanılabilir yönteme çevrilir. Eski sahibin kayıtları kaynak dünyanın derlemesinden (`build/scenarios/p2-source`) okunur. Toprağı kalmayan beş merkezsiz meclis rapordan düşer: 555 → 551 ülke.

## Sıfatlar

Senaryonun adlandırdığı 175 ülkenin hiçbirinde sıfat (`TAG_ADJ`) yoktu. Oyun bağlı ve dinamik adları "üst devlet sıfatı + state" biçiminde kurduğu için Van'da "RUM_ADJ Erzurum" gibi ham anahtarlar görünüyordu. Başlıca 118 ülkenin sıfatı elle yazıldı (Rumi/Rûm, Isfahani/İsfahan, Parisian/Paris...). Geri kalanlarda yönetim sözcükleri atılmış yer adı kullanılır.

## Balkan demografisi ("güçlü")

| State | Türk | Müslüman |
|---|---:|---:|
| Selanik (Makedonya) | %19 → **%45** | %23 → **%58** |
| Üsküp | %20 → **%45** | %36 → **%65** |
| Batı Trakya | %37 → %55 | %38 → %65 |
| Doğu Trakya | %58 → %72 | %62 → %78 |
| Kuzey Trakya | %32 → %50 | %36 → %60 |
| Teselya | %8 → %20 | %9 → %32 |
| Girit | %28 → %40 | %28 → %45 |
| Attika | %6 → %15 | %6 → %20 |
| Doğu / Batı Ege adaları | %17 / %6 → %28 / %15 | %17 / %6 → %30 / %18 |
| Bağlılar (Müslüman) | Bulgaristan ve Dobruca %24 → %39; Bosna %35 → %50; Kosova %63 → %78; Arnavutluk %80 → %90; Sırbistan %14 / %10 → %29 / %25 | |

Toplam nüfus aynı kalır. Diğer Müslüman gruplar (Arnavut, Boşnak, Pomak) Müslüman hedefine ölçeklenir, gayrimüslimler oranla küçülür. Türklerin %10'u aştığı Teselya, Attika ve Batı Ege'de Türk homeland'i eklendi.

## Doğrulama

[verify.py](verify.py) şunları denetler:
- pay toplamları ve okuryazarlık korunmuş, state nüfusları değişmemiş;
- kompozisyon yalnız Balkan planında değişmiş ve hedefte;
- aktarımlar raporda doğru sahipte;
- sıfatlar yazılmış;
- bağlılık ağı D2 planına eşit;
- dokunulmayan ülkelerin içeriği aynı;
- yeni uyarı yok. İzin verilen tek istisna Haiti ve Venezuela'nın kaybettikleri state'lerdeki vanilla birliklerinin kaldırılması notu.

[M1b hazırlayıcısı](../mechanics_m1b_literacy/prepare.py) aktarımları tanır: taşınan pay eski sahibinin katsayısını korur, M1b yeniden çalıştırıldığında P2 dünyası bire bir üretilir.

Etkinleştirme sonrası: `check` 0 hata, 16 uyarı; siyasi denetim geçti; araç testleri 123/123. Oyunda sınanmadı.

```sh
cp world/scenario.yml build/political/p2-source.yml; cp build/world-political/active-political-report.json build/political/p2-source-report.json
python3 scripts/tools.py atlas scenario build build/political/p2-source.yml --out build/scenarios/p2-source
python3 scenarios/atlas/political_p2_corrections/adjectives.py
python3 scenarios/atlas/political_p2_corrections/prepare.py
python3 scripts/tools.py atlas scenario validate build/political/p2-candidate.yml
python3 scripts/tools.py atlas scenario build build/political/p2-candidate.yml --out build/scenarios/p2-candidate
python3 scenarios/atlas/political_p2_corrections/verify.py
```
