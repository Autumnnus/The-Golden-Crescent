# Demografi 24 — Rus ormanı, Volga, Baltık, Finlandiya ve Sibirya

Bu paket [ana senaryonun](../../../docs/scenario/senaryo.md) "Moskova Tatar baskısı altında bölgesel kalır; Sibirya'ya yayılmış büyük Rusya yoktur" kararını nüfusa uygular. **56 state'te 20 ülkenin 56 doğrudan payı** etkin Atlas kaynağına işlendi. Kararlar [planda](plan.yml), uygulama öncesi POP'lar [dondurulmuş kaynakta](source-pops.json).

## Sahalin düzeltmesi

Kullanıcı kararıyla (24 Eylül 2026) [siyasi betik](political.py) Sahalin'de kalan Rus-Amerikan şirketi `ALK` payının iki province'ini Ainu Mosir (`AIN`) payına katar. `ALK` topraksız kalır ve Faz 21'deki başkent kaydı silinir; kara sahibi ülke **556 → 555**. AIN'in Faz 15 planı bu pakette açıkça değiştirilir: 7.281 → **8.074** kişi (şirket payının 793 kişisi Ainu/Nivkh nüfusuna döner). AIN merkezsiz olduğu için şirketin tek liman seviyesi Atlas kuralıyla düşer (3.229 → 3.228). Diplomasi değişmedi; Doğu Asya teknik bölgesinde açık pay kalmadı.

## Nüfus kararları

| Kapsam | Pay | Önce | Etkin başlangıç | Rus/Ukraynalı/Alman/Belarus POP |
|---|---:|---:|---:|---:|
| Moskova, Novgorod, Baltık, Finlandiya | 25 | 22.115.229 | 21.055.000 | 18,52 M → 17,21 M |
| Tatar hanlığı, Kırım, Kalmuk, Volga–Ural ve Sibirya yönetimleri | 31 | 14.397.149 | 9.079.074 | 10,98 M → 1,53 M |
| Dünya nüfusu | | 1.085.995.961 | 1.079.616.864 | |

- **Moskova** (15,47 M) ve **Novgorod** (2,40 M) Rus Ortodoks çekirdeğini korur; Moskova'ya Tatar baskısının izi olarak küçük Tatar tüccar/garnizon toplulukları (Kasımov çevresi dahil) eklendi, toplam %3 azaldı. St. Petersburg kurulmadığı için Ingria 976 binden 500 bine iner; İzhor, Ingria Fin, Estonyalı ve Hansa tüccarları kalır. Arkhangelsk, Karelya, Nenetsia ve Kola'da Pomor Rusları ile Karelya, Komi/Nenets ve Sámi halkları birlikte yaşar.
- **Baltık** (`UBD`) Leton/Eston Lutheran çoğunluğunu ve Baltık Alman seçkinlerini korur; imparatorluk döneminin Rus toplulukları küçülür. **İsveç tacı Finlandiyası** devralınan bileşimiyle kalır.
- **Büyük Tatar Hanlığı** 6,96 M'den **4,20 M**'ye iner: Kazan, Ufa, Samara, Saratov, Astarhan, Don, Stavropol ve Taurida'da Volga Tatarları, Nogaylar, Başkurtlar, Çuvaşlar, Mariler, Mordvinler, Kazaklar ve Kalmuklar çoğunluktadır. Rus nüfusu esir, tüccar ve Kryaşen toplulukları ile Don/Terek Kazakları olarak kalır (%5–35); Novorossiya kolonizasyonu olmadığından Taurida'da Ukraynalı Kazak/köylü payı %30'dur. **Kırım Hanlığı** Kırım Tatar çoğunluğu, Rum, Ermeni, Yahudi/Karay ve Rûm tüccarlarıyla kurulur; Kuban'da Çerkes ve Nogay nüfusu vardır.
- **Mari, Mordvin ve Ural meclisleri** kendi halklarıyla başlar; eski Novgorod kökenli Vyatka ve Stroganov tuzlalarının Rusları %25–28 olarak kalır. Çuvaş, Mari, Udmurt, Mordvin ve Komi toplulukları kısmen geleneksel inançlarına döner.
- **Sibirya ve uzak doğu:** Sibirya Tatarları, Hantı/Mansi (`ugrian`), Samoyed/Tunguz ve diğer halklar (`siberian`), Buryat (Budist ve Şamanist), Saha, Yukagir, Çukçi ve Kamçatka halkları çoğunluktadır; imparatorluk misyonlarından gelen Ortodoksluk ve 1,3 M Rus yerleşimci kaldırıldı. Buhara tüccarları, Kyakhta ticareti ve küçük Rus kürk tüccarları kalır.
- `VKM` birincil kültürü `mongol` yerine kurulu oyunun `kalmyk` kültürü oldu. Köle POP'u yoktur; Moskova'daki serflik POP mesleği değil, sonraki hukuk aşamasının konusudur.
- Homeland'ler Faz 21 kuralıyla yazıldı; kural artık aynı state'teki daha önce planlanmış payları da hesaba katar. Samara (`KZH` payı) ve Kuban (`CIR` payı) Faz 25'e kadar atlandı.

[52 yerleşim profili](city-profiles.yml) state nüfusunun içindeki tasarım alt kümeleridir. Rus imparatorluğundan önceki veya ona bağlı olmayan adlar profillendi (Moskova, Novgorod, Kazan, Astarhan, Kasımov, Tümen, Kerç, Riga, Tallinn, Helsingfors, Åbo); St. Petersburg, Yekaterinburg, Sivastopol, Rostov-on-Don, Omsk gibi imparatorluk kuruluşları profillenmedi, oyundaki görünen adlar değişmedi.

## Doğrulama ve açık kalanlar

[Önizleme](../../../build/maps/russia-siberia-demography.html) yalnız Sahalin'i siyasi değişiklik olarak gösterir. Aday `scenario validate/build`, [faz doğrulaması](../../../build/demography/russia-siberia-verification.json), etkin Atlas `build/check` (**0 hata; 25 uyarı**), güncellenen siyasi denetim ve 38 araç öz testi geçti. Motor testi yapılmadı. Moskova'nın serflik/emek düzeni, Tatar hanlığının kanunları ve Sibirya meclislerinin bina/teknoloji başlangıcı hukuk–ekonomi aşamasına kalır.

Yeniden üretim: `russia-siberia-source.yml`, `-source-pops.txt`, `-source-report.json` uygulama öncesi etkin dünyadır. `political.py` → `scenario build --out build/scenarios/russia-siberia-political` → `snapshot.py` → `prepare.py` → `scenario validate/build --out build/scenarios/russia-siberia-candidate` → `verify.py`.
