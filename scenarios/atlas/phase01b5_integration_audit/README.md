# Faz 1B.5 — Rûm statik entegrasyon denetimi

**13 Eylül 2026. Kümülatif denetimdir; yeni ülke üretmez ve etkin/oynanabilir sürüm değildir.**

Bu paket Faz 1B.4B çıktısını kurulu Victoria 3 1.13.11 dosyalarıyla karşılaştırır. [audit.py](audit.py), yorum satırlarını ayıkladıktan sonra `TUR`, `GRE` ve `ION` ülke scope'larını tarar; [integration-audit.json](integration-audit.json) dosya ve hash düzeyinde kanıtı saklar. [verify.py](verify.py) parent hashlerini, replace path kapsamını, altı Nizam bağını ve risk kararlarını yeniden doğrular.

## Sonuç

Atlas'ın ürettiği ve metadata ile değiştirdiği yedi history klasöründe `TUR`, `GRE` veya `ION` referansı kalmamıştır. Faz 1B.4B statik validate/build denetiminden geçtiği için şu anda doğrulanmış bir script parse veya build çökmesi yoktur.

Ancak metadata yalnız `buildings`, `countries`, `diplomacy`, `military_formations`, `pops`, `population` ve `states` history klasörlerini değiştirir. Vanilla'nın aşağıdaki başlangıç dosyaları yüklenmeye devam eder:

- TUR/GRE/ION karakter yaratımları;
- TUR power bloc'u, Prusya–TUR tarihî antlaşması ve GRE/TUR lobileri;
- TUR siyasî hareketi ve başlangıç AI stratejisi;
- GRE/TUR gizli AI hedefleri ve global başlangıç kontrolleri.

Bunlar tek başına parse çökmesi kanıtı değildir. Arazi ve Atlas history'si kaldırılmış etiketlerde eski karakter, diplomasi, AI ve global davranış üretme ihtimali taşıdıkları için **oynanabilir sürüm engelidir**. Journal, event, decision, scripted effect/trigger ve on_action dosyalarında da doğrudan scope'lar vardır. Çoğu ülke veya durum koşuluyla boşta kalabilir; motor testi olmadan hepsinin güvenle no-op olduğu iddia edilmez.

## Nizam sözleşmesi

Altı bağ doğru ülkelere kurulmuştur: Rûm; Bosna, Arnavutluk, Tuna, Adana, Erzurum ve Trabzon'un overlord'udur. Prototip bağlı ülkenin kendi diplomatik oyununu başlatmasını ve alt bağlı edinmesini engeller, onu Rûm savaşlarına katar ve gelirinin yüzde 8'ini aktarır.

Bu yüzde 8 sabit yıllık katkı değildir. Yazılı tasarımdaki levy kotası, gümrük/pazar işlemi ve karşılıklı müzakereyle fesih uygulanmamıştır. Bağlı taraf tek başına feshedemez; overlord feshedebilir. `annex_on_country_formation = yes`, geniş rütbe izni, overlord rengi ve `same_as_vassal` kategorisinin yan etkileri de motor testi ister. Bu nedenle prototip aktif sürüm için henüz kabul edilmedi.

## Basra–Kuveyt kararı

Vanilla `STATE_BASRA` tek şehir ve tek port hubı taşır. Doğrulanmış şehir `x807060` Basra'da, port `x00F060` Kuveyt'tedir. İkinci bir fiziksel liman, ayrı incelemeli state-region/province bölünmesi olmadan eklenmeyecek. Mevcut temsil statik olarak tutarlı kalır; Şattülarap ve Kuveyt'i iki ayrı gerçek port yapmak istenirse bu karar yeniden açılır.

## Yeniden üretme

Mod kökünde:

```sh
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b5_integration_audit/audit.py
/Users/kadir/Projects/vic3-mod-tools/.venv/bin/python scenarios/atlas/phase01b5_integration_audit/verify.py
```

Tarama oyun kurulumunu yalnız okur. `world/scenario.yml` oluşturmaz; oyuna veya loglara yazmaz.

## Sonraki iş — Faz 1B.5B

Önce başlangıçta yüklenen eski TUR/GRE/ION history blokları dar bir uyumluluk katmanıyla etkisizleştirilecek; büyük vanilla dosyaları körlemesine kopyalanmayacak. Sonra Nizam sözleşmesi yazılı tasarımla eşleştirilecek. Basra harita bölünmesi ayrı karar olarak kalacak. Bu iki statik engel kapandıktan sonra izole modda ilk motor açılışı ve log gözlemi yapılacak.
