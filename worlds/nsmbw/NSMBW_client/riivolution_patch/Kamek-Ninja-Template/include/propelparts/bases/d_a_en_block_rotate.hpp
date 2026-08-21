#pragma once
#include <game/bases/d_a_en_blockmain.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/bases/d_bg.hpp>

// SMW-style flip blocks

class daEnBlockRotate_c : public daEnBlockMain_c {
public:
    virtual int create();
    virtual int doDelete();
    virtual int execute();
    virtual int draw();
    virtual int preDraw();

    virtual void initialize_upmove();
    virtual void initialize_downmove();

    virtual void block_upmove();
    virtual void block_downmove();

    void calcModel();
    void blockWasHit(bool isDown);
    bool playerOverlaps();
    void createItem();
    void destroyBlock();
    bool checkTenCoin();

    static void callBackF(dActor_c *self, dActor_c *other);

    STATE_FUNC_DECLARE(daEnBlockRotate_c, Wait);
    STATE_FUNC_DECLARE(daEnBlockRotate_c, HitWait);
    STATE_FUNC_DECLARE(daEnBlockRotate_c, Flipping);

    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mFlipBlockModel;

    dPanelObjList_c mTile;

    int mFlipsRemaining;
    mVec3_c mInitialPos;

    int mContents;
    int mOriginalContents;
    bool mIndestructible;
};