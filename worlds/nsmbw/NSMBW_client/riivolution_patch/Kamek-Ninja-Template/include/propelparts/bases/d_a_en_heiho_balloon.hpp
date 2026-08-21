#pragma once
#include <propelparts/bases/d_a_en_heiho.hpp>

class daEnHeihoBalloon_c : public daEnHeiho_c {
public:
    enum BALLOON_MOVEMENT_e {
        MOVEMENT_NONE,
        MOVEMENT_HORIZONTAL,
        MOVEMENT_VERTICAL,
        MOVEMENT_CIRCLE,
    };

    virtual int create();

    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual bool hitCallback_Star(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Spin(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_HipAttk(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_YoshiHipAttk(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Fire(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Ice(dCc_c *self, dCc_c *other);

    virtual void initializeState_DieFall();

    virtual void initializeState_EatIn();

    virtual bool createIceActor();

    virtual void FumiScoreSet(dActor_c *actor);

    virtual void fumiSE(dActor_c *actor);
    virtual void fumiEffect(dActor_c *actor);
    virtual void spinfumiSE(dActor_c *actor);
    virtual void spinfumiEffect(dActor_c *actor);

    virtual void yoshifumiSE(dActor_c *actor);
    virtual void yoshifumiEffect(dActor_c *actor);

    virtual void loadModel();
    virtual void updateModel();
    virtual void drawModel();
    virtual void calcModel();

    virtual void setTurnByPlayerHit(dActor_c *player);
    virtual void setInitialState();

    void popBubble(dActor_c *player);
    void popIfPlayerBelow();

    STATE_FUNC_DECLARE(daEnHeihoBalloon_c, Balloon);
	STATE_FUNC_DECLARE(daEnHeihoBalloon_c, BalloonFall);

    nw4r::g3d::ResFile mBalloonRes;
    m3d::mdl_c mBalloonModel;
    m3d::anmChr_c mBalloonAnm;
    m3d::anmTexSrt_c mBalloonSrt;
    m3d::anmMatClr_c mBalloonClr;

    bool mIsFloating;
    mVec2_c mBalloonBaseline;
    dCc_c mBalloonCc;
    float mBalloonScale;
    bool mPopCollision;

    bool mIsBalloon;
    BALLOON_MOVEMENT_e mMovement;
    u8 mBalloonDistance;
    bool mPopSensor;
    u8 mBalloonColor;
};