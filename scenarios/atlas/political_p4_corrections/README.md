# P4 — Altıncı inceleme düzeltmeleri

**26 Eylül 2026 · etkin.** Kullanıcının P3 sonrası oyun içi incelemesinden gelen düzeltmeler. Kararlar [plan.yml](plan.yml) dosyasında; plan [P3 hazırlayıcısı](../political_p3_borders/prepare.py) ile uygulanır (`--plan-dir scenarios/atlas/political_p4_corrections --name p4`). Toplam 2 province bölmesi ve 44 pay aktarımı var; toprağı kalmayan 37 ülke düşer ve ülke sayısı 505'ten 468'e iner. Nüfus ve bina seviyesi (14.226) değişmez.

## Ad sorunu: vanilla adları senaryo adlarını eziyordu

Oyunda Musul Emirliği "Kürdistan", Kazak Hanlığı "Küçük Cüz" olarak görünüyordu. Sebep şu: Atlas ülke adlarını `tgc_generated_countries` dosyasına yazıyor. Vanilla'nın aynı anahtarı tanımladığı etiketlerde (KUR, KZH, SIC, HAM, UBD, MUG...) çakışmada vanilla metni kazanıyor. Yani P2 ve P3'te vanilla etiketlere verilen adlar ve sıfatlar oyunda hiç görünmemiş.

[vanilla_overrides.py](../../runtime_cleanup/vanilla_overrides.py) artık çakışan anahtarları `localization/replace/<dil>/tgc_country_name_overrides_l_<dil>.yml` dosyasına kopyalıyor; bu klasör vanilla'yı ezer. Şu an 84 anahtar kapsanıyor (42 ülke adı ve sıfatı).

Ad değişimine bir örnek: haritada "Hindustan" olarak görünen `MUG` artık kanondaki adıyla **Gurkanî İmparatorluğu** görünür.

**Araç sınırı:** `atlas check` bu klasörü ayrı bir üstüne yazma katmanı olarak tanımıyor. Aynı anahtarlar `replace` dosyasında ve Atlas'ın dosyasında durduğu için 168 "duplicate key" hatası veriyor. Oyunda doğru davranış budur; düzeltme araç reposunda gerekiyor, açık iş olarak duruyor.

## Değişiklikler

| Bölge | Değişiklik |
|---|---|
| **Uygur Hanlığı** | Çinghay'ı Kuzey Çin'den alır. Hindukuş'ta Chitral'i (iki payı) ve Kafiristan'ı Afgan kuşağından alır (7,8 → 9,4 M). Kuzey Çin Çinghay'ı geri ister. |
| **İran** | Tebriz Şahlığı İsfahan'ın kuklasıdır (`puppet`). Vanilla'da kukla kendi bağlısını tutamadığı için Bakü ve Erevan İsfahan'ın koruması olur. İran İttifakı kalkar (üst devlet ile bağlısı ittifak yapamaz); Rûm–Tebriz rekabeti Rûm–İsfahan rekabetine dönüşür. |
| **Musul** | `KUR` artık oyunda da "Musul Emirliği" görünür (yukarıdaki ad düzeltmesi). |
| **Arabistan** | Şam, Cebel Şammar'ın Hail'in batısındaki Cevf–Tebük–Teyma çölünü (47 province) alır. El-Hasa kıyısı (Katif, Safva) Necid'den Bahreyn'e geçer ve **Bahreyn ve Hasa Emirliği** kurulur; Körfez'in iki kıyısında deniz ticaret emirliğidir. Mahra, Hadramut'la birleşerek **Hadramut Sultanlığı** olur (Umman koruması). Necid, Cebel Şammar, Yemen Zeydi İmamlığı, Lahic ve Hicaz Şerifliği'ne senaryo adları verildi. |
| **Hindistan** | Yaklaşık 60 devlet 26'ya indi. Ayrıntı aşağıdaki listede. |
| **Tatar–Kazak** | Tatar Hanlığı Ural'ın batı yakasını alır (Bukey bozkırı, 28 province, 45 bin kişi); Uralsk kenti Kazak'ta kalır. "Küçük Cüz" adı yerine Kazak Hanlığı görünür. |

**Hindistan'daki birleşmeler:**
- **Gurkanî İmparatorluğu** (36,0 → 40,1 M):
  - Patiala'nın Delhi payı
  - Garhwal
  - Bahawalpur
  - bütün Bundelkhand (Bundelkhand, Jhansi, Baghelkhand, Surguja)
  - Bhopal navaplığı
  - Alwar

  Ayrıca Jodhpur Gurkanî'nin koruması olur.
- **Racput hanedanları:** Kota Jaipur'a, Bikaner ve Jaisalmer Jodhpur'a katılır.
- **Sih Devleti:** Patiala'nın dağ Pencap'ındaki Sih reisleri katılır.
- **Gujarat Liman Birliği:** Kutch ve Kathiawar kıyısını tek birlik olarak alır. Idar Baroda'ya katılır.
- **Doğu ve Orta Hindistan:**
  - Orissa: Kalahandi, Mayurbhanj, Patna ve Jeypore'u alır.
  - Nagpur: Bastar'ı alır.
- **Güney Hindistan:**
  - Travankor: Koçin'i alır.
  - Tamil krallığı: Pudukkottai'yi alır.
  - Maratha: Satara ile Kolhapur'u alır.
- **Kuzeydoğu:**
  - Bengal: Cooch Behar ile Tripura'yı alır.
  - Assam: Naga ve Lushai toplulukları katılır.
  - Burma: Arakan ve Mandalay'deki Lushai payları katılır.
- **Keşmir:** Ladakh'ı alır (Gurkanî kuklası).

## Doğrulama

[P3 doğrulayıcısı](../political_p3_borders/verify.py) `--plan-dir/--name p4` ile çalıştı ve geçti:
- state nüfusları değişmedi;
- soy kaydı ([lineage.yml](lineage.yml)) kişi sayısı ve okuryazarlıkla tutarlı;
- aktarımlar ve bağlılık ağı planla aynı;
- yeni uyarı yok.

Kölelik yasağı olan alıcılara geçen üç paydaki köle POP'ları serbest bırakıldı: Chitral, Kafiristan, Cooch Behar.

[M1b](../mechanics_m1b_literacy/prepare.py) soy kayıtlarını artık P4 → P3 zinciriyle okuyor ve bu dünyada birebir yeniden çalışıyor. Topraksız kalan ülkelerin okul geçmişi vanilla ülke geçmişinden okunuyor.

[Siyasi denetim](../world_political/active_political_audit.py) P3 ile P4'ü sırayla uyguluyor ve geçti; araç testleri 123/123.

`atlas check` sonucu: **168 hata** (yalnız yukarıdaki `replace` tekrarları), 16 uyarı. Oyunda sınanmadı.

## Açık konular

- **Vanilla rütbe kısıtı:** Tebriz (4,5 M) İsfahan'dan (8,0 M) düşük rütbeli olmalı. Oyunda kukla bağı açılışta bozuluyorsa sebep budur.
- **Adlandırma değişikliği:** P2 ve P3'te verilen ama görünmeyen adlar (Napoli, Hansa, Livonya, Tuareg, Tuna Emirliği, Bosna Emirliği...) ilk kez görünecek.

```sh
cp world/scenario.yml build/political/p4-source.yml; cp build/world-political/active-political-report.json build/political/p4-source-report.json
python3 scripts/tools.py atlas scenario build build/political/p4-source.yml --out build/scenarios/p4-source
python3 scenarios/atlas/political_p3_borders/prepare.py --plan-dir scenarios/atlas/political_p4_corrections --name p4
python3 scripts/tools.py atlas scenario validate build/political/p4-candidate.yml
python3 scripts/tools.py atlas scenario build build/political/p4-candidate.yml --out build/scenarios/p4-candidate
python3 scenarios/atlas/political_p3_borders/verify.py --plan-dir scenarios/atlas/political_p4_corrections --name p4
```
