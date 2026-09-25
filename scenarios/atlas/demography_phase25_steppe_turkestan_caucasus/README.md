# Demografi 25 — Kazak bozkırı, Türkistan, Kafkasya ve Afganistan–Belucistan

Bu paket [yazılı atlasın](../../../docs/scenario/dunya_atlasi.md) Kafkasya, bozkır ve Orta Asya tablosunu nüfusa uygular. **22 ülkenin 54 doğrudan payı** etkin Atlas kaynağına işlendi; sınır, bağlılık ve bina değişmedi. Rusya ve Orta Asya teknik bölgelerinde açık pay kalmadı. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Kararlar

- **Yerel nüfus korunur:** Buhara, Hive, Hokand, Türkmenler, Kırgızlar, Herat/Kabil/Kandahar ve Beluç hanlıklarının devralınan nüfusu zaten yereldir; ölçek ve ortak kültür–din grupları korunur. Peşaver vadisindeki Pencap/Hindko toplulukları Kabil payında kalır.
- **Rus imparatorluk yerleşimi:** Kullanıcının Faz 24'teki ölçülü azaltma kararı uygulanır. Orenburg, Çelyabinsk, Yaik hattı, Akmola/Semireçye ile Kızlar, Grozni, Vladikavkaz, Tiflis ve Bakü garnizonlarındaki **746.457** Rus/Ukraynalı/Alman POP'u **28.840**'a iner (küçük Kazak/Terek ve tüccar kalıntıları). Yerini Kazak, Başkurt, Tatar, Nogay, Çeçen, Çerkes, Gürcü, Ermeni, Azeri ve Dağıstan halkları alır.
- **Kölelik:** Buhara, Hive, Hokand, Afgan ve Beluç yönetimlerinde vanilla `law_debt_slavery` yazılı H8 "borç/ev içi kölelik yasal" profiline uyar; Türkmenlerin `law_slave_trade` kanunu esir ticaretini temsil eder. **828.966** köle POP'u aynı sayıda korunur. Hive ve Hokand'daki Rus esirlerin çoğu, bu evrende bölgeye ulaşan bir Rus imparatorluğu olmadığı için İranlı, Türkmen, Özbek ve Uygur esirlere yeniden dağıtıldı. Kafkas devletlerinde köle POP'u yoktur.
- **Kafiristan** (`KAF`) resmî dini `hindu` yerine yerel çok tanrılı inancın oyun karşılığı `animist` oldu; köleleri dahil Kho/Kafir nüfusu aynı inanca geçer.
- **Homeland:** Faz 21 kuralıyla yazıldı; Faz 24'te atlanan Samara (`russian, tatar` → `russian, tatar, mordvin, kazak, bashkir`) ve Kuban da bu pakette tamamlandı. Çelyabinsk'in `russian` homeland'i `bashkir, kazak, tatar` olur.

| Alan | Önce | Etkin başlangıç |
|---|---:|---:|
| 54 hedef pay | 16.872.907 | 16.346.200 |
| Dünya nüfusu | 1.079.616.864 | 1.079.090.157 |

KAN ve MAK'ın Sistan payları Ortadoğu paketine kaldığı için bu iki ülke kısmi sayılır. [48 yerleşim profili](city-profiles.yml) payın planlı kültür–din gruplarına orantılı tasarım alt kümeleridir (Semerkand, Buhara, Hive, Taşkent, Hokand, Kabil, Peşaver, Herat, Kandahar, Kalat, Erivan, Bakü, Derbent...). Rus imparatorluk kaleleri ve yeniden adlandırmaları (Verniy, Grozni, Vladikavkaz, Orenburg, Elizavetpol) profillenmedi.

## Doğrulama ve açık kalanlar

[Önizleme](../../../build/maps/steppe-turkestan-caucasus-demography.html) 0 sınır değişikliği gösterir. Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/steppe-turkestan-caucasus-verification.json), etkin Atlas `build/check` (**0 hata; 25 uyarı**), siyasi denetim ve 38 araç öz testi geçti. Motor testi yapılmadı. Gürcistan, Erevan, Bakü ve Dağıstan imametlerinin kanun/teknoloji/bina başlangıcı yoktur; bozkır ve Türkistan'ın köle POP'larının tek `slaves` statüsüyle temsili hukuk aşamasında ayrıca değerlendirilmelidir.

Yeniden üretim: `steppe-turkestan-caucasus-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `snapshot.py` → `prepare.py` → `scenario validate/build --out build/scenarios/steppe-turkestan-caucasus-candidate` → `verify.py`.
