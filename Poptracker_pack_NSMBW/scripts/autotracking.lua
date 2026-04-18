-- Configuration --------------------------------------
AUTOTRACKER_ENABLE_ITEM_TRACKING = true
AUTOTRACKER_ENABLE_LOCATION_TRACKING = true and not IS_ITEMS_ONLY
AUTOTRACKER_ENABLE_DEBUG_LOGGING = false and ENABLE_DEBUG_LOG
AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP = true and AUTOTRACKER_ENABLE_DEBUG_LOGGING
AUTOTRACKER_ENABLE_DEBUG_LOGGING_SNES = true and AUTOTRACKER_ENABLE_DEBUG_LOGGING
-------------------------------------------------------
print("")
print("Active Auto-Tracker Configuration")
print("---------------------------------------------------------------------")
print("Enable Item Tracking:        ", AUTOTRACKER_ENABLE_ITEM_TRACKING)
print("Enable Location Tracking:    ", AUTOTRACKER_ENABLE_LOCATION_TRACKING)
if AUTOTRACKER_ENABLE_DEBUG_LOGGING then
    print("Enable Debug Logging:        ", AUTOTRACKER_ENABLE_DEBUG_LOGGING)
    print("Enable AP Debug Logging:        ", AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP)
    print("Enable SNES Debug Logging:        ", AUTOTRACKER_ENABLE_DEBUG_LOGGING_SNES)
end
print("---------------------------------------------------------------------")
print("")

-- uncomment this to use `Tracker.AllowDeferredLogicUpdate` to defer logic updates, which might be needed if you touch A LOT of items/locations at once.
-- if Tracker.AllowDeferredLogicUpdate == false then Tracker.AllowDeferredLogicUpdate = true end

-- loads the AP autotracking code
ScriptHost:LoadScript("scripts/autotracking/archipelago.lua")
-- loads the SNES autotracking code
ScriptHost:LoadScript("scripts/autotracking/snes.lua")

