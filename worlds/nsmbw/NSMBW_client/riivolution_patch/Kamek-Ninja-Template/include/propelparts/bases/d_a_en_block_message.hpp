#pragma once
#include <game/bases/d_a_en_blockmain.hpp>
#include <game/bases/d_bg.hpp>

// Message block from SMW

class daEnBlockMessage_c : public daEnBlockMain_c {
public:
    virtual int create();
    virtual int doDelete();
    virtual int execute();

    virtual void block_upmove();
    virtual void block_downmove();

    void blockWasHit(bool isDown);

    STATE_FUNC_DECLARE(daEnBlockMessage_c, Wait);

    dPanelObjList_c mTile;

    unsigned long mMessageId;
};