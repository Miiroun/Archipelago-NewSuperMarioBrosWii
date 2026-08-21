#pragma once
#include <game/bases/d_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/bases/d_effect.hpp>

// Custom shyguy enemy

class daEnHeiho_c : public dEn_c {
public:
    enum HEIHO_TYPE_e {
        HEIHO_TYPE_WALKER,
        HEIHO_TYPE_WALKER_LEDGE,
        HEIHO_TYPE_SLEEPER,
        HEIHO_TYPE_JUMPER,
        HEIHO_TYPE_PACER,
    };

    // fBase_c overrides
    virtual int create();
    virtual int execute();
    virtual int draw();

    // dBaseActor_c overrides
    virtual void finalUpdate();

    // dEn_c overrides
    virtual void Normal_VsEnHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual void initializeState_DieFall();
    virtual void executeState_DieFall();

    virtual void initializeState_DieOther();
    virtual void executeState_DieOther();

    virtual bool setDamage(dActor_c *actor);

    virtual bool createIceActor();

    // New functions
    virtual void loadModel();
    virtual void updateModel();
    virtual void drawModel();
    virtual void calcModel();

    virtual void setTurnByPlayerHit(dActor_c *player);
    virtual void setInitialState();

    void setWalkSpeed();
    void playChrAnim(const char* name, m3d::playMode_e playMode, float blendFrame, float rate);
    bool checkLedge(float xOffset);

    void reactFumiProc(dActor_c *player);
    void reactSpinFumiProc(dActor_c *player);
    void reactYoshiFumiProc(dActor_c *player);

    // States
    STATE_FUNC_DECLARE(daEnHeiho_c, Walk);
	STATE_FUNC_DECLARE(daEnHeiho_c, Turn);
    STATE_FUNC_DECLARE(daEnHeiho_c, Sleep);
    STATE_FUNC_DECLARE(daEnHeiho_c, Jump);
    STATE_FUNC_DECLARE(daEnHeiho_c, Dizzy);
    STATE_FUNC_DECLARE(daEnHeiho_c, Idle);

    // Internal variables
    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mHeihoModel;
    m3d::anmChr_c mAnmChr;
    m3d::anmTexPat_c mAnmTexPat;

    int mTimer;
	float mDying;
	float mBaseline;
    float mFinalPos[2];
    int mJumpCounter;

    mEf::levelEffect_c mDizzyEffect;

    // Settings variables
    HEIHO_TYPE_e mType;
    int mColor;
    u8 mHealth;
    int mDistance;
    u8 mSpawnDir;

    static const float smc_WALK_SPEED;
};