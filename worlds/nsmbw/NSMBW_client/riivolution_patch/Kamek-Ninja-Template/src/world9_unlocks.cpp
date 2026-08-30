#include <kamek.h>
#include <types.h>
#include <game/bases/d_wm_lib.hpp>


// it happens at 0x808CE56C, the game checks if its world 9, then calls setSpecialWorldAnm() (0x808CED00)
// dWmLib::isSpecialWorldCourseOpen() just calls dWmLib::isRemainderCollectionCoin(), which returns if the collected number of star coins (for that world) is greater than or equal to the max number of coins

extern u8 isSpecialWorldCourseOpen(u8 courseIdx);
extern void FUN_808ce8e0(int param_1, int param_2, f32 param_3, f32 param_4);

// how to edit to easily change with dme?
kmBranchDefCpp(0x808ce57c, 0x808ce5b0, void, int param_1)
{
    bool bVar1;
    u8 courseIdx;

    courseIdx = *(u8 *)(param_1 + 4) & 0xff;
    if ((courseIdx < 10) && (bVar1 = isSpecialWorldCourseOpen(courseIdx), !bVar1)) {
        FUN_808ce8e0(param_1, 0, 0.0, 0.0);
    }
    return;
}


/*
// maybe easier to just consider it in asm

kmBranchDefAsm(0x808ced00, 0x808ce5b0)
{
stwu       r1, 4(r1)
mfspr      r0,LR
stw        r0, 4 (r1)
stw        r31, 4 (r1)
or         r31,r3,r3
lwz        r0,0x4(r3)
rlwinm     r3,r0,0x0,0x18,0x1f
cmplwi     r3,0x9
bgt        LAB_808ced48
bl         j_GetStarCoinsRemainingInWorld
cmpwi      r3,0x0
bne        LAB_808ced48
lis        r4,-0x7f6c
or         r3,r31,r31
lfs        f1,-0x3bb0(r4)
li         r4,0x0
fmr        f2,f1
bl         FUN_808ce8e0
LAB_808ced48:
    lwz        r0, 4(r1)
    lwz        r31, 4(r1)
    mtspr      LR,r0
    addi       r1,r1,0x10
    blr
}
*/

// maybe just have to settle for single mem override, for now

// do I still need the function to make the call, thats problematic
// might be easier to replace it fully?

/* Original function
void daWmCourse_c::setSpecialWorldAnm(daWmCourse_c *param_1)
{
    bool bVar1;
    uint courseIdx;

    courseIdx = (param_1->_)._.m_param & 0xff
    if ((courseIdx < 10) && (bVar1 = dWmLib::isSpecialWorldCourseOpen(int)(courseIdx), !bVar1)) {
        daWmCourse_c::setAnm(param_1, 0, 0.0, 0.0);
    }
    return;
}
*/