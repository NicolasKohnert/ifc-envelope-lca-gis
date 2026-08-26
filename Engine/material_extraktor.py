import ifcopenshell.util.element

import logging

logger = logging.getLogger("BIM-GIS_Pipeline")

def get_material(element):

    material = ifcopenshell.util.element.get_material(element)

    if material is None :
        return []

    if material.is_a("IfcMaterial"):
        return [material.Name]

    elif material.is_a("IfcMaterialLayerSetUsage"):
        layer_set = material.forLayerSet
        return [layer.Material.Name for layer in layer_set.MaterialLayers if layer.Material]

    elif material.is_a("IfcMaterialLayerSet"):
        return [layer.Material.Name for layer in material.MaterialLayers iflayer.Material]

    elif material.is_a("IfcMaterialList"):
        return [m.Name for m in material.Material]

    else:
        logger.warning(f"Unknown material-type for {element.GlobalId}: {material.is_a()}")


def material_extraktor(ifc_model, elemente):
    ergebnisse = []
    ohne_material = 0

    for element in elemente:
        materialien = get_material(element)

        if not materialien:
            ohne_material +=1
            logger.warning(f"Missing material {element.GlobalID}:{element.is_a()}")

        ergebnisse.append({
            "guid": element.GlobalId,
            "ifc-type": element.is_a(),
            "name": element.Name or "Unknown",
            "materialien": materialien
        })
logger.info(f"{len(ohne_ergebnisse)}elements without material information/ {len(ergebnisse)}elements with material information")