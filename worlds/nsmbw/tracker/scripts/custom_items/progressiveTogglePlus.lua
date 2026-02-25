ProgressiveTogglePlus = class(CustomItemProgressiveTogglePlus)

--[[
    states : table
    {
        [state : integer] = --0-based index
        {
            image : string --path to the image
            codes : string --codes for the state
            disabled : boolean --disabled
        }
        ...
    }
    -- states for the progression

    loop : boolean
    -- loop through progression states

    disableToggle : boolean
    -- disables the toggle part of the item (right click will decrease the progression state instead; if disableProgessive is enabled as well the item will act as a static)

    disableProgessive : boolean
    -- disables the progression part of the item (left and right click will toggle instead; if disableToggle is enabled as well the item will act as a static)

    initialStage : integer
    -- initial progression state

    initialActive : boolean
    -- initial active state

    toggleChildren : list LuaItem
    -- also toggles these Items when this item is toggled and enableChildToggle is true (only via :setActive)

    enableChildToggle : boolean
    -- enables toggling toggleChildren (only via :setActive)

    progressionChildren : table
    {
        children : list LuaItem with a continuous, numeric index
        states : table
        {
            [parent_state] = {
                [child_index] = child_state
                ...
            }
            ...
        }
    }
    -- set the progression of the progressionChildren.children to the state defined in progressionChildren.states
        when this item is progressed to a state equal to a index in progressionChildren.state and enableChildToggle is true (only via :setState)

    enableChildProgression
    -- enables progression of progressionChildren (only via :setState)
]]

function ProgressiveTogglePlus:init(name, code, states, loop, disableToggle, disableProgessive, initialStage, initialActive, toggleChildren, enableChildToggle,
    progressionChildren, enableChildProgression)

    self:createItem(name)
    self.code = code
    self.active = false
    self.states = states
    self.state = 1
    self.loop = loop
    self.disableToggle = disableToggle
    self.disableProgessive = disableProgessive
    self.toggleChildren = toggleChildren
    self.enableChildToggle = enableChildToggle
    self.progressionChildren = progressionChildren
    self.enableChildProgression = enableChildProgression

    self:getImages()
    self:setState(initialStage)
    self:setActive(initialActive)
    self.ItemInstance.PotentialIcon = self.images[initialStage]
end

function ProgressiveTogglePlus:getImages()
    self.images = {}
    for i = 0, #self.states do
        self.images[i] = ImageReference:FromPackRelativePath(self.states[i].image)
    end
end

function ProgressiveTogglePlus:getState()
    return self.state
end

function ProgressiveTogglePlus:setState(state)
    self:propertyChanged("state",state)
    if self.enableChildProgression then
        if self.progressionChildren.states[state] then
            for k,v in pairs(self.progressionChildren.states[state]) do
                if self.progressionChildren.children[k] then
                    self.progressionChildren.children[k]:setState(v)
                end
            end
        end
    end
end

function ProgressiveTogglePlus:advanceState()
    local start = self.state
    local target = start
    repeat
        if target == #self.states then
            if self.loop then
                target = 0
            end
        else
            target = self.state + 1
        end
    until start == target or not self.states[target].disabled
    if target then
        self:setState(target)
    end
end

function ProgressiveTogglePlus:decreaseState()
    local start = self.state
    local target = start
    repeat
        if target == 0 then
            if self.loop then
                target = #self.states
            end
        else
            target = self.state - 1
        end
    until start == target or not self.states[target].disabled
    if target then
        self:setState(target)
    end
end

function ProgressiveTogglePlus:setActive(active)
    self:setProperty("active",active)
    if self.enableChildToggle then
        for _,v in pairs(self.toggleChildren) do
            v:setActive(active)
        end
    end
end

function ProgressiveTogglePlus:getActive()
    return self.active
end

function ProgressiveTogglePlus:updateIcon()
    self.ItemInstance.Icon = self.images[self.state]
    if PopVersion and PopVersion > "0.1.0" then
        if self.active then   
            self.ItemInstance.IconMods = ""
        else
            self.ItemInstance.IconMods = "@disabled"
        end
    end
end

function ProgressiveTogglePlus:onLeftClick()
    if self.disableToggle and self.disableProgessive then return end
    if self.disableProgessive then
        self:setActive(not self.active)
    else
        self:advanceState()
    end
end

function ProgressiveTogglePlus:onRightClick()
    if self.disableToggle and self.disableProgessive then return end
    if self.disableToggle then
        self:decreaseState()
    else
        self:setActive(not self.active)
    end
end

function ProgressiveTogglePlus:canProvideCode(code)
    if code == self.code then
        return true
    else
        for i = 0, #self.states do
            for code2 in string.gmatch(self.states[i].codes, "[^,]+") do
                if code == code2 then
                    return true
                end
            end
        end
        return false
    end
end

function ProgressiveTogglePlus:providesCode(code)
    if code == self.code then
        return self.state
    end
    for i = 0, #self.states do
        for code2 in string.gmatch(self.states[i].codes, "[^,]+") do
            if code == code2 then
                return self.state
            end
        end
    end
    return 0
end

function ProgressiveTogglePlus:advanceToCode(code)
end

function ProgressiveTogglePlus:save()
    local saveData = {}
    saveData["state"] = self:getState()
    saveData["active"] = self.active
    saveData["disableToggle"] = self.disableToggle
    saveData["disableProgessive"] = self.disableProgessive
    return saveData
end

function ProgressiveTogglePlus:load(data)
    if data["state"] ~= nil then
        self:setProperty("state",data["state"])
    end
    if data["active"] ~= nil then
        self:setProperty("active",data["active"])
    end
    if data["disableToggle"] ~= nil then
        self:setProperty("disableToggle",data["disableToggle"])
    end
    if data["disableProgessive"] ~= nil then
        self:setProperty("disableProgessive",data["disableProgessive"])
    end
    return true
end

function ProgressiveTogglePlus:propertyChanged(key, value)
    print(string.format("ProgressiveTogglePlus:propertyChanged key %s with value %s",key,value))
    if key == "state" then
        self.state = value
    end
    if key == "active" then
        self.active = value
    end
    if key == "disableToggle" then
        self.disableToggle = value
    end
    if key == "disableProgessive" then
        self.disableProgessive = value
    end
    if key == "enableChildToggle" then
        self.enableChildToggle = value
    end
    if key == "enableChildProgression" then
        self.enableChildProgression = value
    end
    if key == "state" or key == "active" then
        self:updateIcon()
    end
end
