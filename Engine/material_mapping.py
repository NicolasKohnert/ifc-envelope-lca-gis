MATERIAL_MAPPING = {
    "Raudbetoon - Konstruksioon": "Reinforced concrete",
    "Soojustus- vill pehme": "Mineral wool",
    "GENEERLINE - KONSTRUKTRIOON": None,
    "Soojustus- SPU": "Polyurethane rigid foam",
    "Air Space - Frame": None,
    "Soojustus- vill pehme välissein": "Mineral wool",
    "Öhkvahe": None,
    "Kipsplaat - weekindel": "Gypsum board",
    "KERGPLOKK": "Lightweight concrete block",
    "Kipsplaat": "Gypsum board" 
}

def mappe_material(ifc_material_name):
    return MATERIAL_MAPPING.get(ifc_material_name)