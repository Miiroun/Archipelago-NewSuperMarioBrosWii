#include <kamek.h>


//ends up loaded into 0x80D26040

// hooks onto end of bar draw function
kmBranchDefAsm(0x800B0B40, 0x800B0B44)
{
    // load address into r17, clears r18
    lis r18, 0x80BB
    ori r18, r18, 0xB000


    // load address that is in memory 0x80BBB000
    lwz r17, 0(r18)

    // if r17 is 0 should branch to blr
    cmpwi r17, 0          // check if r17 is 0
    bc 12, 2, skipp           // Return if parameter is 0


    // empty memory at 0x80BBB000
    lis r16, 0x0000
    stw r16, 0(r18)

    // empty r18
    lis r18, 0x0000

    // flush instruction cache for value
    dcbf r17,r18
    sync
    icbi r17,r18
    isync

    // branch back
    skipp:
        blr
}

// moves the blr instruction one adress lower
kmWrite32(0x800B0B44, 0x4e800020);
