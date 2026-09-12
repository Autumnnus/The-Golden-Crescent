# Flavor projeleri

Her hikâyeyi ayrı klasörde tut:

```text
flavor/projects/hikayenin_adi/
  plan.yml
  assets/         # gerekiyorsa özgün DDS/BK2/poster dosyaları
```

Buraya örnek otomatik etkinleştirilmez. Örnek diyagram: `python3 scripts/tools.py flavor preview @examples/flavor/academy.yml --open`. Ortak çalışma sözleşmesinin konumunu `python3 scripts/tools.py docs` gösterir. Oyun çıktıları buraya yazılmaz; onaydan sonra `build/flavor/` altında oluşur.
