import os
import struct
import zipfile
from typing import Optional, List

from ppc_asm.assembler.ppc import *

#from NSMBW_client.NSMBWInterface import GAMES, HUD_MESSAGE_DURATION
from worlds.Files import APPlayerContainer

def patch_iso(input, output):
    print("TODO implement patcher")

class NSMBWContainer(APPlayerContainer):
    game: str = "NSMBW"  # type: ignore

    def __init__(self,config_json: str,options_json: str,outfile_name: str,
                 output_directory: str,player: Optional[int] = None,player_name: str = "",server: str = "",):
        self.config_json = config_json
        self.config_path = "config.json"
        self.options_path = "options.json"
        self.options_json = options_json
        container_path = os.path.join(output_directory, outfile_name + ".apnsmbw")
        super().__init__(container_path, player, player_name, server)
    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        opened_zipfile.writestr(self.config_path, self.config_json)
        opened_zipfile.writestr(self.options_path, self.options_json)
        super().write_contents(opened_zipfile)


def construct_hook_patch(game_version: str, progressive_beams: bool) -> List[int]:
    from ppc_asm import assembler

    #symbols = py_randomprime.symbols_for_version(game_version)
    symbols = {}

    # UpdateHintState is 0x1BC in length, 111 instructions
    num_preserved_registers = 2
    num_required_instructions = 111
    instruction_size = 4
    block_size = 32
    patch_stack_length = 0x30 + (num_preserved_registers * instruction_size)
    instructions: List = [
        stwu(r1, -(patch_stack_length - instruction_size), r1),
        mfspr(r0, LR),
        stw(r0, patch_stack_length, r1),
        stmw(
            GeneralRegister(block_size - num_preserved_registers),
            patch_stack_length
            - instruction_size
            - num_preserved_registers * instruction_size,
            r1,
        ),
        or_(r31, r3, r3),
        # Check if trigger is set
        lis(
            r6, GAMES[game_version]["HUD_TRIGGER_ADDRESS"] >> 16
        ),  # Load upper 16 bits of address
        ori(
            r6, r6, GAMES[game_version]["HUD_TRIGGER_ADDRESS"] & 0xFFFF
        ),  # Load lower 16 bits of address
        lbz(r5, 0, r6),
        cmpwi(r5, 1),
        bne("early_return_hud"),
        # If trigger is set then reset it to 0
        li(r5, 0),
        stb(r5, 0, r6),
        # Prep function arguments
        lis(
            r5, struct.unpack("<I", struct.pack("<f", HUD_MESSAGE_DURATION))[0] >> 16
        ),  # Float duration to show message
        li(r6, 0x0),
        li(r7, 0x1),
        li(r9, 0x9),
        stw(r5, 0x10, r1),
        stb(r7, 0x14, r1),
        stb(r6, 0x15, r1),
        stb(r6, 0x16, r1),
        stb(r7, 0x17, r1),
        stw(r9, 0x18, r1),
        addi(r3, r1, 0x1C),
        lis(
            r4, GAMES[game_version]["HUD_MESSAGE_ADDRESS"] >> 16
        ),  # Load upper 16 bits of message address
        ori(
            r4, r4, GAMES[game_version]["HUD_MESSAGE_ADDRESS"] & 0xFFFF
        ),  # Load lower 16 bits of message address
        bl(symbols["wstring_l__4rstlFPCw"]),
        addi(r4, r1, 0x10),
        # Call function
        bl(symbols["DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo"]),
        nop().with_label("early_return_hud"),
        # Progressive Beam Patch
        #*construct_progressive_beam_patch(game_version, progressive_beams),
        # Early return
        lmw(
            GeneralRegister(block_size - num_preserved_registers),
            patch_stack_length
            - instruction_size
            - num_preserved_registers * instruction_size,
            r1,
        ).with_label("early_return_beam"),
        lwz(r0, patch_stack_length, r1),
        mtspr(LR, r0),
        addi(r1, r1, patch_stack_length - instruction_size),
        blr(),
    ]

    # Fill remaining instructions with nops
    while len(instructions) < num_required_instructions:
        instructions.append(nop())

    if len(instructions) > num_required_instructions:
        raise Exception(
            f"Patch function is too long: {len(instructions)}/{num_required_instructions}"
        )

    return list(
        assembler.assemble_instructions(
            symbols["UpdateHintState__13CStateManagerFf"], instructions, symbols=symbols
        )
    )


class Patcher(object):
    @staticmethod
    def patch_iso(input_iso_path, output_path):
        print("TODO: implement patcher")
        #what do we need to patch into the gamefiles?
