#pragma once
#include <game/bases/d_a_en_blockmain.hpp>
#include <game/bases/d_bg.hpp>
#include <game/bases/d_pswitch_manager.hpp>

class daEnBlockSwitch_c : public daEnBlockMain_c {
public:
    virtual int create();
    virtual int doDelete();
    virtual int execute();

    virtual void initialize_upmove();
    virtual void initialize_downmove();

    virtual void block_upmove();
    virtual void block_downmove();

    void blockWasHit(bool isDown);

    void createItem();

    STATE_FUNC_DECLARE(daEnBlockSwitch_c, Wait);
    STATE_FUNC_DECLARE(daEnBlockSwitch_c, HitWait);
    STATE_FUNC_DECLARE(daEnBlockSwitch_c, Dotted);

    dPanelObjList_c mTile;
    int mPalaceType;
    dPSwManager_c::SwType_e mSwitchType;
    bool mIsDotted;
    mVec3_c mInitialPos;
    bool mGiveCoin;
};

const u32 l_switchblock_item_values[5] = {
    0xF,				// Empty
    0xC,				// Mushroom
    0,					// Fire
    0x15,				// Propeller
    0xE					// Ice
};