#include <kamek.h>


//ends up loaded into 0x80D26040

// hooks onto end of bar draw function
kmBranchDefAsm(0x800B0B40, 0x800B0B44)
{
    // load address into r11, clears r12
    lis r12, 0x80BB
    ori r12, r12, 0xB000


    // load address that is in memory 0x80BBB000
    lwz r11, 0(r12)

    // if r11 is 0 should branch to blr
    cmpwi r11, 0          // check if r11 is 0
    bc 12, 2, skipp           // Return if parameter is 0


    // empty memory at 0x80BBB000
    lis r10, 0x0000
    stw r10, 0(r12)

    // empty r12
    lis r12, 0x0000

    // flush instruction cache for value
    dcbf r11,r12
    sync
    icbi r11,r12
    isync

    // branch back
    skipp:
        blr
}

// moves the blr instruction one adress lower
//kmWriteDefAsm(0x800B0B44){blr}
kmWrite32(0x800B0B44, 0x4e800020);
