from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, TypedDict

from worlds.nsmbw.Common import *
# this file should populate the tracker location group

from worlds.nsmbw.world import NSMBWworld
import json

loc_group = NSMBWworld.location_name_groups
loc_name_id = NSMBWworld.location_name_to_id


class Section(TypedDict):
    name : str
    item_count : int

class MapLocation(TypedDict):
    map : str
    x : int
    y : int
    size : int

class Pin(TypedDict):
    name : str
    sections : List[Section]
    map_locations : List[MapLocation]



tracker_path = Path(__file__).parent.parent / "NSMBW_client" / "tracker"
partial_trackerfiles_path = Path(__file__).parent / "partial_tracker_files"


values : List[Pin] = json.load((partial_trackerfiles_path / "locations.json").open())




converted_values : List[Pin] = []
for i, pin in enumerate(values):
    groups : Iterable
    if pin["name"] in list([name_base(*level) for level in LEVELS]):
        groups = loc_group[pin["name"] + " Everything"]
    elif pin["name"] in loc_name_id.keys():
        groups = [pin["name"]]
    elif pin["name"] in loc_group.keys():
        groups = loc_group[pin["name"]]
    else:
        raise ValueError(f"{pin['name']} is not a valid location group name")
    sections: List[Section]= []

    for location_name in groups :
        sections.append(
            {
            "name": location_name,
            "item_count": 1
            }
        )

    fixed_pin : Pin = {
        "name"          : values[i]["name"],
        "sections"      : sections,
        "map_locations" : values[i]["map_locations"],
    }
    converted_values.append(fixed_pin)



json.dump(converted_values, (tracker_path / "locations" / "locations.json").open("w+"), indent=2)
print("Successfully built ")