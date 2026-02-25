-- this is an example file for SNES memory autotracking 
-- more info: https://github.com/black-sliver/PopTracker/blob/master/doc/AUTOTRACKING.md#memory-interface-usb2snes
EXAMPLE_ADDR = 0x7E07F7
EXAMPLE_SIZE = 0x8

function update_example(segment)
    if not AUTOTRACKER_ENABLE_ITEM_TRACKING then
        return
    end
    local readResult = segment:ReadUInt8(EXAMPLE_ADDR) -- preferred way of reading
    local readResult2 = AutoTracker:ReadU16(EXAMPLE_ADDR + 0x1) -- alternative way of reading  
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_SNES then
        print(string.format("update_example: readResult: %x, readResult2: %x", readResult, readResult2))
    end
    -- changing example item
    local obj = Tracker:FindObjectForCode("toggle")
    if obj then
        obj.Active = readResult2 > readResult
    end
    -- changing example section
    local loc = Tracker:FindObjectForCode("@Example Parent/Example Location 1/Example Section 1")
    if loc and readResult2 > readResult then
        loc.AvailableChestCount = loc.AvailableChestCount - 1
    end
end

if AUTOTRACKER_ENABLE_ITEM_TRACKING then
    ScriptHost:AddMemoryWatch('example', EXAMPLE_ADDR, EXAMPLE_SIZE, update_example)
end
