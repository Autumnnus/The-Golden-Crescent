# Yeni AI ajanı için devir notu — 24 Eylül 2026 (demografi tamamlandı)

## Nihai amaç

**The Golden Crescent**, Victoria 3 için 1 Ocak 1836'da başlayan bir alternatif dünya modudur. İslam dünyasının bilimsel ve kurumsal Altın Çağı sürmüş, sanayi devrimi Ortadoğu'da doğmuştur. Avrupa feodal yapıdan daha geç çıkar; Lehistan–Litvanya teknoloji aktarımıyla görece güçlüdür, Moskova Tatar baskısı altında kalır ve Sibirya'ya yayılmış büyük Rusya yoktur. İskandinavya görece gelişmiş kalır. Japonya/Kore büyük ölçüde tanınır; Güneydoğu Asya'da Batılı Hristiyan sömürgecilik yerine Müslüman denizci güçlerin etkisi vardır. Afrika, Amerika ve Asya kendi siyasi ve toplumsal aktörlerine sahiptir. Farklar halkların veya dinlerin doğasından değil, kurumlar, kaynaklar ve tarihsel tercihlerden doğar.

Kullanıcı senaryonun yalnız haritasını değil, **oynanabilir başlangıç dünyasını** ister: sınırlar ve ülkeler; her state/ülke payında nüfus, ortak kültür–din bileşimi ve okuryazarlık; ardından ekonomi, bina, şirket, kanun, teknoloji, çıkar grubu, ordu ve diplomasi. Daha sonra Flavor aracıyla event/journal zincirleri kurulabilir. Kullanıcı işin geniş ama denetlenebilir bölgesel paketlerle ilerlemesini, araç sözdizimiyle oyunun çökmesine neden olacak hataların önlenmesini ve açık ilerleme sayısını önemser.

## Kaynaklar ve araçlar

- Önce kökteki `AGENTS.md` ile [senaryo yetki tablosunu](README.md) oku. Güncel yazılı kanon [ana senaryo](senaryo.md), [dünya atlası](dunya_atlasi.md), bölge belgeleri ve ilgili ülke/ekonomi/hukuk/diplomasi defterleridir. `docs/archive/` ve `docs/scenario/archive/` tarihsel kayıttır.
- Etkin Atlas V2 kaynağı **`world/scenario.yml`**. `common/history/`, üretilen ülke/yerelleştirme dosyaları ve `build/` çıktıları elle düzenlenmez. Harita verisi ve kimlikler için `python3 scripts/tools.py atlas find/show/rules` kullan; kimlik veya province hex değeri tahmin etme.
- Atlas/Flavor uygulaması modun dışında, yerel `vic3-mod-tools` reposundadır. [Araç başlangıcı](../TOOLS.md): `python3 scripts/tools.py doctor`, `python3 scripts/tools.py docs`; oradan harici `docs/WORKFLOWS.md` ve Atlas LLM rehberini oku. Oyun kurulumuna ve loglarına yazma.
- Flavor bu demografi çalışmasının parçası değildir. Flavor planı yapılırsa **tam diyagram sürümüne kullanıcının açık onayı gelmeden** approve/build/install çalıştırma.
- Çalışma ağacı uzun süredir değişik ve birçok faz dizini Git'te henüz izlenmiyor. `git status --short` ile başla; ilgisiz değişiklikleri silme veya resetleme.

## Şu an yapılanlar

1. **Sayısal demografi tamamlandı.** Dilimler **01–28** `scenarios/atlas/demography_phase*/` altında plan, dondurulmuş POP, hazırlık/doğrulama betikleri ve şehir profilleriyle belgelendi. 24 Eylül 2026'da Amerika ([21](../../scenarios/atlas/demography_phase21_north_america/README.md), [22](../../scenarios/atlas/demography_phase22_andalusian_america/README.md), [23](../../scenarios/atlas/demography_phase23_south_america/README.md)), [Rusya–Sibirya](../../scenarios/atlas/demography_phase24_russia_siberia/README.md), [bozkır–Türkistan–Kafkasya](../../scenarios/atlas/demography_phase25_steppe_turkestan_caucasus/README.md), [Ortadoğu–Hindistan](../../scenarios/atlas/demography_phase26_middle_east_india/README.md), [Batı Avrupa](../../scenarios/atlas/demography_phase27_west_europe/README.md) ve [Güney–Doğu Avrupa](../../scenarios/atlas/demography_phase28_south_east_europe/README.md) işlendi. `python3 scripts/demography_progress.py`: **1.046/1.046 pay (%100), 16/16 teknik bölge kapalı.**
2. Kullanıcı kararları (24 Eylül 2026): Kuzey Amerika iç kıtası ile Rus imparatorluk yayılım alanlarında vanilla yerleşimci nüfusu **ölçülü azaltmayla** yerel halklara çevrildi. Dört dar siyasi düzeltme yapıldı: Alaska `ALK` → yeni `VTU`, Teksas `TEX` → yeni `VCD`, Sahalin `ALK` → `AIN`, Tranquebar `DEN` → `TAM`. Province listeleri korunarak sahipler değişti. **Bunlar ve önceki Boer düzeltmesi oyunda sınanmadı.**
3. Etkin dünya **675 kara state'i, 555 kara sahibi ülke**, nüfus **1.079.219.810** (Faz 20 sonunda 1.093.551.034). Bina seviyesi 3.228 (siyasi düzeltmelerde 5 seviye düştü).
4. Son etkin `atlas build` + `atlas check` **0 hata, 25 uyarı**; [siyasi denetim](../../scenarios/atlas/world_political/active_political_audit.py) bütün sonradan yapılmış sahiplik, ülke kültür/din ve kölelik kanunu değişikliklerini açık istisna olarak tanır ve geçer; araç öz testleri **38/38**. Bunlar statik kaynak testidir.
5. Kölelik tutarlılığı: köle POP'u tutan her ülkenin raporunda kölelik kanunu vardır (fazların `verify.py` denetimi). Yazılı hukuk yasaklıyorsa (H7, H9, 1801/1820 ilgaları) köle POP'ları serbest bırakıldı. Yasal saydığı yerlerde (H8/H10) ise ya korundu ya da gerekirse `law_legacy_slavery`, `law_slave_trade` veya `law_debt_slavery` yazıldı.
6. Faz 21–28 betikleri yeniden kullanılabilir: `mix`, `release_slaves`, `slave_mix`/`slave_total`, `replace_planned`, `absorb`, ülke kültür/din/kanun değişiklikleri ve önceki planları sayan kural tabanlı homeland.

7. Mekanik aşama başladı ([plan](MEKANIK_ASAMA_PLANI.md)). Kullanıcı kararıyla sıra M1 → M2 → M0 oldu ve üçü etkinleşti:
   - **M1:** Başlangıç history'si olmayan 159 ülkeye teknoloji kademesi, tam kanun seti ve okul/sağlık/polis kurumu verildi.
   - **M2:** 314 state'in vanilla binası uyarlanarak geri getirildi, az binalı paylara temel ekonomi eklendi (3.228 → 10.254 seviye).
   - **M0:** Atlas kaynağındaki sahiplik, ordu ve diplomasi kalıntıları ile vanilla override'ları temizlendi. Uyarı 14, `check` 0 hata.
   - İkinci oyun testi: okuryazarlık yalnız birkaç ülkede yüksekti, hayat standardı kötüydü. Kullanıcı modun amacını hatırlattı: İslam ülkelerinde okuryazarlık yüksek, diğerlerinde düşük olmalı; Avrupa İslam'ın gerisinde kalmalı.
   - **M1b** ([paket](../../scenarios/atlas/mechanics_m1b_literacy/README.md)): İlk sürüm (çekirdek girdi %64,7, okul 5) üçüncü testte Rûm/İsfahan'ı %70–80'de açtı. 25 Eylül'de yeniden kuruldu. Açılış hedefleri: İsfahan %48, çekirdek %34, orta İslam %25, zayıf İslam %18, Avrupa üst %24, Batı–orta Avrupa %17,5, güney–doğu %11, Doğu Asya %15, geri kalan %8,6. Girdi = hedef − okul katkısı; okul seviyeleri 1–3. Kullanıcı sonucu onayladı; aynı gün İran çevresi (Horasan/Mazenderan %33), Rûm–Mısır komşuları (Levant %30–32, Adana/Trabzon %31, Balkanlar %19–23) ve Fas (%29) birkaç puan yükseltildi. Vanilla `traditional` efektinin serfliği okul kanunu olan ülkede atlanır ([override](../../scenarios/runtime_cleanup/README.md)).
   - **M3-lite** ([paket](../../scenarios/atlas/mechanics_m3_islamic_economy/README.md)): Rûm 1B.2 sanayisi ve İslam dünyasına tüketim öncelikli bina yoğunluğu eklendi (10.250 → 14.398 seviye). `check` 0 hata, 15 uyarı; siyasi denetim geçti; araç testleri 123/123.
   - Dördüncü oyun testi bekleniyor: açılış okuryazarlığı hedeflerden birkaç puan saparsa `mechanics_m1b_literacy/prepare.py` içindeki `boost` kalibre edilir.

## Açık işler ve bilinen sınırlar

- **Sıradaki ana iş üçüncü oyun testi ve tam M3:** M1b/M3-lite sonrası okuryazarlık ve hayat standardı ölçümü, sonra kalan sanayi havzaları ve şirketler. Atlas'ın açık kanunları devralınan `effect_starting_politics_*` efektlerinden önce yazması araç reposunda düzeltilmeli. Mekanik aşamanın kalanı: ekonomi (bina, üretim yöntemi, şirket, altyapı), kanun/teknoloji, çıkar grupları, ordu/donanma. Amerika, Sibirya, Kafkasya ve birçok Afrika/Asya yerel meclisinin **teknoloji, kanun ve binası yok**; yeni nüfus iş/istihdam kapasitesiyle dengelenmedi. Jamaika (190 bin), Hollanda Guyanası (72 bin) ve Fas Brezilyası'nın plantasyon nüfusu ekonomi aşamasında bina ile eşleşmeli.
- Kanun çelişkileri: `SEQ`, `PRG`, `URU`, `PRA`, `SPU` vanilla kölelik/ayrımcılık kanunlarını taşıyor ama köle POP'ları kaldırıldı (H9'a çevrilmeli). Moskova serfliği, Tatar hanlığı ve Avrupa malikâne/lonca düzeni hukuk aşamasında yazılmalı.
- Siyasi/başkent açıkları: Cusco şehir hub'ı `SPU` payında, `VCU` başkenti Arequipa (kanon Cusco). `STATE_NEW_YORK`'un tamamı Yeni Hollanda'da; iç New York Haudenosaunee alanı yalnız nüfus/homeland ile temsil ediliyor. Birçok kurulu hub adı bu evrende anakronik (New York, Washington, St. Petersburg, Yekaterinburg, Santiago, São Paulo...); yerelleştirme kararı açık.
- Kimlik temsil sınırları: Nubyalı, İrfanî/Zerdüşt, Khasi, Tipperah, Tlingit, Lenca, Gê, Charrúa, Mapuçe ve Romanlar için ayrı oyun kültürü yok; geniş karşılıklar faz README'lerinde yazılı.
- Güney Afrika'da `MTB` merkezsiz olduğu için eski `TRN` alanının 5 bina seviyesi düşüyor; `Pretoria`, `Bloemfontein`, `Johannesburg` hub adları anakronik olabilir.
- Oyun içi yeni başlangıç testi (özellikle yeni `VTU`/`VCD` ülkeleri, birleşen Sahalin/Madras payları, yeni kölelik kanunları ve homeland'ler) gerekli.

## Yeni ajanın hemen yapacağı iş

1. `git status --short`, `python3 scripts/tools.py doctor`, `python3 scripts/tools.py docs`, `python3 scripts/demography_progress.py` (100% olmalı) çalıştır; [ekonomi ve toplum](ekonomi_ve_toplum.md), [hukuk ve kurumlar](hukuk_ve_kurumlar.md) ve [siyasi oyun kurulumu](SIYASI_OYUN_KURULUMU.md) belgelerini oku.
2. Kullanıcıyla mekanik aşamanın sırasını netleştir: önce oyun içi yeni başlangıç testi mi, yoksa ekonomi/kanun paketleri mi. Kurulu oyunun ilgili vanilla kaynaklarını (`atlas rules`) salt okunur incele.
3. Mekanik paketleri demografi paketleri gibi bölgesel ve doğrulanabilir kur: aday → `scenario validate/build/report` → hedef dışı alan koruması → etkinleştir → `build`, `check` (0 hata), siyasi denetim, öz test. Üretilen dosyalara elle dokunma.
4. Her paketten sonra kullanıcıya yapılanları, test sınırlarını ve açık maddeleri bildir.

Yeni ajana verilecek kısa görev: **“Bu modda The Golden Crescent alternatif dünyasının Atlas V2 kaynağını kaldığı yerden sürdür. `docs/scenario/DEVIR_NOTU.md` ve kök `AGENTS.md` talimatlarını oku. Sayısal demografi 1.046/1.046 payda tamamlandı; sıradaki iş ekonomi, kanun/teknoloji, çıkar grubu ve ordu başlangıcıdır. Etkin kaynak `world/scenario.yml`; Atlas/Flavor araç kodu ayrı repoda. Aday önizlemesi ve tam doğrulama sonrası etkinleştir; motor test edilmemiş sınırları bildir.”**
