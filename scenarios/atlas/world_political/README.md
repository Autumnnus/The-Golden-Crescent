# Dünya siyasi iskeleti

Bu dizin The Golden Crescent'ın 1836 siyasi dünya kartlarının
kaynağıdır. Kartlar yalnız doğrudan state/province sahipliğini ve bunun için
gerekli asgarî ülke tanımını kurar. Nüfus, kültür-din oranı, bina, şirket,
kanun, teknoloji, ordu, ekonomi ve Flavor burada üretilmez.

## Durum

Siyasi sahiplik aşaması **kilitlidir.** Şu anda 65 kart
(`card00.json`–`card64.json`) birleşik önizlemeye alınmıştır. Dünya 675 state
içerir ve 675'inin de doğrudan province sahipliği bir kartta açıkça yazılır.
`card63.json`, önceki büyük alternatif tarih kartlarının dışındaki 221 yerel
state'i de kesin `split` kaydına dönüştürür; varsayılan sahiplik kalmaz.
`SIYASI_STATE_KARAR_DEFTERI.md` bu yerel kararları okunabilir biçimde listeler.

`political_completion_audit.py`, varlığını koruyan bütün vanilla başlangıç
pact'larını bloklayıcı olarak listeler; state karar defterini ve yazılı
diplomasi sözleşmesini çalıştırır.
Audit `ready_for_political_lock: true` yazmadıkça bu önizleme ülke/sınır/
diplomasi açısından tamamlanmış değildir.

Önemli kapanışlar:

- RUS, CHI, BIC, ABD, Meksika, Brezilya, Arjantin, Şili, Fransa, İspanya,
  Portekiz ve Prusya gibi geçersiz büyük başlangıç düzenleri dağıtıldı.
- Avrupa'da Lehistan-Litvanya, Baltık Prusya Dükalığı, Kraków ve üç Britanya
  tacı; Amerika'da yerel meclisler, kıyı kolonileri ve And devletleri;
  Afrika'da yerel egemenlikler işlendi.
- Mısır'ın Mavi Nil, Kordofan ve Eritre dışındaki doğrudan sınırı Dongola ile
  sınırlıdır. Afrika'daki Avrupalı depo payları yerel sahiplere döndü.
- Londra Tacı'nın tek doğrudan denizaşırı istisnası Bahamalar, Bermuda, Güney
  Atlantik ve Batı Hint Adaları'ndaki 11 kalan province'tir. Bu alanların
  sınırı `docs/scenario/diplomasi.md`de tanımlıdır.
- Güneydoğu Asya'da Mısır/Umman liman hakları state sahibi değildir; Aceh,
  Makassar, Johor ve Sulu sözleşmeleri siyasi ilişki kaydında görünür.

Yetkili siyasi kararlar [dünya atlası](../../../docs/scenario/dunya_atlasi.md),
[diplomasi](../../../docs/scenario/diplomasi.md), [state karar defteri](../../../docs/scenario/SIYASI_STATE_KARAR_DEFTERI.md), bölgesel senaryo dosyaları ve
[dünya siyasi inşa planında](../../../docs/scenario/SIYASI_INSA_PLANI.md)
tutulur. Atlas çıktısı bu belgelerin yerine geçmez.

## Yeniden üretme ve doğrulama

Kart üreticileri gerektiğinde gerçek kurulu oyun state/province verisini yeniden
okur. Aynı kaynak dizinde, şu komutlar siyasi önizlemeyi baştan üretir:

```sh
python3 scenarios/atlas/world_political/prepare_card00.py
# Değiştirilmiş bir kartın kendi prepare_cardNN.py üreticisini de çalıştır.
python3 scenarios/atlas/world_political/verify_cards.py
python3 scenarios/atlas/world_political/prepare_partial_preview.py
python3 scripts/tools.py atlas scenario validate build/world-political/partial-political-preview.json
python3 scripts/tools.py atlas scenario report build/world-political/partial-political-preview.json --out build/world-political/partial-political-report.json
python3 scripts/tools.py atlas scenario build build/world-political/partial-political-preview.json --out build/scenarios/world-political-preview
python3 scenarios/atlas/world_political/political_state_ledger.py
python3 scenarios/atlas/world_political/diplomacy_contract_audit.py
python3 scenarios/atlas/world_political/political_completion_audit.py
python3 scripts/tools.py atlas map --scenario build/world-political/partial-political-preview.json --mode changes --data --out build/maps/world-political-partial.png
```

`verify_cards.py`, bütün kartların beklenen şemasını, map-only kuralını,
çakışan state yazımını, yeni ülke başkentini ve kritik kapanışların sahiplerini
sınar. `political_state_ledger.py`, 675 state'in province geometrisini,
yasaklanan eski doğrudan sahipleri ve her state'in açık kart kararını
denetler. `political_completion_audit.py`, bunun yanında geçici ülke kaydını,
devralınan diplomasiyi ve Londra denizaşırı bağımlılıklarının sabit kapsamını
denetler; ayrıca etkin modu değiştirmeden `build/scenarios/` altındaki izole
paketi Atlas'ın sıkı üretilmiş-dünya denetiminden geçirir.

Kart önizlemesi `build/` altında kalır. Etkin oyun kaynağı artık
`world/scenario.yml`dir; [siyasi oyun kurulumu](../../../docs/scenario/SIYASI_OYUN_KURULUMU.md)
geçici nüfus/bina köprüsünü ve motor doğrulama kapısını açıklar. Kartlarda
sınır değiştirilirse etkin kaynak da güncellenir ve `active_political_audit.py`
ile eşitlik doğrulanır. Denetim, ilk kart önizlemesinden sonraki sekiz Hint
hub düzeltmesini, [Pegu'daki tek Danimarka province devrini](../demography_phase13_mainland_seasia/README.md)
ve [Samoa'nın Tonga state'indeki iki yerel province'ini](../demography_phase16_oceania/README.md)
ayrı, kesin province hareketleri olarak uygular. [Filipin demografi dilimindeki](../demography_phase14_maritime_seasia/README.md)
Tondo ve Visaya resmî din düzeltmesini de yalnız bu iki ülke için kesin
istisna olarak doğrular; ülke sınırlarını değiştirmez.
[Mağrip–Sahra demografi dilimindeki](../demography_phase17_maghreb_sahara/README.md)
`TUA` birincil kültür eklemesi de yalnız bu ülkenin tanımına dar istisnadır.

## Bölgesel karar kayıtları

1. `regions/00_middle_east_balkans.md`
2. `regions/01_europe_mediterranean.md`
3. `regions/02_india.md`
4. `regions/03_east_asia_seas.md`
5. `regions/04_africa.md`
6. `regions/05_americas_oceania.md`

Her kartta `pops: drop` ve `buildings: drop` zorunludur. Harita aşamasında
mekanik veriyi değiştirerek siyasi doğrulamayı bulandırmayız.
