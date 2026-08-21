#pragma once
#include <game/bases/d_a_en_blockmain.hpp>
#include <game/bases/d_bg.hpp>

// ON/OFF switch block

class daEnBlockFlag_c : public daEnBlockMain_c {
public:
    enum BLOCK_FLAG_MODE_e {
        TOGGLE_EVENT = 0,
        SWAP_EVENTS = 1
    };

    virtual int create();
    virtual int doDelete();
    virtual int execute();

    virtual void initialize_upmove();
    virtual void initialize_downmove();

    virtual void block_upmove();
    virtual void block_downmove();

    void equaliseEvents();
    void blockWasHit(bool isDown);

    STATE_FUNC_DECLARE(daEnBlockFlag_c, Wait);

    dPanelObjList_c mTile;

    BLOCK_FLAG_MODE_e mFlagMode;

    u16 mEventID1, mEventID2;
};