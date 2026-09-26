# D2 — Bağlılık ağı

**25 Eylül 2026 · etkin; türler [D5](../diplomacy_d5_vanilla_subjects/README.md) ile vanilla'ya çevrildi.** Aşağıdaki ağ geçerlidir; özel tür adları ve gelir oranları artık kullanılmıyor. Kullanıcı kararları: İsfahan Fars devletlerini, Paris beş Fransız devletinin hepsini, Mısır Nil ve Libya kuşağını tutar. Tebriz İsfahan'ın vassalı değil müttefikidir ([D3](../diplomacy_d3_treaties/README.md)). Levant ortak garantili tampon kalır. Bağlılık sayısı 27 → **63**.

| Üst devlet | Yeni bağlılar | Tür |
|---|---|---|
| İsfahan | Horasan, Mazenderan, Kirman, Luristan, Huzistan; Herat | Şah Vassalı; haraç |
| Tebriz | Bakü, Erevan | sınırlı koruma |
| Paris | Burgonya, Akitanya, Oksitanya, Bretonya, Provence | Feodal Vassal (liberty desire 35–55; Burgonya en yüksek) |
| Mısır | Sennar, Trablus; Fizan, Darfur (Hicaz mevcut) | Nil Sözleşmesi; haraç |
| Umman | Trucial kıyısı, Mahra, Kathiri | sınırlı koruma |
| Büyük Tatar Hanlığı | **Moskova** (Tatar Haracı, liberty desire 65), Mari, Mordvin, Kalmuk | haraç / özerk bağlılık |
| Lehistan–Litvanya | Baltık Prusya Dükalığı | sözleşmeli vassal |
| Danimarka (Kalmar dış kurulu) | Vinland; Schleswig, Holstein | sömürge şartı; Taç Birliği |
| İngiltere–Galler | İrlanda Tacı; Londra Tacı Denizaşırı Bağımlılıkları | Taç Birliği; sömürge şartı |
| Buhara / Hokand | Maimana, Kunduz / Kırgız Birlikleri | haraç |
| Haydarabad | Kurnool | sözleşmeli vassal |
| Endülüs | San Salvador, Nikaragua meclisleri | haraç |

Yeni türler [plan.yml](plan.yml) içinde tanımlıdır:
- `ve_shah_vassal`: vassal tabanı, savaşa katılır, %8 gelir.
- `ve_feudal_vassal`: vassal, savaşa katılır, %10.
- `ve_nile_compact`: vassal, %6.
- `ve_crown_union`: personal union tabanı, üst devletin hükümdarını kullanır, %5.
- `ve_tatar_tribute`: tributary, %7.

Hiçbir yeni tür alt bağlı tutamaz. Mevcut 27 bağlılık değişmedi.

Doğrulama ([verify.py](verify.py)): liste = kaynak + plan; raporlanan üst devlet ağı plana eşit; ülke içerikleri ve uyarılar değişmedi.
