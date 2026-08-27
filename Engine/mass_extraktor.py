import ifcopenshell.util.element
from logger import logger




def get_mass(element):
    psets = ifcopenshell.util.element.get_psets(element)

    qto= (
        psets.get("Qto_WallBaseQuantities", {})
        or psets.get("Qto_SlabBaseQuantities", {})
        or psets.get("Qto_FootingBaseQuantities", {})
        or psets.get("Qto_ColumnBaseQuantities", {})
        or psets.get("Qto_BeamBaseQuantities", {})
    )

    volume = qto.get("NetVolume") or qto.get("GrossVolume")
    return volume

def mass_extractor(elemente):
    ergebnisse = []
    ohne_menge = 0

    for element in elemente:
        volume = get_mass(elemente)

        if volume is None:
            ohne_menge += 1
            logger.warning(f"{element.GlobalId} ({element.is_a()}) has no extracable volume")

        ergebnisse.append({
            "guid":element.GlobalId,
            "ifc_type": element.is_a(),
            "name": element.Nmae,
            "volume": round(volume, 2) if volume is not None else None
        })

    logger.info(f"{len(elemente) - ohne_menge}/{len(elemente)} with volume exctracted")
    return ergebnisse