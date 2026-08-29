import json
import requests
from logger import logger

OEKOBAUDAT_BASE_URL = "https://www.oekobaudat.de/OEKOBAU.DAT/resource"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def suche_gwp_faktor(suchbegriff: str, sprache: str = "de") -> float | None:
    if not suchbegriff:
        return None

    try:
        search_url = f"{OEKOBAUDAT_BASE_URL}/processes"
        params = {
            "search": "true",
            "name": suchbegriff,
            "lang": sprache,
            "format": "json",
        }

        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        daten = response.json()

        results = daten.get("data")
        if not results:
            logger.warning(f"No match found for '{suchbegriff}'")
            return None

        uuid = results[0].get("uuid")
        if not uuid:
            return None

        detail_url = f"{OEKOBAUDAT_BASE_URL}/processes/{uuid}"
        detail_res = requests.get(detail_url, params={"format": "json"}, headers=headers, timeout=10)
        detail_res.raise_for_status()
        detail_data = detail_res.json()

        lcia_results = detail_data.get("LCIAResults", {}).get("LCIAResult", [])

        if isinstance(lcia_results, dict):
            lcia_results = [lcia_results]

        gwp_werte = {}

        for result in lcia_results:
            result_str = str(result).lower()
            if any(k in result_str for k in ["gwp", "global warming", "erwärmungspotenzial"]):
                anies = result.get("other", {}).get("anies", [])

                if isinstance(anies, list):
                    for entry in anies:
                        if isinstance(entry, dict) and "module" in entry and "value" in entry:
                            modul = str(entry["module"])
                            try:
                                gwp_werte[modul] = float(entry["value"])
                            except (ValueError, TypeError):
                                gwp_werte[modul] = entry["value"]

                elif isinstance(anies, dict):
                    for modul, wert in anies.items():
                        try:
                            gwp_werte[str(modul)] = float(wert)
                        except (ValueError, TypeError):
                            gwp_werte[str(modul)] = wert

                if not gwp_werte and "meanValue" in result:
                    try:
                        gwp_werte["total"] = float(result["meanValue"])
                    except (ValueError, TypeError):
                        pass

                if gwp_werte:
                    break

        if not gwp_werte:
            return None

        # Berechnet die Summe direkt in der Funktion und gibt sie als Float zurück
        lebenszyklus_module = {
            k: v for k,v in gwp_werte.items()
            if k != "D" and isinstance(v, (int, float))
        }
        gesamter_gwp = sum(lebenszyklus_module.values())

        modul_d_wert = gwp_werte.get("D")
        if modul_d_wert is not None:
            logger.info(f"Modul D nicht im gesamtwert enthalten: {modul_d_wert}")

        return gesamter_gwp

    except Exception as e:
        logger.error(f"API Failure with '{suchbegriff}': {e}")
        return None

if __name__ == "__main__":
    ergebnis = suche_gwp_faktor("Beton", sprache="de")
    print("Gesamter GWP-Wert:", ergebnis, flush=True)