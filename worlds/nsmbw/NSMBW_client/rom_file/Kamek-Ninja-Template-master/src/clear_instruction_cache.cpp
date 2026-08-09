#include <kamek.h>
#include <kamek_sdk.h>

// find end of function to hook onto
kmBranchDefAsm(0x00, 0)
void WriteInstructionClearCache(void)
{
    // - Hook up kamek patch that can clear jit: load instru from memory: # r17+r18=address of instruction you want to remove from cache dcbf r17,r18  sync icbi r17,r18 isync

    // load address to write and value to write
    register int *p_reg_address asm ("r17");
    int volatile * const p_reg_address = (int *) 0x8000000; // deside on register
    int volatile * const p_reg_value = (int *) 0x8000004;

    // write value to adress
    *p_reg_address = *p_reg_value;

    // load address into r17 + r18
    li r18, 0


    // flush instruction cache for value
    dcbf r17,r18
    sync
    icbi r17,r18
    isync

}

