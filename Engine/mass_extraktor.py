import ifcopenshell.util.element
import ifcopenshell.geom
from Engine.logger import logger


settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)


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

    if volume is None:
        try:
            shape = ifcopenshell.geom.create_shape(settings, element)
            if shape and shape.geometry:
                verts = shape.geometry.verts
                faces = shape.geometry.faces

                calc_volume = 0.0
                for i in range(0, len(faces), 3):
                    p1 = (verts[3*faces[i]], verts[3*faces[i]+1], verts[3*faces[i]+2])
                    p2 = (verts[3*faces[i+1]],verts[3*faces[i+1]+1], verts[3*faces[i+1]+2])
                    p3 = (verts[3*faces[i+2]], verts[3*faces[i+2]+1], verts[3*faces[i+2]+2])

                    calc_volume += (p1[0] * (p2[1]*p3[2] - p3[1]*p2[2]) +
                                    p1[1] * (p2[2]*p3[0] - p3[2]*p2[0]) + 
                                    p1[2] * (p2[0]*p3[1] - p3[0]*p2[1]))/ 6.0
                return abs(calc_volume)
        except Exception as e:

            if element.is_a("IfcRoof") and hasattr(element, "IsDecomposedBy"):
                sub_volume =0.0
                has_sub_elements = False
                for rel in element.IsDecomposedBy:
                    for part in rel.RelatedObjects:
                        v = get_mass(part)
                        if v is not None:
                            sub_volume += v
                            has_sub_elements = True
                if has_sub_elements:
                    return sub_volume
            logger.warning(f"Geometriefehler bei {element.GlobalId} ({element.is_a()}): {e}")

    return volume

def mass_extractor(elemente):
    ergebnisse = []
    ohne_menge = 0

    for element in elemente:
        volume = get_mass(element)

        if volume is None:
            ohne_menge += 1
            logger.warning(f"{element.GlobalId} ({element.is_a()}) has no extracable volume")

        ergebnisse.append({
            "guid":element.GlobalId,
            "ifc_type": element.is_a(),
            "name": element.Name,
            "volume": round(volume, 2) if volume is not None else None
        })

    logger.info(f"{len(elemente) - ohne_menge}/{len(elemente)} with volume exctracted")
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

    masses = mass_extractor(elements)
    for m in masses:
        print(m)