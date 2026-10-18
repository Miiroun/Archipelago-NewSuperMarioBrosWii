#include <kamek.h>
#include <game/bases/d_wm_lib.hpp>

//breakpoint 0x80c7fecf

// this makes level points red
/*
kmBranchDefCpp(0x800fa440, 0x800fa6e4, int, int param_1, int param_2)
{
    return 2;
}
*/


//extern "C" {
//extern bool IsCourseClear__6dWmLibFii(int world, int stage);
//extern int GetClearStatus__6dWmLibFii(int param_1, int param_2);
//}



//extern int GetClearStatus(int param_1, int param_2);


bool IsCourseOmoteClear(int param_1, int param_2)
{

  //int iVar1;
  //bool bVar2;

  int iVar1;
  bool bVar2;

  iVar1 = dWmLib::GetClearStatus(param_1, param_2);
  if ((iVar1 == 1) || (iVar1 == 2) || (iVar1 == 4)) {
    bVar2 = true;
  }
  else {
    bVar2 = false;
  }
  return bVar2;


  //return dWmLib::IsCourseOmoteClear(param_1,param_2);
  //asm {
  //}
  //return dWmLib::IsCourseClearSimple(param_1, param_2);
}



kmBranchDefCpp(0x800fae70, 0x800faeb0, bool, int param_1, int param_2)
{
    register int param_1_copy;
    register int param_2_copy;

    asm {
        mr param_1_copy, r3
        mr param_2_copy, r4
    }


    int world = param_1 & 0xffU+1;
    int level = param_2 & 0xffU+1;

    register int world_unlocked;
    register int level_unlock;
    register int bowser_unlock;


    asm {
        lis r12, 0x80BB
        ori r12, r12, 0xB000

        lwz r10, 44(r12)
        mr world_unlocked, r10
        lwz r10, 48(r12)
        mr level_unlock, r10
        lwz r10, 52(r12)
        mr bowser_unlock, r10

    }

    world_unlocked >> (world-1);
    world_unlocked = world_unlocked & 1;


    bool cleared = IsCourseOmoteClear(param_1_copy, param_2_copy); // default

    if (world == 8 and level == 38){
        // this code allows client to confirm bowser_unlock
        cleared =  bowser_unlock == 1;
    } else if ((level == 22) && (world_unlocked == 0)) {
        // this code dissables towers if not enabled second half
        cleared =  false;
    } else {
        if (level_unlock == 1) {
            //cleared = IsCourseOmoteClear(world, level);
        } else if (level_unlock == 3)  {
            cleared = true;
        } else {
            // panic
            cleared = true;
        }
    }

    return cleared;
}


// this fixes so paths are walkable
/*
kmBranchDefCpp(0x808df9f0,0x808dfe40,int, int param_1, int param_2, int param_3)
{
    return 1;
}
*/