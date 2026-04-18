-- use this file to map the AP location ids to your locations
-- first value is the code of the target location/item and the second is the item type override (feel free to expand the table with any other values you might need (i.e. special initial values, increments, etc.)!)
-- to reference a location in Pop use @ in the beginning and then path to the section (more info: https://github.com/black-sliver/PopTracker/blob/master/doc/PACKS.md#locations)
-- to reference an item use it's code
-- here are the SM locations as an example: https://github.com/Cyb3RGER/sm_ap_tracker/blob/main/scripts/autotracking/location_mapping.lua
BASE_LOCATION_ID = 0
LOCATION_MAPPING = {
	[BASE_LOCATION_ID + 00001] = { { "@Example Parent/Example Location 1/Example Section 1" } },
	[BASE_LOCATION_ID + 00002] = { { "toggle" } },
	-- multiple locations on this id
	[BASE_LOCATION_ID + 00003] = { { "@Example Parent/Example Location 1/Example Section 1" }, { "@Example Parent/Example Location 1/Example Section 2" } },
}
