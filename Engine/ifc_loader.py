from pathlib import Path

import ifcopenshell

from Engine.logger import logger



BASE_PATH = Path(__file__).resolve().parent.parent

def load_ifc_file(file_name):
    #Load the IFC file using ifcopenshell
    ifc_path = BASE_PATH / "ifc" / file_name

    try:
        ifc_model = ifcopenshell.open(str(ifc_path))
        logger.info(f"IFC-Data :{ifc_path.name} --> successfully uploaded")
        return ifc_model
    
    except Exception as e:
        logger.warning(f"IFC-Data uploadmissed: {e}")
        return None

if __name__ == "__main__":
    model = load_ifc_file("1807_EP_AR_v18.ifc")

        
        
