#pragma once
#include <game/bases/d_actor.hpp>
#include <game/bases/d_bg.hpp>
#include <game/bases/d_bg_ctr.hpp>

class daLiftBgBase_c : public dActor_c {
public:
    enum COLLTYPE_e {
        COLL_SOLID,
        COLL_SEMISOLID,
        COLL_NONE,
        COLL_THINRIGHT,
        COLL_THINLEFT,
        COLL_THINTOP,
        COLL_THINBOTTOM,
        COLL_CIRCLE,
    };

    enum CONTROLTYPE_e {
        CONTROL_PATH,
        CONTROL_ROTATION,
        CONTROL_PAIR_OBJ,
    };

    // fBase_c overrides
    virtual int create();
    virtual int doDelete();
    virtual int execute();

    virtual bool initMovement();
    virtual void executeMovement();

    void getRange();
    void createPanelObj();
    void deletePanelObj();
    void updatePanelObj();

    void setVisible(bool isVisible);

    void initCollision();

    static void callBackF(dActor_c *self, dActor_c *other);
    static void callBackH(dActor_c *self, dActor_c *other);
    static void callBackW(dActor_c *self, dActor_c *other, u8 direction);

    static bool checkRevFoot(dActor_c *self, dActor_c *other);
    static bool checkRevHead(dActor_c *self, dActor_c *other);
    static bool checkRevWall(dActor_c *self, dActor_c *other, u8 direction);

    dBg_ctr_c mBg;
    dRideRoll_c mRide;

    dPanelObjList_c *mTiles;
    int mTileCount;

    float zOrder;

    int mSrcX, mSrcY;
    int mWidth, mHeight;

    bool mVisible;
    bool mFindFail;

    CONTROLTYPE_e mControlType;

    // Settings
    u8 mRectIdx;
    COLLTYPE_e mCollType;
};