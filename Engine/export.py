import geopandas as gpd
from pathlib import Path
from logger import logger      
DEFAULT_CRS = "EPSG:25832"

def exportiere_geopackage(daten, ausgabe_pfad, layer_name, crs=DEFAULT_CRS):
    if not daten:
        logger.warning(f"No data for export in layer: {layer_name}--skipt")
        return None

    fehlende_geometrie = [i for i, item in enumerate(daten) if item.get("geometry") is None]
    if fehlende_geometrie:
        logger.warning(
            f"{len(fehlende_geometrie)} elements withou geometry in {layer_name}"
            f"deleted from export"
        )
        daten = [item for item in daten if item.get("geometry") is not None]

    if not daten:
        logger.warning(f"After cleaning no data for layer:{layer_name}-export skipet")
        return None

    try:
        gdf = gpd.GeoDataFrame(daten, geometry="geometry", crs=crs)

        ausgabe_pfad = Path(ausgabe_pfad)
        ausgabe_pfad.parent.mkdir(parents=True, exist_ok=True)

        gdf.to_file(str(ausgabe_pfad), layer=layer_name, drivers="GPKG")
        logger.info(f"{len(gdf)}features as layer {layer_name} to {ausgabe_pfad} exported")

    except Exception as e:
        logger.error(f"failure with export to Geopackage {layer_name}: {e}")
        raise


def exportiere_alle_modelle(voll_daten, huelle_daten, lod2_daten, ausgabe_verzeichnis="data/output"):
    ausgabe_pfad = Path(ausgabe_verzeichnis) / "bim_gis_ergebnis.gpkg"

    exportiere_geopackage(voll_daten, ausgabe_pfad, layer_name="modell_voll")
    exportiere_geopackage(huelle_daten, ausgabe_pfad, layer_name="modell_huelle")

    if lod2_daten is not None:
        exportiere_geopackage([lod2_daten], ausgabe_pfad, layer_name="modell_lod2")
    else:
        logger.info(f"No lod2 modell")

    logger.info(f"end of export: {ausgabe_pfad}")
    return ausgabe_pfad

if __name__ == "__main__":
    from shapely.geometry import Polygon
    test_daten =[ {
        "guid": "TEST-001",
        "category": "Aussenwand",
        "name": "Testwand",
        "co2_kg": 123.45,
        "geometry": Polygon([(0,0), (10,0), (10, 5), (0,5)]),
    }]
exportiere_geopackage(test_daten, "data/output/test.gpkg", layer_name="test_layer")
