#include <kamek.h>
#include <types.h>

kmBranchDefAsm(0x80a9afe0, 0x80a9afe4)
{
    // loads address into r12
    lis r12, 0x80BB
    ori r12, r12, 0xB004

    // load value to write into r11
    lis r11, 0x0000
    li r11, 0x0001

    //write value at r11
    stw r11, 0(r12)

    blr
}

// extra blr out of function
//kmWriteDefAsm(0x80a9afe4) {blr}
kmWrite32(0x80a9afe4, 0x4e800020);
