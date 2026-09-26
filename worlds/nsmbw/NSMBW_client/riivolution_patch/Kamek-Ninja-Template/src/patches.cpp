#include <kamek.h>
#include <kamek_sdk.h>
#include "d_save_mng.hpp"
#include "d_info.hpp"


// Writes that riivolution is active to mem, to verify in client
kmWrite32(0x80BBB01C, 0xFFFFFFFF);


// Skip Wii Remote Strap Screen PAL by CLF78
//kmWrite32(0x803286C0, 0x8015D0A0);
//kmWrite32(0x803286CC, 0x8015D010);
//kmWrite32(0x803286D8, 0x8015CFC0);
// does not work

// - exception handler // Disable the button sequence
kmWrite32(0x802D7528, 0x48000060);


// from pipe rando

// Skip opening cutscene
kmWrite32(0x809191C4, 0x48000018);

// Skip title screen movies
kmWrite32(0x80781FB8, 0x60000000);
kmWrite32(0x80781FBC, 0x38600000);

// Always can save patches
kmWrite32(0x8077AA7C, 0x60000000); // message
kmWrite32(0x8092FD00, 0x38000002); // button behavior

extern bool IsWorldCollectionCoinComplete(int world);


// Don't hide Star Coins on Coin Battle stages
kmCallDefCpp(0x80157EB8, void, u8* layout)
{
    if (dInfo_c::m_startGameInfo.level2 == 19) {
        return;
    }

    layout[0xBB] &= ~1;
}

// Show Coin Battle stages properly on pause menu
extern u32 m_startGameInfo__7dInfo_c;

kmCallDefAsm(0x8015ACC4)
{
    // clang-format off
    nofralloc
    rlwinm. r0, r0, 0x0, 0x19, 0x19
    bne L_out

    lis r8, (m_startGameInfo__7dInfo_c + 0xF)@ha
    lbzu r5, (m_startGameInfo__7dInfo_c + 0xF)@l(r8)
    cmpwi r5, 19
    bne L_out

    ori r0, r0, 0x40
    lbz r4, -1(r8)

L_out:
    rlwinm. r0, r0, 0x0, 0x19, 0x19
    blr
    // clang-format on
}
