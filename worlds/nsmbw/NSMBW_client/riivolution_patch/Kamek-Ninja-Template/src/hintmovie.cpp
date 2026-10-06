#include <kamek.h>
#include <kamek_sdk.h>


kmBranchDefCpp(0x80792f50, 0x80792fe8, void, volatile u8 param_1)
{
    volatile u8 amount = *(volatile u8*)0x80BBB028u; // this is c code that should read the memory

    *(u8 *)(param_1 + 0x288) = amount;
    return;
}

/*
extern __restore_gpr26

kmBranchDefAsm(0x80792f50, 0x80792fe8)
{
    lis r12, 0x80BB
    ori r12, r12, 0xB000

    // load value to write into r11
    //lis r10, 0x0001
    //stw r10, 0(r12)

    //lwz r30, 24(r12)
    lis r26, 0
    li r26, 15

    stw        r30 ,0x288 (r26 )
    addi       r11 ,r1,0x20
    bl         __restore_gpr26
    lwz        r0,local_res4 (r1)
    mtspr      LR,r0
    addi       r1,r1,0x20


    blr
}
*/
