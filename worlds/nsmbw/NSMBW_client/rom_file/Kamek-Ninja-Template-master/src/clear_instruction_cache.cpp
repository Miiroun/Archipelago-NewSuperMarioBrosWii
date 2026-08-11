#include <kamek.h>


//ends up loaded into 0x80D26040

// hooks onto end of bar draw function
kmBranchDefAsm(0x800B0B40, 0x800B0B44)
{
    // load address into r17, clears r18
    lis r18, 0x80BB
    ori r18, r18, 0xB000

    lwz r17, 0(r18) // this is the problematic line, originally lbz

    lis r18, 0x0000


    // flush instruction cache for value
    dcbf r17,r18
    sync
    icbi r17,r18
    isync

    // branch back
    blr
}

// moves the blr instruction one adress lower
kmWrite32(0x800B0B44, 0x4e800020);
