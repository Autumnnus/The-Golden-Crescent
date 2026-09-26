"""Country adjectives (TAG_ADJ) for every named scenario country.

The game builds subject and dynamic names from the adjective ("<overlord adjective> <state>"); no
scenario country had one, so the opening screen showed raw keys such as "RUM_ADJ Erzurum".
Named countries get a written adjective from OVERRIDES; the rest use their place name with the
form-of-government words removed (English and Turkish separately).
Writes adjectives.yml (generated; review, do not hand-edit).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OVERRIDES = {  # tag: (English, Turkish)
    "RUM": ("Rumi", "Rûm"), "ISF": ("Isfahani", "İsfahan"), "TBR": ("Tabrizi", "Tebriz"),
    "KHO": ("Khorasani", "Horasan"), "MAZ": ("Mazandarani", "Mazenderan"), "KRM": ("Kermani", "Kirman"),
    "LUR": ("Luri", "Luristan"), "HUZ": ("Khuzestani", "Huzistan"), "KUR": ("Mosuli", "Musul"),
    "BSR": ("Basrawi", "Basra"), "SYR": ("Damascene", "Şam"), "LEB": ("Lebanese", "Lübnan"),
    "PAL": ("Jerusalemite", "Kudüs"), "KUW": ("Kuwaiti", "Kuveyt"), "BOS": ("Bosnian", "Bosna"),
    "ALB": ("Albanian", "Arnavut"), "BUL": ("Danubian", "Tuna"), "FPA": ("Parisian", "Paris"),
    "FBG": ("Burgundian", "Burgonya"), "FBR": ("Breton", "Bretonya"), "FAQ": ("Aquitanian", "Akitanya"),
    "FOC": ("Occitan", "Oksitanya"), "FPR": ("Provençal", "Provence"), "MUG": ("Mughal", "Gurkanî"),
    "PNJ": ("Sikh", "Sih"), "BGL": ("Bengali", "Bengal"), "MAR": ("Maratha", "Maratha"),
    "GJT": ("Gujarati", "Gucerat"), "TAM": ("Tamil", "Tamil"), "ORI": ("Odia", "Orissa"),
    "AWA": ("Awadhi", "Awadh"), "ASM": ("Assamese", "Assam"), "NAG": ("Nagpuri", "Nagpur"),
    "HYD": ("Hyderabadi", "Haydarabad"), "MYS": ("Mysorean", "Mysore"), "TRA": ("Travancorean", "Travankor"),
    "BUR": ("Burmese", "Burma"), "JAI": ("Jaipuri", "Jaipur"), "NCH": ("Northern Chinese", "Kuzey Çin"),
    "JNG": ("Jiangnanese", "Jiangnan"), "SHU": ("Shu", "Shu"), "YUE": ("Yue", "Yue"), "MCH": ("Manchu", "Mançu"),
    "MGL": ("Mongol", "Moğol"), "DZH": ("Dzungar", "Cungar"), "KSG": ("Kashgari", "Kaşgar"),
    "KZH": ("Kazakh", "Kazak"), "KIR": ("Kyrgyz", "Kırgız"), "VGE": ("Georgian", "Gürcü"),
    "VER": ("Erevani", "Erevan"), "VBA": ("Bakuvian", "Bakü"), "VDA": ("Dagestani", "Dağıstan"),
    "VCR": ("Crimean", "Kırım"), "VTA": ("Tatar", "Tatar"), "VKM": ("Kalmyk", "Kalmuk"),
    "VMS": ("Muscovite", "Moskova"), "VNG": ("Novgorodian", "Novgorod"), "VMA": ("Mari", "Mari"),
    "VMO": ("Mordvin", "Mordvin"), "VUR": ("Uralic", "Ural"), "VST": ("Siberian Tatar", "Sibirya Tatar"),
    "VBY": ("Buryat", "Buryat"), "VSA": ("Sakha", "Saha"), "VAN": ("Andalusian", "Endülüs"),
    "VCA": ("Castilian", "Kastilya"), "VAR": ("Aragonese", "Aragon"), "VGL": ("Galician", "Galiçya"),
    "VNV": ("Navarrese", "Navarra"), "MAS": ("Algerian", "Cezayir"), "CON": ("Constantinian", "Konstantin"),
    "VBR": ("Brandenburgian", "Brandenburg"), "VPM": ("Pomeranian", "Pomeranya"), "VRC": ("Rhenish", "Ren"),
    "ANH": ("Anhaltine", "Anhalt"), "VMI": ("Milanese", "Milano"), "VVE": ("Venetian", "Venedik"),
    "VEL": ("English", "İngiliz"), "VSC": ("Scottish", "İskoç"), "VIR": ("Irish", "İrlanda"),
    "GBR": ("London Crown", "Londra Tacı"), "VNE": ("New Andalusian", "Yeni Endülüs"), "VMY": ("Maya", "Maya"),
    "VPL": ("Polish-Lithuanian", "Leh-Litvanya"), "VSN": ("Sennari", "Sennar"), "VPI": ("Pearl Islander", "İnci Adaları"),
    "VNI": ("New English", "Yeni İngiltere"), "VNH": ("New Dutch", "Yeni Hollanda"), "VPA": ("Pennsylvanian", "Pennsylvania"),
    "VVA": ("Virginian", "Virginia"), "VBU": ("New Bursan", "Yeni Bursa"), "VIN": ("Vinlander", "Vinland"),
    "VDC": ("Potomac", "Potomac"), "VFB": ("Moroccan Brazilian", "Fas Brezilyası"), "VSI": ("New Ishbiliyan", "Yeni İşbiliye"),
    "VBO": ("Bohemian", "Bohemya"), "VBT": ("Brabantine", "Brabant"), "VLG": ("Liégeois", "Liège"),
    "VKN": ("Kandyan", "Kandy"), "VTD": ("Tondo", "Tondo"), "VVS": ("Visayan", "Visaya"),
    "VPD": ("Prussian", "Prusya"), "VIT": ("Isthmian", "Kıstak"), "VQU": ("Quiteño", "Quito"),
    "VCU": ("Cusqueño", "Cusco"), "VKC": ("Charcan", "Charcas"), "VMU": ("Muisca", "Muisca"),
    "VGZ": ("New Granadan", "Yeni Gırnata"), "VSM": ("Samoan", "Samoa"),
    "ADA": ("Adanan", "Adana"), "VNP": ("Northern Plateau", "Kuzey Plato"), "VPS": ("Southern Plateau", "Güney Plato"),
    "VRI": ("Southern Rivers", "Güney Nehirleri"), "VNR": ("Northeastern", "Kuzeydoğu"), "VCS": ("Central Chilean", "Orta Şili"),
    "VSO": ("Sonoran", "Sonora"), "VGC": ("Goiás", "Goiás"), "VBJ": ("Bajío", "Bajío"), "VTC": ("Tucumán", "Tucumán"),
}
EN_WORDS = r"\b(Grand Principality|Principality|Kingdom|Kingdoms|Empire|Duchy|Crown|Margraviate|Khanate|Khanates|Sultanate|" \
           r"Shahdom|Emirate|Atabegate|Republic|Confederation|Confederacy|League|Councils?|Assembl(y|ies)|Government|" \
           r"State|Civic|City|Trade|Port|Coastal|Coast|Highland|River|Rivers|Valley|Lake|Mining|Forest|Plateau|" \
           r"Maritime|Treaty|Island|Colonial|Charter|Mountain|Peoples|District|of|the)\b'?"
TR_WORDS = r"(?<!\w)(İmparatorluğu|Krallıkları|Krallığı|Büyük Prensliği|Prensliği|Dükalığı|Tacı|Marklığı|Hanlıkları|Hanlığı|" \
           r"Sultanlığı|Şahlığı|Emirliği|Atabeyliği|Cumhuriyeti|Konfederasyonu|Birlikleri|Birliği|Meclisleri|Meclisi|" \
           r"Yönetimi|Devleti|İmametleri|Kent|Ticaret|Liman|Kıyı|Yüksekova|Nehirleri|Nehri|Nehir|Vadi|Göl|Maden|Orman|" \
           r"Denizci|Deniz|Antlaşma|Ada|Koloni|Şartı|Dağ|Halkları|Bölgesi|Merkez)(?!\w)"


def strip(name: str, pattern: str) -> str:
    text = re.sub(pattern, "", name)
    return re.sub(r"\s+", " ", text).strip(" -–")


def main() -> None:
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    names = {tag: (c["name"], c.get("name_tr") or c["name"]) for tag, c in world["countries"].items() if c.get("name")}
    names["VGZ"] = ("New Granada", "Yeni Gırnata")
    table = {}
    for tag, (en, tr) in sorted(names.items()):
        adj = OVERRIDES.get(tag) or (strip(en, EN_WORDS) or en, strip(tr, TR_WORDS) or tr)
        table[tag] = {"en": adj[0], "tr": adj[1]}
    (HERE / "adjectives.yml").write_text(
        "# Generated by adjectives.py; review, do not hand-edit.\n" +
        yaml.safe_dump({"version": 1, "countries": table}, allow_unicode=True, sort_keys=True, width=110))
    print(f"{len(table)} adjectives ({sum(t in OVERRIDES for t in table)} written)")
    for tag, row in table.items():
        if tag not in OVERRIDES:
            print(f"  {tag}: {names[tag][0]} -> {row['en']} | {names[tag][1]} -> {row['tr']}")


if __name__ == "__main__":
    main()
