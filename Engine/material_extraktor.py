import ifcopenshell.util.element

from Engine.logger import logger

from Engine.material_mapping import mappe_material


def get_material(element, ifc_model):
    materialen = []
    
    # Suche direkt über die globalen Material-Relationen des Modells
    for rel in ifc_model.by_type("IfcRelAssociatesMaterial"):
        if element in rel.RelatedObjects:
            mat_obj = rel.RelatingMaterial
            
            if mat_obj.is_a("IfcMaterial"):
                if mat_obj.Name:
                    materialen.append(mat_obj.Name)
                    
            elif mat_obj.is_a("IfcMaterialLayerSetUsage"):
                layer_set = mat_obj.ForLayerSet
                if layer_set and hasattr(layer_set, "MaterialLayers"):
                    for layer in layer_set.MaterialLayers:
                        if layer.Material and layer.Material.Name:
                            materialen.append(layer.Material.Name)
                            
            elif mat_obj.is_a("IfcMaterialLayerSet"):
                if hasattr(mat_obj, "MaterialLayers"):
                    for layer in mat_obj.MaterialLayers:
                        if layer.Material and layer.Material.Name:
                            materialen.append(layer.Material.Name)
                            
            elif mat_obj.is_a("IfcMaterialList"):
                if hasattr(mat_obj, "Materials"):
                    for m in mat_obj.Materials:
                        if m.Name:
                            materialen.append(m.Name)
                            
    # Fallback auf den Bauteiltyp, falls direkt nichts gefunden wurde
    if not materialen and hasattr(element, "IsTypedBy"):
        for rel in element.IsTypedBy:
            ifc_type = rel.RelatingType
            if ifc_type:
                for assoc in ifc_model.by_type("IfcRelAssociatesMaterial"):
                    if ifc_type in assoc.RelatedObjects:
                        mat_obj = assoc.RelatingMaterial
                        if mat_obj.is_a("IfcMaterialLayerSetUsage") and mat_obj.ForLayerSet:
                            for layer in mat_obj.ForLayerSet.MaterialLayers:
                                if layer.Material and layer.Material.Name:
                                    materialen.append(layer.Material.Name)
                        elif mat_obj.is_a("IfcMaterial") and mat_obj.Name:
                            materialen.append(mat_obj.Name)
                            
    return materialen

def material_extractor(ifc_model, elemente):
    # Schritt 1: Einmalig alle Material-Zuordnungen im Modell vorab einlesen (High-Performance-Index)
    mat_map = {}
    
    for rel in ifc_model.by_type("IfcRelAssociatesMaterial"):
        mat_obj = rel.RelatingMaterial
        materialen = []
        
        if mat_obj.is_a("IfcMaterial") and mat_obj.Name:
            materialen.append(mat_obj.Name)
        elif mat_obj.is_a("IfcMaterialLayerSetUsage") and mat_obj.ForLayerSet:
            for layer in mat_obj.ForLayerSet.MaterialLayers:
                if layer.Material and layer.Material.Name:
                    materialen.append(layer.Material.Name)
        elif mat_obj.is_a("IfcMaterialLayerSet"):
            for layer in mat_obj.MaterialLayers:
                if layer.Material and layer.Material.Name:
                    materialen.append(layer.Material.Name)
        elif mat_obj.is_a("IfcMaterialList"):
            for m in mat_obj.Materials:
                if m.Name:
                    materialen.append(m.Name)
                    
        for obj in rel.RelatedObjects:
            mat_map[obj.id()] = materialen

    # Schritt 2: Typ-Zuordnungen einbeziehen (Vererbung vom IfcType auf die Instanz)
    for rel in ifc_model.by_type("IfcRelDefinesByType"):
        relating_type = rel.RelatingType
        if relating_type.id() in mat_map:
            for obj in rel.RelatedObjects:
                if obj.id() not in mat_map:
                    mat_map[obj.id()] = mat_map[relating_type.id()]

    # Schritt 3: Elemente abfragen und verarbeiten
    ergebnisse = []
    ohne_material = 0
    
    for element in elemente:
        materialien = mat_map.get(element.id(), [])
        
        if not materialen:
            ohne_material += 1
            logger.warning(f"Missing material {element.GlobalId} ({element.is_a()})")
            continue
            
        oekobaudat_begriffe = []
        for mat_name in materialien:
            ziel = mappe_material(mat_name)
            if ziel is None:
                logger.warning(f"{element.GlobalId}: Material '{mat_name}' not found")
            else:
                oekobaudat_begriffe.append(ziel)
                
        ergebnisse.append({
            "guid": element.GlobalId,
            "ifc_type": element.is_a(),
            "name": element.Name or "Unknown",
            "materialien": materialien,
            "oekobaudat_suchbegriffe": oekobaudat_begriffe
        })
        
    logger.info(f"{ohne_material} elements without material information / {len(ergebnisse)} extracted")
    return ergebnisse

if __name__ == "__main__":
    import ifcopenshell
    from Engine.ifc_loader import load_ifc_file
    
    model = load_ifc_file("AC-20-Smiley-West-10-Bldg.ifc")
    element_types = [
            "IfcWall", "IfcSlab", "IfcColumn", "IfcBeam",
            "IfcRoof", "IfcFooting", "IfcPile", "IfcDoor", "IfcWindow"
        ]
    elements = [e for t in element_types for e in model.by_type(t)]
    materials = material_extractor(model,elements)
    for m in materials:
            print(m)