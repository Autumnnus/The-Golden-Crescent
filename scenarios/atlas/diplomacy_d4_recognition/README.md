# D4 — Senaryoya göre tanınma

**25 Eylül 2026 · etkin.** Kullanıcı kararı: vanilla 1836'nın "Batı kulübü" tanınma düzeni bu evrene aykırıdır. İslam devletleri tanınmış olmalıdır. Çin'de kurulan yeni devletler gibi Müslüman olmayan devletler ve Amerika'nın yerli devletleri tanınmamış olmalıdır.

Kural ([plan.py](plan.py) → [plan.yml](plan.yml)):
- Merkezsiz olmayan her **İslam devleti → tanınmış.** 78 ülke, 65,5 milyon kişi. Başlıcaları: Mısır, Fas, Tunus, Trablus, Umman, Sokoto, Bornu, Massina, Hicaz, Necd, Zeydî Yemen, Buhara, Hive, Hokand, Kabil, Herat, Sind, Aceh, Yogyakarta, Surakarta, Johor, Sulu, Somali ve Svahili kıyı devletleri.
- **Avrupa, Avrupa kökenli koloni ve yerleşimci devletler** ile Hristiyan Kafkasya krallıkları (Gürcistan, Erevan) **tanınmış kalır.** Kullanıcının kararı Avrupa'yı açıkça belirtmediği için bu grup korundu.
- Diğer bütün örgütlü **Müslüman olmayan devletler → tanınmamış.** 32 ülke, 428,8 milyon kişi:
  - Jiangnan, Kuzey Çin, Yue, Shu, Mançurya, Moğol ve Cungar hanlıkları, Buryat;
  - Maratha, Nagpur, Tamil, Mysore, Travankor, Orissa, Assam, Sih devleti, Jaipur, Kandy, Burma;
  - Tondo ve Visaya birlikleri;
  - Mari, Mordvin, Kalmuk;
  - Quito, Cusco, Kuzey ve Güney Peru, Muisca, Cauca, Orta Şili, Maya Birliği.
  - Japonya, Kore, Siam, Dai Nam, Etiyopya devletleri zaten tanınmamıştı.

Yalnız `country_type` değişir. M1 teknoloji kademeleri ve kanunları dondurulmuş M1b öncesi kaynaktan hesaplandığı için değişmedi. Bağlılık türleri ve antlaşma maddeleri iki türe de izin verir.

Doğrulama ([verify.py](verify.py)): yalnız planlanan türler değişti; üretilen ülke tanımları yeni türü taşıyor; nüfus, bina, kanun, teknoloji ve diplomasi değişmedi; yeni uyarı yok.

**Oyun etkisi:** Tanınmamış devletler büyük güç rütbesine çıkamaz ("tanınmamış büyük güç" en yüksek rütbeleridir). Tanınma için diplomatik oyun başlatabilirler. Tanınmış devletler onlara karşı bazı savaş hedeflerini daha kolay kullanır. Çin ve Hindistan'ın büyük devletleri bu yüzden 1836'da İslam güçlerinin ve Avrupa'nın gerisinde başlar.
