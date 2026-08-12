from wiithon.disc.patcher import WiiIsoPatcher
from wiithon.formats.bcsv import BCSV, calculate_field_hash

ISO_PATH = "../assets/smg.iso"
OUTPUT_PATH = "../assets/smg_patch.iso"

BCSV_PATH = "StageData/CannonFleetGalaxy/CannonFleetGalaxyScenario.arc/scenariodata.bcsv"

FIELD_NAMES = {
    calculate_field_hash("ScenarioNo"):             "ScenarioNo",
    calculate_field_hash("ScenarioName"):           "ScenarioName",
    calculate_field_hash("PowerStarId"):            "PowerStarId",
    calculate_field_hash("AppearancePowerStarObj"): "AppearancePowerStarObj",
    calculate_field_hash("Comet"):                  "Comet",
    calculate_field_hash("LuigiModeTimer"):         "LuigiModeTimer",
}


def display_bcsv(bcsv: BCSV) -> None:
    print(f"Fields ({len(bcsv.fields)}) :")
    for field in bcsv.fields:
        print(f"  [{field.field_hash:#010x}] {field.field_name} ({field.field_type.name})")

    print(f"\nEntries ({len(bcsv.entries)}) :")
    for i, entry in enumerate(bcsv.entries):
        print(f"  Entry {i} :")
        for key, value in entry.items():
            print(f"    {key} = {value!r}")


if __name__ == "__main__":
    with WiiIsoPatcher(ISO_PATH) as patcher:
        with patcher.edit_as(BCSV_PATH, BCSV, field_names=FIELD_NAMES, str_fmt="shift_jis") as bcsv:
            print("=== BEFORE ===")
            display_bcsv(bcsv)

            for entry in bcsv.entries:
                entry["LuigiModeTimer"] = 0

            print("\n=== AFTER ===")
            display_bcsv(bcsv)

        # patcher.build(OUTPUT_PATH)
        # print(f"\nPatched : {OUTPUT_PATH}")
