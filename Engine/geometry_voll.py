import numpy as np
import ifcopenshell.geom
from shapely.geometry import Polygon
from logger import logger

def volle_geometry(ifc_model, elementtypen=None):
    if elementtypen is None:
        elementtypen = [
            "IfcWall","IfcSlab", "IfcColumn", "IfcBeam",
            "IfcRoof", "IfcFooting", "IfcPile", "IfcDoor", "IfcWindow"
        ]

    settings = ifcopenshell.geom.settings()

    voll_daten = []
    fehler_count = 0
    verarbeitet_count = 0

    for ifc_typ in elementtypen:
        elemente = ifc_model.by_type(ifc_typ)
        logger.info(f"{len(elemente)} elements with typ {ifc_typ} found")

        for element in elemente:
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                verts= np.array(shape.geometry.verts).reshape(-1, 3)

                matrix = np.array(shape.transformation.matrix.data).reshape(4, 4).T
                homo_verts = np.hstack([verts, np.ones((len(verts), 1))])
                transformed_verts = (homo_verts @ matrix)[:, :3]

                min_x, min_y = np.min(transformed_verts[:,2], axis=0)
                max_x, max_y = np.max(transformed_verts[:,2], axis=0)
                poly = Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)])

                voll_daten.append = ({
                    "guid": element.GlobalId,
                    "ifc_type": element.is_a(),
                    "name": element.Nmae,
                    "geometry": poly
                })
                verarbeitet_count += 1

            except Exception as e:
                fehler_count += 1
                logger.warning(f"Geometric failure on{element.GlobalId}({ifc_typ}): {e}")

    logger.info(f"{verarbeitet_count}elements ready, {fehler_count}failures detected")
    return voll_daten
