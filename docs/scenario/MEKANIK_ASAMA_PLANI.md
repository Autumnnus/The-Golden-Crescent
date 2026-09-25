# Mekanik aşama planı — kurumlar, eğitim, ekonomi ve log temizliği

**24 Eylül 2026 · Kullanıcı kararı: sıra M1 → M2 → M0, teknoloji kanondaki sınıflara göre. M1 ([paket](../../scenarios/atlas/mechanics_m1_institutions/README.md)), M2 ([paket](../../scenarios/atlas/mechanics_m2_economy/README.md)) ve M0 ([Atlas düzeltmeleri](../../scenarios/atlas/mechanics_m0_cleanup/README.md), [vanilla override'ları](../../scenarios/runtime_cleanup/README.md)) etkin. İkinci oyun testinden sonra M1b ([İslam önceliğiyle okuryazarlık](../../scenarios/atlas/mechanics_m1b_literacy/README.md)) ve M3-lite ([İslam dünyasının tüketim ekonomisi](../../scenarios/atlas/mechanics_m3_islamic_economy/README.md), Rûm 1B.2 dahil) de etkinleşti; üçüncü oyun testi bekleniyor. Sırada tam M3 (diğer sanayi havzaları, şirketler).** Sayısal demografi 1.046/1.046 payda tamamlandı ve ilk oyun testinde nüfus, kültür–din, köle ve homeland katmanları planla birebir görüldü. Aynı test üç sorunu gösterdi: okuryazarlık neredeyse her yerde düşük, hayat standardı birçok ülkede çok kötü (tahıl ve giyim çok pahalı), açılış logunda ~630 script hatası var. Bu belge bunların nedenini ölçer ve paket sırasını önerir.

## 1. Ölçülen durum (etkin `world/scenario.yml`)

| Grup | Ülke | Nüfus |
|---|---:|---:|
| Teknoloji yok, kanun yok, bina yok | 154 | 668,5 M |
| Teknoloji yok, kanun var (vanilla kalıntısı), bina yok | 70 | 39,9 M |
| Teknoloji var, bina yok | 125 | 23,1 M |
| Teknoloji, kanun ve bina var (vanilla history devralan etiketler) | 186 | 279,1 M |

- Siyasi kurulumda yeni kurulan ülkelerin (`V*` ve yeniden tanımlanan etiketler) hiçbirine teknoloji, kanun, kurum veya bina yazılmadı. Bu gruba Rûm (27 M, tek bina), Jiangnan (150 M), Kuzey Çin, Yue, Bengal, Lehistan–Litvanya, Endülüs, Moskova, Maratha, İngiltere, Paris, Bohemya, İsfahan da dahil.
- Etkin dünyada **3.228 bina seviyesi** var; vanilla başlangıcında yaklaşık 8 bin seviye bulunur. Uyumsuz bulunan 314 state'in binaları siyasi aşamada bilerek düşürüldü (bkz. [siyasi oyun kurulumu](SIYASI_OYUN_KURULUMU.md)).
- Oyun geçimlik çiftlikleri kendisi kurar; POP'lar bu yüzden "köylü" görünür. Fakat tahıl, giyim, mobilya, odun gibi temel mallar üretilmediği için fiyatlar tavan yapar ve hayat standardı çöker.
- Okuryazarlık: kurulu oyun, POP okuryazarlığını kurulum sırasında eğitim erişiminden yeniden hesaplar (`common/scripted_effects/00_starting_pop_literacy.txt` notu). Eğitim erişimi eğitim kanunundan, okul kurumu seviyesinden, teknolojiden ve modifier'lardan gelir. 555 ülkenin 523'ünde eğitim kanunu yok. Demografi planındaki pay okuryazarlıkları üretildi, ancak yalnız kurulum girdisi olarak kalıyor.
- Önceden hazırlanıp etkinleştirilmemiş mekanik paketler var: Rûm ekonomisi ([1B.2](../../scenarios/atlas/phase01b2_rum_economy/README.md), 1.231 seviye ve kapasite denetimi), Rûm ordusu ([1B.3](../../scenarios/atlas/phase01b3_rum_military/)), Nizam bağlıları ve bağımsız kuşak (1B.4A/B).

## 2. İlkeler

- Yazılı kaynaklar bağlayıcıdır: [ekonomi ve toplum](ekonomi_ve_toplum.md) sanayi havzaları ve sektör tablosu, [hukuk ve kurumlar](hukuk_ve_kurumlar.md) H1–H10 profilleri, [ülke dosyaları](ulke_dosyalari.md). "Doğu ileri" demek her eyalete fabrika vermek değildir.
- Her paket bölgesel ve doğrulanabilir olur: aday → `scenario validate/build/report` → hedef dışı alan koruması → etkinleştirme → `build`/`check` (0 hata) → siyasi denetim → oyun içi kısa kontrol listesi.
- Sayısal hedefler (okuryazarlık, hayat standardı, fiyat) motor sonucudur. Her paketten sonra oyun içi ölçümle kalibre edilir; statik rapor "dengelendi" sayılmaz.
- Üretilmiş dosyalara elle dokunulmaz. Atlas'ın yapamadığı işler (ör. vanilla journal/AI dosyalarının kaldırılmış ülkelere başvurması) mod içinde dar, belgeli override olarak çözülür; araç hatası ise araç reposunda düzeltilir.

## 3. Paketler

### M0 — Açılış logu temizliği

| Hata kaynağı | Satır | Sahibi | Çözüm yönü |
|---|---:|---|---|
| `common/journal_entries/02_peru_bolivia.txt` kaldırılmış ülkelere bakıyor | 396 | Vanilla, Atlas dışında | Mod içinde dar journal override veya koşul |
| Lobiler, tarihî ticaret, antlaşmalar, varsayılan AI stratejisi, askerî konuşlanmalar, Karadağ JE | ~70 | Vanilla, Atlas dışında | Aynı yöntem; her dosya ayrı kayıt |
| Artık başka ülkede kalan binaların eski yabancı sahiplik kaydı (`create_building` ownership) | ~30 | Atlas çıktısı | Etkin kaynakta sahipliği yerelleştirmek veya Atlas'ta genel kural |
| Britanya ordu/donanma karargâhı ve kayıp generaller | ~25 | Atlas çıktısı | Vanilla birlikleri yeni sahiplerin bölgelerine taşımak ya da ordu paketini M4'e bırakıp temizlemek |
| Bağlılık anlaşması olmayan ülkeye `add_liberty_desire` | 8 | Atlas diplomasi katmanı | Kaynakta ilgili liberty kayıtlarını düzeltmek |
| `ve_andalusi` kültür dosyası UTF-8 BOM ve eksik kültür modifier'ları | 7 | Mod içeriği | BOM ve altı `ve_andalusi_*` static modifier'ı |

### M1 — Kurumsal iskelet ve eğitim (okuryazarlığı düzeltir)

Başlangıç history'si olmayan **159 ülkeye** (714 M kişi; vanilla'dan gelen kademe 7 merkezsiz ülkeler zaten vanilla history taşır) şunlar yazıldı:
- **Teknoloji kademesi:** kurulu oyunun 1–7 başlangıç paketleri (1 = en ileri). Önerilen eşleme yazılı sektör tablosuna dayanır: Rûm, İsfahan, Tebriz, Mısır, Endülüs, Jiangnan kademe 1–2. Lehistan, Kalmar, Britanya taçları, Bavyera, Gurkanî ve Bengal kademe 2–3. Diğer Avrupa, Hint ve Doğu Asya devletleri kademe 3–4. Afrika ve Asya hanedanları kademe 4–6. H9 yerel topluluk birlikleri kademe 6–7. Sömürgeler metropollerinin bir-iki kademe gerisinde.
- **Kanun seti:** 26 kanun grubunun tamamı, ülkenin H profilinden türetilir (H1–H10 tablosu: ekonomik yönetim, ticaret, vergi, toprak, kölelik, eğitim, sağlık, haklar). Demografide yazılan kölelik kanunları korunur.
- **Kurumlar ve eğitim:** eğitim kanunu (dinî, özel, kamu veya okulsuz) ve okul kurumu seviyesi, demografi planındaki okuryazarlık hedefine göre seçilir. Kurulum hesabı hedefi tutturmazsa küçük bir `ve_` eğitim erişimi modifier'ı eklenir. Oyun içinde kalibrasyon turu yapılır.
- **Çıkar grupları:** yönetimdeki IG'ler H profiline göre, ayrıntısız.

### M2 — Temel ekonomi (hayat standardını düzeltir)

Binasız her state payına kural tabanlı bir temel yazılır. M1'in teknolojisi gerektiği için M1'den sonra gelir.
- Hükümet idaresi (nüfus ve devlet kapasitesine göre), inşaat sektörü, kıyıda liman.
- Ekilebilir alana ve bölgesel ürüne göre tahıl çiftlikleri (buğday/pirinç/mısır/çavdar/darı), hayvancılık, kereste, balıkçılık.
- State kaynaklarına göre plantasyon ve madenler.
- Temel tüketim imalatı (dokuma, mobilya, gıda) ülkenin gelişmişlik sınıfıyla orantılı.
- Hedef yoğunluk vanilla'ya yakın, yaklaşık milyon kişi başına 8–10 seviye; H9 yerel yönetimlerde daha düşük, kent ağırlıklı ülkelerde daha yüksek. Toplam yaklaşık 6–7 bin yeni seviye.
- Kaynak ve ekilebilir alan sınırlarını Atlas denetler. Rapordaki istihdam ve altyapı tahmini her bölge için kontrol edilir.
- Kabul: oyunda temel mal fiyatları makul, köylü hayat standardı ~5–10, kentli ~8–15.

### M1b — İslam önceliğiyle okuryazarlık (etkin)

İkinci testte okuryazarlık yalnız birkaç ülkede yüksekti. İlk M1b (İslam çekirdeği %60–70) üçüncü testte Rûm/İsfahan'ı %70–80'de açtı. 25 Eylül kararı: İsfahan %48, diğer gelişmiş Müslüman devletler %32–36, orta İslam %20–30, az gelişmiş Müslüman devletler ve Avrupa ortalaması %15–20, Doğu Asya %10–18, geri kalan %2–10. Hedefler açılış ekranı değeridir. Girdi, okul kanunu ve seviyesinin kurulumda eklediği puanlar düşülerek hesaplanır. Okul seviyeleri 1–3'e indi. Vanilla history'li 84 İslam ülkesine okul kanunu, kurumu ve tenant farmers verildi.

### M3-lite — İslam dünyasının tüketim ekonomisi (etkin)

Rûm 1B.2 sanayi planı (1.161 açık seviye) ve diğer İslam paylarına tüketim öncelikli yoğunlaştırma: çekirdek 32, tanınmış 20, tanınmamış 16 seviye/milyon. Dünya toplamı 10.250 → 14.398 seviye.

### M3 — Bölgesel sanayi merkezleri

Yazılı sanayi havzaları (Marmara–Bursa, Tebriz, İsfahan–Kaşan, Kahire–İskenderiye, Bağdat–Basra, Jiangnan, Varşova–Kraków, Ren–Saksonya–Bohemya, İsveç metal merkezleri...) temel ekonominin üstüne eklenir. Rûm'un 1B.2 paketi güncel demografiyle yeniden doğrulanıp etkinleştirilir. Şirketler burada eklenir.

### M4 — Ordu, donanma, diplomasi davranışı

Rûm 1B.3 ordusu ve diğer ülkelerin temel orduları; M0'dan kalan askerî kalıntılar; bağlılık ve anlaşma davranışının motor denetimi.

## 4. Test döngüsü

Her paketten sonra oyunda yeni başlangıçla aynı kısa liste kontrol edilir: seçili 10 ülkenin okuryazarlığı, hayat standardı ve tahıl/giyim fiyatı, işsizlik, `error.log` satır sayısı. Log salt okunur incelenir.
