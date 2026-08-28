import ifcopenshell.util.element

import logging

from material_mapping import mappe_material

logger = logging.getLogger("BIM-GIS_Pipeline")

def get_material(element):

    material = ifcopenshell.util.element.get_material(element)

    if material is None :
        return []

    if material.is_a("IfcMaterial"):
        return [material.Name]

    elif material.is_a("IfcMaterialLayerSetUsage"):
        layer_set = material.ForLayerSet
        return [layer.Material.Name for layer in layer_set.MaterialLayers if layer.Material]

    elif material.is_a("IfcMaterialLayerSet"):
        return [layer.Material.Name for layer in material.MaterialLayers if layer.Material]

    elif material.is_a("IfcMaterialList"):
        return [m.Name for m in material.Materials]

    else:
        logger.warning(f"Unknown material-type for {element.GlobalId}: {material.is_a()}")


def material_extraktor(ifc_model, elemente):
    ergebnisse = []
    ohne_material = 0

    for element in elemente:
        materialien = get_material(element)

        if not materialien:
            ohne_material +=1
            logger.warning(f"Missing material {element.GlobalId}:{element.is_a()}")

    oekobaudat_begriffe = []
    for mat_name in materialien:
        ziel = mappe_material(mat_name)
        if ziel is None:
            logger.warning(f"{element.GlobalId}: Material'{mat_name}'not found")
        oekobaudat_begriffe.append(ziel)

        ergebnisse.append({
            "guid": element.GlobalId,
            "ifc_type": element.is_a(),
            "name": element.Name or "Unknown",
            "materialien": materialien,
            "oekobaudat_suchbegriffe": oekobaudat_begriffe
        })
    logger.info(f"{len(ohne_material)}elements without material information/ {len(ergebnisse)}elements with material information")
    return ergebnisse