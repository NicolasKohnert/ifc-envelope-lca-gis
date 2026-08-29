import ifcopenshell.api
from logger import logger

def co2_in_ifc_schreiben(ifc_model, co2_ergebnisse):
    geschrieben = 0 
    nicht_gefunden = 0

    for item in co2_ergebnisse:
        element = ifc_model.by_guid(item["guid"])
        if element is None:
            nicht_gefunden += 1
            logger.warning(f"Element mit guid {item["guid"]} in model nicht gefunden")
            continue
        try:
            pset = ifcopenshell.api.run(
                "pset.add_pset", ifc_model,
                product=element, name="Pset_CO2Berechnung"
            )
            ifcopenshell.api.run(
                "pset.edit_pset", ifc_model,
                pset=pset,
                properties={
                    "CO2_kg": item["co2_kg"],
                    "Volumen_m3": item.get("volume"),
                },
            )
            geschrieben += 1
        except Exception as e:
            logger.error(f"Fehler beim schreiben bei {item["guid"]}:{e}")

    logger.info(f"{geschrieben}/{len(co2_ergebnisse)} Elemente mit CO2 propertiy versehen"
                f"({nicht_gefunden} GUIDs nicht im Model gefunden)")
    return ifc_model


def ifc_speichern(ifc_model, pfad):
    try:
        ifc_model.write(str(pfad))
        logger.info(f"IFC-Datei gespeichert: {pfad}")
    except Exception as e:
        logger.error(f"Fehler beim speichernder IFC Datei: {e}")
        raise
