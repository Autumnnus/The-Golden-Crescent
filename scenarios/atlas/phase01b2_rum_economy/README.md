# Faz 1B.2 — Rûm özgürleşme ve ekonomi omurgası

**13 Eylül 2026. Statik ve kümülatif Atlas önizlemesi; etkin veya oynanabilir sürüm değildir.**

Bu paket Faz 1A sınırlarını ve Faz 1B.1'in 27 milyonluk Rûm nüfusu, eğitim, hukuk ve kurum kararlarını içerir. Yeni işler yalnız Rûm'un doğrudan yönettiği 25 eyalet payıdır. Kaynak [scenario.json](scenario.json), okunabilir üretim kararları [economy-plan.json](economy-plan.json), gerçek üretim yöntemlerinden çıkarılan kapasite hesabı [capacity-audit.json](capacity-audit.json), kabul sonucu [verification.json](verification.json).

## Özgürleşme

Faz 1B.1'in derlenmiş ortak kültür–din gruplarında **216.325 kişi** vanilla'dan `pop_type = slaves` olarak kalmıştı. Bu pakette her grubun kişi sayısı, kültürü ve dini aynen korunur; yalnız meslek statüsü `peasants` olur. Yeni derlemede Rûm nüfusu 27.000.000, kalan `slaves` statüsü 0 ve açık `peasants` dönüşümü 216.325'tir.

Bu işlem `law_slavery_banned` kanununun 1811'den beri yürürlükte olduğu yazılı tasarımla nüfusu uyumlu kılar. Fakat kanunun vanilla `on_activate` bloğu yakın zamanda kaldırılma değişkeni üretebilir. History kurulumu sırasında bu bloğun çalışıp çalışmadığı motor testi olmadan kesin değildir. 1836'da “yeni kaldırıldı” etkisi görülürse Atlas'ın ürettiği ülke history katmanına elle müdahale edilmeyecek; kaynak veya araç sözleşmesinde açık bir başlangıç etkisi çözümü geliştirilecek.

## Ekonomik yapı

| Havza | Başlangıç rolü | Tasarım sınırı |
|---|---|---|
| Konstantiniyye–Marmara | Çelik, alet, motor, dokuma, kâğıt, silah, tersane, üniversite ve merkez idare | Kömür/metal sevki ve yüksek kamu gideri |
| Kastamonu–Ereğli | Ana kömür, kereste ve maden demiryolu | Kaza, liman ve alet darboğazı |
| Aydın–İzmir | İkincil kömür, dokuma, tüketim malları ve liman | Pamuk/boya ve dış ticarete bağımlılık |
| Konya–Ankara | Tahıl, hayvancılık, tarım aleti, gıda ve hukuk/teknik eğitim | Kıyıdan uzaklık ve taşıma gideri |
| Bağdat–Halep | Kâğıt, kayıt, eğitim, gıda, dokuma ve nehir/Akdeniz bağlantısı | Bağdat–Basra kesintisiz demiryolu varsayılmaz |
| Balkan–Ege kuşağı | Demir, kereste, tahıl, pamuk, cam, tersane ve kıyı ikmali | Her eyalet ağır sanayi merkezi değildir |

Rûm'un raporlanan bina toplamı **1.231 seviye**. Açık üretim yöntemlerinin tam istihdam kapasitesi 3.450 bürokrasi, haftalık 64,5 inovasyon, 190 inşaat ve 913 eyalet altyapısıdır. Bunlar gerçek işe alım veya bütçe sonucu değildir.

Kaynak kapasite hesabında kömür, motor, gübre, demir, kâğıt, çelik, kükürt ve alet girdileri sıfırın altında kalmaz. Boya, kumaş, et, ipek ve odun açıktadır. Bunlar hata gizleme amacıyla tamamlanmadı:

- Boya dış ticaretten gelir; Rûm başlangıçta tropik boya üreticisi değildir.
- Kumaşın bir kısmı Rûm tarımından, kalanı Mısır/Adana ve başka tedarikçilerden gelir. Bu bağımlılık için sonraki bölge fazlarında gerçek pazar ilişkisi gerekir.
- İran ipeği ve Balkan/Karadeniz odunu yazılı ticaret ağının somut ekonomik değeridir.
- Et açığı, kent gıdası ve ordu bütçesini birbirine bağlayan başlangıç baskısıdır.

Kapasite hesabı yalnız açık seçilmiş üretim yöntemlerini toplar. Subsistence üretimi, devralınmış küçük binalar, nüfus tüketimi, fiyatlar, konvoylar, ücretler, vergi, throughput ve kalifikasyonlar dahil değildir. Pozitif toplam çalışan fabrika garantisi değildir; negatif toplam da otomatik oyun hatası değildir.

## Bölünmüş eyalet güvenliği

Hub sahibine aykırı vanilla bina aktarımı temizlendi:

- Rûm'un Adana payında şehir, liman, çiftlik ve maden hub'ı ADA'dadır; Rûm payında eski liman/balıkçılık/plantasyonlar kaldırıldı, yalnız sahip olduğu kereste hub'ı kullanıldı.
- Basra şehri BSR, limanı KUW, maden ve çiftlik payı RUM'dadır; Rûm'un yanlış limanı ve ticaret merkezi kaldırıldı, kükürt ve nehir tarımı korundu.
- Trabzon'da Rûm şehir/çiftlik payını kullanır; TRB'nin liman, maden ve kereste hub'ına bina yazılmaz.
- Erzurum'da Rûm yalnız çiftlik payını kullanır; ERZ'nin şehir/maden payına el koymaz.

## Teknoloji ve üretim yöntemleri

Tier 4 tabanı, genel bir “bütün teknolojiler ileri” kısayoluna çevrilmedi. Sanayi zincirinin kullandığı `atmospheric_engine`, `mechanical_tools`, `lathe`, `mechanized_workshops`, `intensive_agriculture`, `railways`, `canneries`, `dialectics`, `rifling` ve `screw_frigate` eklendi; Atlas öncülleri tamamladı. Madenlerde atmosferik pompa, dokumada dikiş makinesi/mekanik tezgâh, inşaatta demir karkas, devlet dairelerinde yatay dosyalama, demiryolunda erken tren kullanılır. Elektrik, dizel, kıtalararası demiryolu, seri çelik filo veya ileri otomasyon başlangıç varsayımı değildir.

## Yeniden üretme ve doğrulama

Mod kökünde:

```sh
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b2_rum_economy/prepare.py
python3 scripts/tools.py atlas scenario report scenarios/atlas/phase01b2_rum_economy/scenario.json --out build/phase01b2/report.json
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b2_rum_economy/audit.py
python3 scripts/tools.py atlas scenario build scenarios/atlas/phase01b2_rum_economy/scenario.json --out build/phase01b2/generated
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b2_rum_economy/verify.py
python3 scripts/tools.py atlas preview --scenario scenarios/atlas/phase01b2_rum_economy/scenario.json --region RUM,BOS,ALB,BUL,ADA,ERZ,TRB,KUR,BSR,SYR,LEB,PAL,KUW --out build/maps/phase01b2-rum.html
```

Doğrulama; 452 diğer ülkenin değişmemesini, sınır/diplomasi/kanun/kurum devamlılığını, kaynak ve ekilebilir alan sınırlarını, gerçek bina–PM–teknoloji kimliklerini, ortak kültür/din gruplarının birebir korunmasını, köle statüsünün sıfırlanmasını ve yeni uyarı olmamasını kontrol eder. Seçilen PM kaynak dosyalarının SHA-256 kayıtları kapasite denetimindedir. Oyun motoru çalıştırılmadı ve `world/` etkinleştirilmedi.

## Sonraki iş — Faz 1B.3

Rûm'un ordu/donanması, hükümet çıkar grupları ve savaş borcu başlangıç baskısı kurulacak. Ardından diğer 12 bölge ülkesinin nüfus–ekonomi–hukuk–ordu paketleri, Nizam bağlılık mekaniği ve Basra/Trabzon/Tırnova şehir-hub sorunları çözülecek. En son eski TUR/GRE/ION event ve kayıtlı scope kalıntıları denetlenip aktif dünya için motor testi yapılacak.
