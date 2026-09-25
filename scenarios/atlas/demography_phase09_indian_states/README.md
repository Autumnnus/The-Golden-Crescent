# Demografi 9 — diğer büyük Hint devletleri

Etkin `world/scenario.yml` için [plan](plan.yml), **15 ülkenin 18 doğrudan state payını** kapsar: Sih Devleti, Keşmir, Jaipur, Udaipur/Mewar, Jodhpur, Awadh, Sindh, Gujarat liman birliği, Haydarabad, Mysore, Tamil devleti, Travankor, Koçin, Assam ve Kandy. Gurkanî, Bengal ve Maratha üyelerinin önceki sayıları korunur; bağımlılar üst ülkeye ikinci kez eklenmez.

Başlangıç nüfusunun çoğu kurulu oyunun bu sınırlara aktarılan topluluklarına yakındı. Bu nedenle [dondurulmuş kaynak POP'ları](source-pops.json) kullanılarak her yerel kültür–din çifti ölçülü oranda yeniden dağıtıldı; hükümdar dini bütün halka uygulanmadı. Okuryazarlık **açık Atlas girdisidir**, motorun hesaplayacağı gerçek oran veya kesin meslek eğitimi sonucu değildir. Aşağıdaki sayılar doğrudan ülke nüfusudur:

| Ülke | Kişi | Okuryazarlık girdisi |
|---|---:|---:|
| `PNJ` Sih | 1.650.000 | %24 |
| `KAS` Keşmir | 1.300.000 | %21 |
| `JAI` Jaipur; `MEW` Mewar; `JOD` Jodhpur | 2.100.000; 620.000; 1.360.000 | %20; %18; %17 |
| `AWA` Awadh; `SIN` Sindh; `GJT` Gujarat | 8.600.000; 2.000.000; 2.800.000 | %21; %19; %25 |
| `HYD` Haydarabad | 15.500.000 | %17–22, dört pay ağırlıklı yaklaşık %20,7 |
| `MYS` Mysore; `TAM` Tamil | 4.400.000; 8.700.000 | %22; %22 |
| `TRA` Travankor; `COC` Koçin | 2.200.000; 540.000 | %24; %24 |
| `ASM` Assam; `VKN` Kandy | 1.800.000; 1.300.000 | %19; %21 |

Sih devletinde Sih nüfus yaklaşık %17; Pencaplı Sünni ve Hindu topluluklar da çok büyüktür. Keşmir'de Sünni vadi çoğunluğu, Gujarat'ta Hindu çoğunluklu ticaret toplumu, Awadh ve Haydarabad'da hanedan inancından ayrı büyük Hindu nüfus korunur. Haydarabad'ın dört payı tek toplama gider; ayrı dört ülke sayılmaz. Sindh, Haydarabad, Tamil, Assam ve Kandy'deki devralınmış bağlı/köle meslekleri yazılı H8 hukuk hedefi oyun kanununa ayrıca çevrilene kadar sayısal olarak korunur. Bağımsız Hint idaresindeki az sayıdaki İngiliz/İskoç/Fransız memur, subay ve aristokrat yerel aynı mesleğe aktarılır. Gujarat'taki 800 Britanyalı özel kapitalist ile sıradan yabancı yerleşimciler otomatik silinmez. Gujarat'taki vanilla `persian/animist` küçük grup `persian/shiite` olarak düzeltilir.

[23 şehir profili](city-profiles.yml) birer state-owner POP **alt kümesidir**; ek oyun nüfusu değildir. Hub province'lerinin siyasi sahibi ve her şehirdeki kültür–din alt toplamları aday POP'larla denetlendi. [Atlas önizlemesi](../../../build/maps/indian-states-demography.html) siyasi sınırın değişmediğini gösterir. `prepare.py` aday üretir; `verify.py` diğer POP ve siyasi alanları, ülke toplamlarını, meslekleri, şehir alt kümelerini denetler. Aday validate/build, etkin build/check ve siyasi denetim geçti: **0 hata, önceki 25 uyarı**. Dünya toplamı **1.083.769.766** oldu.

**Kalan:** küçük Hint devletlerinin sayısal profilleri, binalar/istihdam, kanun–kurum uyumu, ordu/teknoloji ve oyun içi nüfus-ekonomi testi. Bu profil şehir nüfusunu meslek, konut veya gerçek kentleşme mekaniğine çevirmiyor. Önceki açılış testi siyasi haritayı göstermişti; bu yeni demografik revizyon motor içinde henüz sınanmadı.
