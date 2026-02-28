from typing import Dict, Any

GAMES: Dict[str, Any] = {
    "US": {
        "game_id": b"SMNE01",
        "game_rev": 2,
        "SC_current_level" : 0x803741B0,
        "SC_stockage": 0x815E3AA7, # (systeme byte 000) for each level (815E3A*7)",
        "level_world": 0x80315B9F, #"Level world when you are in a level", #change beacuse think wrong
        "level_stat": 0x80C8084F, #. Ex: first byte (00 == level not completed, 10 == level completed, 20 == secret exit) second byte (01 == first star coin collected, 02 == second star coin collected, 03 == first and second stars coins collected) +4 for the others levels
        "inventory_items": 0x80C807D9, #(+1 byte for each)
        "world_level": 0x80315B9C, #(World Map)
        "level_level": 0x80315B9D, #(World Map)
        "HM_stats": 0x80C80EDC, #. Ex: 0 == not available, 1 == unlocked. +1 for each hint movie (80C80ED*) #modified, another gameversion?
        "Worldstats_selectmenu": 0x80C80812, #. Ex: 0 == not available, 1== unlocked. +1 for each world (80C8081*)


        #"powerup_state1" : 0x8154C897, #dont need 1
        "powerup_state2" : 0x8154CCE7, #not shure what diffens betwen these are

        "player_status" : 0x8154CC5C, # =0 if in level, 1 if dead, 2 if menu
        #acording to gemini player_status - 0x1148 = marios base address, should try to find static pointer to this dynamic location

        # need to find
        "red_switch": 0x0000000,


        "HUD_MESSAGE_ADDRESS": 0x803F0BA8,#copypasted these from metroid
        "HUD_TRIGGER_ADDRESS": 0x80573494,



    },"EU": {
        "game_id": b"SMNP01" # EU partially supported
    }
}
