import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from geometry_huelle import huellen_extraktor
from logger import logger

def lod2_erzeugen(ifc_model):
    huellen_daten = huellen_extraktor(ifc_model)

    if not huellen_daten:
        logger.warning(f"No sheldata found- LOD2 cannot be created")
        return None

    alle_polygone = [item["geometry"] for item in huellen_daten]
    vereinigte_form = unary_union(alle_polygone)

    if isinstance(vereinigte_form, MultiPolygon):
        logger.warning(f"{len(vereinigte_form.geoms)} seperate buildingelementsfound - get convex shell")
        verinigte_form = vereinigte_form.convex_hull

    grundflaeche = vereinigte_form.area

    gebaeude_min_z = min(item["min_z"] for item in huellen_daten)
    gebaeude_max_z = min(item["max_z"] for item in huellen_daten)
    gebaeude_hoehe = gebaeude_max_z -  gebaeude_min_z

    lod2_daten = {
        "name": "LOD2-BUILDINGBLOCK",
        "geometry": vereinigte_form,
        "grundflaeche_m2": round(grundflaeche, 2),
        "hoehe_m": round(gebaeude_hoehe, 2),
        "basis_z": round(gebaeude_min_z, 2),
        "anzahl_huellenelemente": len(huellen_daten),
        "guids_enthalten": [item["guid"] for item in huellen_daten]
    }

    logger.info(
        f"LOD2-Block ready: {grundflaeche:.2f}m² area,"
        f"{gebaeude_hoehe:.2f}m height from {len(huellen_daten)} shellelements"
    )
    return lod2_daten

