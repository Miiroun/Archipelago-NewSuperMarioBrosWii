#include <kamek.h>
#include <types.h>

/*
internal name of generic background object dBg_ctr_c
they are stored in a double linked list with id : could possibly use as unique identifiers

internal name of ?-block = HATENA_BLOCK
name of brick block that gives pow EN_OBJ_RENGA_BLOCK

coins are independent? sprites called EN_COIN
- dBg_c::CoinGetBitCheck, helpful?

*/

/*
Implementation details?
Do we store conversion map in cpp or python land?
Easy update counter on hit
- hard to differentiate between instances
lots of data to be store for each level each coin separately
- coin ~ 150 * 80 = 12_000
- brick ~ 25 * 80 = 2_000
- ?-block ~ 10 * 80 = 800
might be nice to not load every level into memory all the time

will also need to write some script to collect all items into single list
how to create logic ? in subregions specify count and id range


- also problem that the normal block is not a class??
seems that every version of ?-block is implemented independently,
need to create a path for all versions
FUN_80036ab0 : checks for breaking of coin block : daEnObjCoinBlock_c
dBlockMgr_c : 80087f40
dBlockMgr_c::breakBlock?
dBlockMgr_c::getBlockTypeFromTilenum(?)
CreateItemByID : creates powerup ???
why does every type seem to have a unique class except for the base class??
- maybe base does not exist?
-> they might be coin block
-> powerup might have weird name
daBlockOneUp_c
maybe its
daEnObjBlock_c
daBlockTaru_c
I think from sprite profile that it should be daEnObjBlock_c
- this is the init function FUN_80a75b40
daEnObjBlock_c::create
=> powerup blocks are a part of daEnObjBlock_c with specific mProfName
daEnObjBlock_c::ProcessForNonHidden()
*/


// maybe better to patch in FUN_80022600 : but is specific to powerups
//path actually done a instru too early, but we dont have space to separate

// THIS works for the brick blocks including powerups but not the ?-blocks, (also crashes game) = 0x800226c0



// this triggers whenever a coin block is hit or a powerup block is hit, but not brick blocks
// but is not enough to increase brick block counter, want each item to be unique
// can do for normal brick blocks and normal free coins later
// have a list in the client, add to it hand have it print a big log green message in client
kmBranchDefAsm(0x80a26d48, 0x80a26d4c)
{

    // do address that we replaced
    stfs f3, 0xd4(r26)


    // loads address into r12
    lis r12, 0x80BB
    ori r12, r12, 0xB000

    // load value to write into r11
    /*
    lis r11, 0x0000
    li r11, 0x0001
    */

    // add 1 to r11
    /*
    lwz r11, 0(r12)
    addi r11, r11, 1
    */

    //write value at r11
    //stw r11, 0(r12)


    // we have a pointer in r3 and or r26?
    //mr r11, r3
    // create x, y, z
    // code is run directly after param is set, so uses their values
    //lfs f5, 0xc00(r3)
    stfs f7, 8(r12)

    //lfs f5, 0xc04(r3)
    stfs f6, 12(r12)

    //lfs f5, 0xc08(r3)
    stfs f5, 16(r12)


    blr
}
//kmWrite32(0x80a27428, 0x4e800020);


/*
WORKS!!
809bf980 - daEnBlock_c::spawnOneOf10Coins(void)
-> triggers when hit brick with many coins

- 80a26c30 daEnItem_c::create

*/