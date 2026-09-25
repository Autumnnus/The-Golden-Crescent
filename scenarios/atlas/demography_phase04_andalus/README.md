# Demografi 4 — Endülüs ana yurdu ve doğrudan Atlantik adaları

**Etkin kaynak:** `world/scenario.yml`. Endülüs Federasyonu `VAN`ın 11 doğrudan state payında nüfus, ortak kültür–din, okuryazarlık ve yedi İberya homeland kaydı düzenlendi. Bağlı Amerika devletleri bu ülke toplamına katılmaz. Tasarım [plan.yml](plan.yml), eski POP kayıtları [dondurulmuş örnekte](legacy-population-snapshot.json), şehir alt kümeleri [city-profiles.yml](city-profiles.yml) içindedir.

| Alan | Nüfus |
|---|---:|
| Yedi İberya state'i | 16.240.000 |
| Cape Verde, Kanarya, Azor, Madeira | 1.260.000 |
| **Doğrudan Endülüs toplamı** | **17.500.000** |

Nüfus ağırlıklı okuryazarlık girdisi **%50,23**; yazılı 16–19 milyon ve %46–54 hedeflerindedir. Ülke toplamında yaklaşık 11,19 milyon Sünni, 5,58 milyon Katolik, 724 bin Yahudi ve küçük Protestan cemaat vardır. Müslüman nüfus Endülüslü, İspanyolca ve Portekizce konuşan gruplar arasında ayrı yazıldı. `ve_andalusi` kültürü yaklaşık 5,28 milyon kişiyi temsil eder; bu kültürün yerleşik İberya mirası ve Arapça dil özelliği [ek tanımda](../../../common/cultures/ve_andalusi.txt) bulunur. Portekizli ve İspanyol toplulukları siyasal federasyonda birincil kültür olarak da kalır. Tarihsel küçük POP grupları sessizce silinmedi.

Vanilla Cape Verde nüfusunun `afro_brazilian` kültür kimliği adaya tam uymaz; bu kayıt şimdilik kültür–din ve kişi sayısı korunarak kullanıldı. Uygun bir Atlantik ada kültürü, isim havuzu ve yerelleştirmesi ayrı tasarlanmalıdır. Aynı şekilde Hikmetiyye bir **hukuk geleneğidir**; burada tüm Hristiyan veya Yahudileri yeni dine dönüştüren bir POP kimliği yaratılmadı. Mevcut 12.012 köle POP'u ve 600 aristokrat, özellikle ada emeği ve hukuk aşaması gelene kadar aynen korunur.

15 yerleşim profili toplam **4.295.000** kişi tahmin eder. Bu, ülke nüfusunun %24,54'üdür; yazılı %25–31 kentleşme aralığında diğer kent ve kasabalara yer bırakır. Kurtuba, Sevilla ve Cadiz aynı Aşağı Endülüs state payının birbirini aşmayan alt kümeleridir. Kurulu oyunda Kurtuba `STATE_LOWER_ANDALUSIA_farm`, Sevilla `STATE_LOWER_ANDALUSIA_city` hub'ıdır. Lore'daki başkent Kurtuba'dır; ülkenin oyun başkenti state düzeyinde Aşağı Endülüs'e ayarlı olsa da şehir işaretinin Sevilla çıkması olasıdır. Hub konumunu yanlış etiketle değiştirmedik; bu arayüz/motor ayrıntısı daha sonra ayrı doğrulanmalıdır.

Mod kökünden:

```sh
python3 scenarios/atlas/demography_phase04_andalus/prepare.py
python3 scripts/tools.py atlas scenario validate build/demography/andalus-candidate.yml
python3 scripts/tools.py atlas scenario report build/demography/andalus-candidate.yml --out build/demography/andalus-candidate-report.json
python3 scripts/tools.py atlas scenario build build/demography/andalus-candidate.yml --out build/scenarios/andalus-demography-candidate
python3 scenarios/atlas/demography_phase04_andalus/verify.py
python3 scripts/tools.py atlas build
python3 scripts/tools.py atlas check
```

Statik denetim, 675 siyasi state'i ve VAN dışındaki tüm POP bloklarını, özel kültürün ülkede ve yedi homeland'de üretilmesini, eski köle/meslek POP'larını ve şehirlerin state ortak gruplarına sığmasını kontrol etti. `atlas build/check` sıfır hata verdi; önceki 25 ordu/state uyarısı sürüyor. Yeni nüfusla oyun başlangıcı ve zaman ilerlemesi henüz motor içinde sınanmadı. Şehir tahminleri oyuna ayrıca şehir POP'u olarak yazılmaz; state POP'larının tasarım alt kümeleridir.
