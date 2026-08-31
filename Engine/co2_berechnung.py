from logger import logger

def berechne_co2(material_daten, mengen_daten, gwp_lookup):
    mengen_by_guid = {m["guid"]: m for m in mengen_daten}
    ergebnisse = []
    uebersprungen_ohne_volumen = 0
    uebersprungen_ohne_material = 0

    for mat in material_daten:
        guid = mat["guid"]
        menge = mengen_by_guid.get(guid)

        if menge is None or menge.get("volume") is None:
            uebersprungen_ohne_volumen += 1
            logger.warning(f"{guid}: No volumne--skipt")
            continue

        gwp_summe = 0.0
        matchbar = False
        for begriff in mat.get("oekobaudat_suchbegriffe", []):
            faktor = gwp_lookup.get(begriff)
            if faktor is not None:
                gwp_summe += faktor
                matchbar = True

        if not matchbar:
            uebersprungen_ohne_material += 1
            logger.warning(f"{guid}: no machable material--skipt")
            continue

        co2_kg = menge["volume"]*gwp_summe
        ergebnisse.append({
            "guid":guid,
            "ifc_type": mat.get("ifc_type"),
            "name": mat.get("name"),
            "volume": menge["volume"],
            "gwp_faktor": round(gwp_summe, 4),
            "co2_kg": round(co2_kg, 2)
        })

    logger.info(
        f"{len(ergebnisse)}/{len(material_daten)} element calculation sucessfull"
        f"({uebersprungen_ohne_volumen} without volume, {uebersprungen_ohne_material} without material)"
        )
    return ergebnisse


