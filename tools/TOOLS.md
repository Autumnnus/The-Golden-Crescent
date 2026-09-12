# Araç seçimi ve birlikte çalışma

Bu repository'de iki ayrı yazarlık aracı vardır. Kullanıcının hikâyesini uygun araca yönlendir; kaynakları tek dosyada birleştirme.

| İş | Araç / kaynak | Rehber |
|---|---|---|
| Başlangıç haritası, ülke sınırları, nüfus, binalar, şirketler, teknoloji, kanunlar, ordu, diplomasi | **Atlas** — `tools/tgc.py`, `world/` veya ayrı V2 senaryo | [LLM senaryo akışı](LLM_SCENARIO_WORKFLOW.md) |
| Oyun sırasında event, seçim, günlük, siyasi/kültürel/dinî hikâye zinciri, tetikleme ve GFX | **Flavor Studio** — `tools/flavor/flavor.py`, `flavor/projects/` | [LLM flavor akışı](flavor/docs/LLM_WORKFLOW.md) |

**Kolay başlatıcılar:** `Atlas.command/.bat/.sh` ve `Flavor.command/.bat/.sh`. İkisi de sunucusuz önizleme üretir. Birinin açık veya çalışıyor olması diğerinin önkoşulu değildir.

İkisi gerekiyorsa önce Atlas başlangıç dünyasını doğrula; ülke filtresiz `scenario report` üret. Flavor komutlarına raporu `--context` ile ver. Böylece yeni ülke kimlikleri ve çıkarılmış ülkeler kontrol edilir; rapor değişikliği flavor onayını geçersiz kılar. Flavor başlangıç dünyasını değiştirmez; rapor gelecekteki oyun durumu değildir.

**Flavor için kullanıcı onayı zorunludur:** Plan ve diyagram üretilebilir; o sürüm onaylanmadan event/journal oyun dosyaları derlenmez veya kurulmaz. Atlas'a verilmiş onay Flavor için otomatik onay sayılmaz. Onaydan sonra paket derlenir, incelenir ve kullanıcı etkin entegrasyon istediyse kurulur. Yeni ülke tanımları önce Atlas'tan etkin moda gelmelidir.

Dosya sahipliği ayrı tutulur: Atlas `tgc_*` / `ve_scenario_*`; Flavor `ve_flavor_<namespace>` dosyalarını ve kendi GFX klasörünü yönetir. Flavor tam history katmanı veya metadata `replace_paths` üretmez. Her araç diğerinin üretilmiş dosyalarını elle düzenlememelidir.

Her iki araçta da “statik kontroller geçti” ile “oyun motorunda çalıştırıldı” farklı sonuçlardır. Özellikle ülke kaldırılması, saved scope referansları ve olayların zamanlaması için kapsam dışındaki içerikleri ayrıca değerlendir.
