from Engine.logger import logger

def berechne_co2(material_daten, mengen_daten, gwp_lookup, dichte_lookup=None):
    if dichte_lookup is None:
        # Standard-Rohdichten in kg/m³ für gängige Materialien
        dichte_lookup = {
            "steel": 7850.0,
            "stahl": 7850.0,
            "gypsum": 900.0,
            "gips": 900.0,
            "concrete": 2400.0,
            "beton": 2400.0,
            "holz": 650.0,
            "timber": 650.0,
            "glas": 2500.0
        }

    mengen_by_guid = {m["guid"]: m for m in mengen_daten}
    ergebnisse = []
    uebersprungen_ohne_menge = 0
    uebersprungen_ohne_material = 0

    for mat in material_daten:
        guid = mat["guid"]
        menge = mengen_by_guid.get(guid)

        if menge is None:
            uebersprungen_ohne_menge += 1
            logger.warning(f"{guid}: No quantity data found -- skip")
            continue

        # GWP-Faktor und passende Einheit aus dem Lookup ermitteln
        gwp_summe = 0.0
        api_einheit = "m3"
        matchbar = False
        erfolgreicher_begriff = None

        for begriff in mat.get("oekobaudat_suchbegriffe", []):
            eintrag = gwp_lookup.get(begriff)
            if eintrag is not None:
                # Prüfen, ob der Lookup ein Tupel (faktor, einheit) oder nur ein Wert ist
                if isinstance(eintrag, (tuple, list)):
                    faktor, einheit_str = eintrag
                    api_einheit = str(einheit_str)
                else:
                    faktor = float(eintrag)
                    
                gwp_summe += faktor
                matchbar = True
                erfolgreicher_begriff = begriff
                break

        if not matchbar:
            uebersprungen_ohne_material += 1
            logger.warning(f"{guid} (Material: {mat.get('name')}): no matchable material found -- skip")
            continue

        # Rohdaten aus den Mengen extrahieren
        gewicht = menge.get("weight") or menge.get("mass")
        volumen = menge.get("volume")

        api_einheit_lower = api_einheit.lower()

        # Dynamische Berechnung je nach API-Bezugseinheit
        if "kg" in api_einheit_lower:
            # Fall A: Ökobaudat bezieht sich auf 1 kg
            if gewicht is not None:
                bezugs_menge = gewicht
            elif volumen is not None:
                dichte = 2400.0  # Fallback
                mat_text = f"{mat.get('name', '')} {erfolgreicher_begriff}".lower()
                for key, val in dichte_lookup.items():
                    if key in mat_text:
                        dichte = val
                        break
                bezugs_menge = volumen * dichte
            else:
                bezugs_menge = 0.0
            einheit = "kg"
        else:
            # Fall B: Ökobaudat bezieht sich standardmäßig auf m³
            if volumen is not None:
                bezugs_menge = volumen
            elif gewicht is not None:
                dichte = 2400.0  # Fallback
                mat_text = f"{mat.get('name', '')} {erfolgreicher_begriff}".lower()
                for key, val in dichte_lookup.items():
                    if key in mat_text:
                        dichte = val
                        break
                bezugs_menge = gewicht / dichte
            else:
                bezugs_menge = 0.0
            einheit = "m3"

        co2_kg = bezugs_menge * gwp_summe

        ergebnisse.append({
            "guid": guid,
            "ifc_type": mat.get("ifc_type"),
            "name": mat.get("name"),
            "menge_wert": round(bezugs_menge, 2),
            "einheit": einheit,
            "gwp_faktor": round(gwp_summe, 4),
            "co2_kg": round(co2_kg, 2),
            "volumen": round(volumen, 4) if volumen is not None else None
        })

    logger.info(
        f"{len(ergebnisse)}/{len(material_daten)} element calculation successful "
        f"({uebersprungen_ohne_menge} without quantity, {uebersprungen_ohne_material} without material)"
    )
    return ergebnisse

if __name__ == "__main__":
    from Engine.ifc_loader import load_ifc_file
    from Engine.mass_extraktor import mass_extractor
    from Engine.material_extraktor import material_extractor
    import Engine.co2_api
    from Engine.co2_berechnung import berechne_co2
    
    # 1. Echtes IFC-Modell laden
    model = load_ifc_file("AC-20-Smiley-West-10-Bldg.ifc")
    
    # Bauteile filtern
    element_types = [
         "IfcWall", "IfcSlab", "IfcColumn", "IfcBeam",
         "IfcRoof", "IfcFooting", "IfcPile", "IfcDoor", "IfcWindow"
    ]
    elements = [e for t in element_types for e in model.by_type(t)]
    
    # 2. Daten extrahieren
    mengen_daten = mass_extractor(elements)
    material_daten = material_extractor(model, elements)
    
    # 3. GWP-Lookup vollautomatisch über deine Ökobaudat-API füllen
    print("Frage GWP-Faktoren live von der Ökobaudat-API ab...")
    gwp_lookup = {}
    
    alle_begriffe = set()
    for mat in material_daten:
        for begriff in mat.get("oekobaudat_suchbegriffe", []):
            alle_begriffe.add(begriff)
        
    for begriff in alle_begriffe:
        print(f"Suche in Ökobaudat: '{begriff}'...")
        faktor = Engine.co2_api.suche_gwp_faktor(begriff, sprache="de")
        
        # Falls Deutsch kein Ergebnis liefert, probieren wir es optional auf Englisch
        if faktor is None:
            faktor = Engine.co2_api.suche_gwp_faktor(begriff, sprache="en")
        
        if faktor is not None:
            gwp_lookup[begriff] = faktor
            print(f" -> Gefunden! GWP-Faktor: {faktor}")
        else:
            print(f" -> Kein Treffer für '{begriff}'.")

        dichte_lookup = {
            "beton": 2400.0,
            "holz": 650.0,
            "glas": 2500.0,
            "timber": 650.0,
            "steel": 7850.0
        }
    
    # 4. Zusammenführen und berechnen
    ergebnisse = berechne_co2(material_daten, mengen_daten, gwp_lookup, dichte_lookup)
    
    print(f"\n--- ERGEBNISSE ({len(ergebnisse)} Elemente erfolgreich berechnet) ---")
    for ergebnis in ergebnisse[:10]:
        print(ergebnis)