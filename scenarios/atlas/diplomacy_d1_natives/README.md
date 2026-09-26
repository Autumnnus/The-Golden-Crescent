# D1 — Merkezsiz yerli topluluklar

**25 Eylül 2026 · etkin.** Kullanıcı kararı: Amerika'da yalnız Aztek (Mezoamerika) ve İnka (And) alanlarındaki devletler ile koloni ve koloni kökenli devletler örgütlü devlet olarak kalır. Diğer yerli toplulukların toprağı kolonileştirilebilir olmalıdır. Aynı karar Sibirya'nın küçük meclislerine de uygulandı. Muisca ve Cauca And kent devletleri olarak devlet kaldı.

[plan.yml](plan.yml) listesindeki **50 ülke** (7,60 milyon kişi) `decentralized` oldu:
- 22 Kuzey Amerika meclisi ve konfederasyonu (Indian Territory ve Oregon dahil);
- 5 Kuzey Meksika meclisi;
- 16 And dışı Güney Amerika ülkesi (Paraguay, Uruguay, Piratini, Grão-Pará dahil);
- 7 Sibirya meclisi.

Oyunda merkezsiz statü toprağı sahipsiz yapmaz: halk, kültür, din, homeland, sınır ve okuryazarlık girdisi aynen kalır. Toprak yalnız vanilla yerlileri gibi kolonileştirilebilir olur. Bu ülkelerin ekonomisi, siyaseti ve araştırması yoktur; oyuncu tarafından oynanamazlar.

- **44 M1 ülkesi:** [classify.py](../mechanics_m1_institutions/classify.py) bu listeyi okur. Ülkeler 7. kademeye ve merkezsiz kanun setine (chiefdom, elder council...) iner. M1 alanlarını [M1b hazırlayıcısı](../mechanics_m1b_literacy/prepare.py) yazar. Kurumları boş olarak açıkça yazılır, çünkü senaryo önizlemesi ülke alanlarını etkin dünyayla birleştirir.
- **Altı vanilla etiket** (SEQ, ORG, PRA, PNI, PRG, URU): `history_mode: replace`, 7. kademe, aynı kanun seti ve ordusuz başlangıç. Vanilla cumhuriyet, kölelik, seçim ve ordu history'leri artık geçerli değil. Bu, DEVIR_NOTU'ndaki "köle POP'u kalmamış ülkelerde kölelik kanunu" açığını da SPU dışında kapatır. Vanilla karakter dosyaları [runtime override](../../runtime_cleanup/README.md) ile boşaltıldı.
- M0/M2'de bu ülkelere yazılmış açık binalar (38 pay, 209 seviye) kaldırıldı. Devralınan vanilla binalarını Atlas kendisi düşürür. Dünya toplamı 14.398 → 14.189 seviye.

Doğrulama ([verify.py](verify.py)): yalnız listedeki ülkeler değişti; nüfus, diğer ülkelerin bina, kanun ve teknolojileri korundu; yeni uyarı çıkmadı (iki istihdam uyarısı kalktı). Etkinleştirme sonrası `check` 0 hata, 13 uyarı.

```sh
cp world/scenario.yml build/diplomacy/d1-source.yml; cp build/world-political/active-political-report.json build/diplomacy/d1-source-report.json
python3 scenarios/atlas/mechanics_m1_institutions/classify.py --source build/mechanics/m1b-source.yml --targets scenarios/atlas/mechanics_m1b_literacy/targets.yml
python3 scenarios/atlas/diplomacy_d1_natives/prepare.py
python3 scenarios/atlas/mechanics_m1b_literacy/prepare.py --source build/diplomacy/d1-stage.yml --out build/diplomacy/d1-candidate.yml
python3 scripts/tools.py atlas scenario validate build/diplomacy/d1-candidate.yml
python3 scripts/tools.py atlas scenario build build/diplomacy/d1-candidate.yml --out build/scenarios/d1-candidate
python3 scenarios/atlas/diplomacy_d1_natives/verify.py
```

**Sınır:** Vanilla journal/event dosyalarında Paraguay ve Brezilya zincirleri (ör. `02_paraguay.txt`) bu etiketlere hâlâ bakar. Merkezsiz ülkede `has_events = no` olduğu için çoğu tetiklenmez; açılış logunda kontrol edilmeli.
