# Demografi 3 — İran konfederasyonunun yedi üyesi

**Etkin kaynak:** `world/scenario.yml`. On üç doğrudan state/ülke payı ayrı ayrı düzenlendi. İran ortaklığına sekizinci bir ülke nüfusu eklenmez; İsfahan ile Tebriz birbirinin nüfusunu kullanmaz. Ortak kültür–din kararları [plan.yml](plan.yml), eski POP verisi [dondurulmuş kayıtta](legacy-population-snapshot.json) bulunur.

| Üye | 1836 nüfusu | Ağırlıklı okuryazarlık girdisi | Temel ayrım |
|---|---:|---:|---|
| İsfahan `ISF` | 8.000.000 | %51,94 | İsfahan–Tahran–Şiraz çekirdeği; Ermeni ve Yahudi kent ağları |
| Tebriz `TBR` | 4.500.000 | %46,90 | Azeri atölyeleri; Urmiye'de Kürt, Ermeni ve Süryani topluluklar |
| Horasan `KHO` | 3.000.000 | %31 | Fars, Kürt, Türkmen ve Beluç kervan çevresi |
| Mazenderan `MAZ` | 2.000.000 | %33 | Hazar kıyısında Mazenderanlı ağırlık |
| Kirman `KRM` | 1.600.000 | %27,06 | İç plato ve Laristan/Körfez payı; Beluç ve Bedevi geçişi |
| Luristan `LUR` | 1.700.000 | %22,94 | Luristan'da Lur, İran Kürdistanı'nda Kürt ağırlık |
| Huzistan `HUZ` | 1.900.000 | %30 | Maşrıkî Arap çoğunluk, Fars/Lur ve yerel Hristiyan topluluklar |

**Konfederasyon üyeleri toplamı 22.700.000** kişidir; yazılı İsfahan 7–9 milyon, Tebriz 4–5 milyon, diğer beş üye birlikte 9–12 milyon hedefleriyle uyumludur. Okuryazarlık oranları oyun motoru sonucu değil Atlas başlangıç girdisidir. Üyelerin sabit meslek kayıtları ve mevcut **102.900 köle POP'u** aynen korunmuştur; emek/hukuk değişimi ayrı aşamadır. `STATE_LARISTAN`ın Umman ve Bahreyn payları korunur; yalnız Kirman payı değiştirilmiştir.

[Şehir profilleri](city-profiles.yml) İsfahan, Şiraz, Tahran, Tebriz, Urmiye, Meşhed, Berfuruş, Kirman, Hürremabad ve Şuşter için toplam **4,13 milyonluk** tahmin içerir. Yerleşim adları kurulu oyunun hub yerelleştirmesinden doğrulandı. Şehirler kendi state/ülke nüfusunun alt kümesidir; Victoria 3'e ayrı şehir POP'u olarak yazılmaz. Ortak kültür–din tahminleri state gruplarını aşmaz.

**Henüz çözümlenmeyen kimlik ayrıntıları:** Yazılı senaryodaki İrfanî kurumlar oyun içinde ayrı bir din türü değil; bu dilimde vanilla `shiite` geniş vekilidir. Kurulu oyunda Zerdüşt dini tanımı da bulunmadığından Zerdüşt cemaatler için uydurma veya yanlış din kimliği eklenmedi. Bu iki konu, din/kanun semantiği ve yerelleştirmesi birlikte tasarlanarak sonraki özel içerik aşamasında ele alınmalı. Nüfusun sayısal ve mevcut oyun kimliklerine dayalı karışımı şu anda statik olarak geçerlidir.

Mod kökünde `prepare.py`, ardından aday için `atlas scenario validate`, `report`, `build` ve bu paketin `verify.py` denetimini çalıştır. Etkin sürümde `atlas build` ve `atlas check` sıfır hata verdi; 25 önceki sınır/ordu uyarısı sürüyor. `verify.py` siyasi sınırları ve İran dışı POP bloklarını değişmeden, yedi üye toplamını ve şehirlerin state gruplarına sığmasını doğrular. Yeni nüfusun oyun motorunda başlangıcı ve zaman ilerlemesi henüz sınanmadı. Eski binalar ve üretim yöntemleri bu demografi fazında dengelenmedi.
