import numpy as np
import ifcopenshell.geom
from shapely.geometry import Polygon
from logger import logger

def filter_aussenwand(ifc_model):
    import ifcopenshell.util.element
    exterior_walls = []
    for w in ifc_model.by_type("IfcWall"):
        psets = ifcopenshell.util.element.get_psets(w)
        pset_common = psets.get("Pset_WallCommon", {})
        is_external = pset_common.get("IsExternal", None)
        if is_external in (True, 1, "True", "true"):
            exterior_walls.append(w)
    logger.info(f"{len(exterior_walls)} walls found")
    return exterior_walls

def filter_dach(ifc_model):
    import ifcopenshell.util.element
    roof_elements = set()
    for roof in ifc_model.by_type("IfcRoof"):
        roof_elements.add(roof)
    for slab in ifc_model.by_type("IfcSlab"):
        pred_type = getattr(slab, "PredefinedType", None)
        if pred_type in ("Roof", "Roofing"):
            roof_elements.add(slab)
    logger.info(f"{len(roof_elements)} roofs found")
    return roof_elements

def filter_fundament(ifc_model):
    fundament_elemente = set()
    for fund in ifc_model.by_type("IfcFooting"):
        fundament_elemente.add(fund)
    for pile in ifc_model.by_type("IfcPile"):
        fundament_elemente.add(pile)
    for slab in ifc_model.by_type("IfcSlab"):
        pred_type = getattr(slab, "PredefinedType", None)
        if pred_type == "BASESLAB":
            fundament_elemente.add(slab)
    logger.info(f"{len(fundament_elemente)}foundtions found")
    return fundament_elemente

def huellen_extraktor(ifc_model):
    settings =ifcopenshell.geom.settings()

    gruppen = [
        (filter_aussenwand(ifc_model), "Aussenwand"),
        (filter_dach(ifc_model), "Dach"),
        (filter_fundament(ifc_model), "Fundament")
    ]

    huelle_daten = []
    fehler_count = 0

    for element, category in gruppen:
        try:
            shape = ifcopenshell.geom.create_shape(settings, element)
            verts = np.array(shape.geometry.verts).reshape(-1, 3)

            matrix = np.array(shape.transformation.matrix.data).reshape(4, 4).T
            homo_verts = np.hstack([verts, np.ones((len(verts), 1))])
            transformed_verts = (homo_verts @ matrix)[:, :3]

            min_x, min_y = np.min(transformed_verts[:, :2], axis=0)
            max_x, max_y = np.max(transformed_verts[:, :2], axis=0)
            poly = Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)])

            huelle_daten.append({
                "guid":element.GlobalId,
                "category": category,
                "ifc_type": element.is_a(),
                "name": element.Name,
                "geometry": poly
            })
        except Exception as e:
            fehler_count += 1
            logger.warning(f"Geomtry failure {element.GloablId}({category}): {e}")
    logger.info(f"{len(huelle_daten)} elements ready ,Failures: {fehler_count}")
    return huelle_daten
    
