from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

SOURCES = {
    "isic5.csv": "https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/ISIC_Rev_5_english_structure.csv",
    "cpc3.csv": "https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/CPC_Ver_3.0_Structure_30Jun2025.csv",
    "coicop2018.xlsx": "https://unstats.un.org/unsd/classifications/Econ/Download/COICOP_2018_English_structure.xlsx",
    "hs2022.json": "https://comtradeapi.un.org/files/v1/app/reference/H6.json",
    "sitc4.json": "https://comtradeapi.un.org/files/v1/app/reference/S4.json",
    "bec5.json": "https://comtradeapi.un.org/files/v1/app/reference/B5.json",
    "isic4to5.xlsx": "https://unstats.un.org/unsd/classifications/Econ/tables/ISIC/ISIC_Rev4_to_ISIC_Rev5_Correspondence_Table-17Jan2025.xlsx",
    "m49.csv": "https://unstats.un.org/unsd/methodology/m49/overview/",
    # Transparent fallback: ILO's structured download was unavailable during the v0.1 build.
    # This complete code/title list is validated by count and spot checks against the ILO manual.
    "isco08.txt": "https://gist.githubusercontent.com/iamarsenibragimov/39b5186a782ee66cca9fb72bf535c655/raw/0c4fd0934dcd9da04fd93a89730d8e5af7634528/ISCO-08%20(International%20Standard%20Classification%20of%20Occupations)%20-%20Complete%20Classification",
}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for filename, url in SOURCES.items():
        print(f"Fetching {filename} from {url}")
        request = urllib.request.Request(
            url, headers={"User-Agent": "ImpactEngines-Classifications-MCP/0.1"}
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            (RAW / filename).write_bytes(response.read())


if __name__ == "__main__":
    main()
