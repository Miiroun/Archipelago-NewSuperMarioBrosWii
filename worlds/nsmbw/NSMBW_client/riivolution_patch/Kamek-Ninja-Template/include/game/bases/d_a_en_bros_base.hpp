#pragma once
#include <game/bases/d_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/bases/d_effect.hpp>

class daEnBrosBase_c : public dEn_c {
public:
    class nodeCallback_c : public m3d::mdl_c::callback_c {
    public:
        virtual ~nodeCallback_c();
        virtual void timingA(ulong nodeId, nw4r::g3d::ChrAnmResult *anmRes, nw4r::g3d::ResMdl resMdl);

        daEnBrosBase_c *mpOwner;
    };

    // fBase_c overrides
    virtual int create();
    virtual int doDelete();
    virtual int execute();
    virtual int draw();

    virtual ~daEnBrosBase_c();

    // dBaseActor_c overrides
    virtual void finalUpdate();

    // dEn_c overrides
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual bool hitCallback_Spin(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_HipAttk(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Ice(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_YoshiBullet(dCc_c *self, dCc_c *other);

    virtual void initializeState_DieFumi();
    virtual void executeState_DieFumi();
    virtual void finalizeState_DieFumi();

    virtual void initializeState_DieFall();
    virtual void executeState_DieFall();
    virtual void finalizeState_DieFall();
    
    virtual bool setDamage(dActor_c *actor);

    virtual bool createIceActor();
    virtual void setIceAnm();

    virtual void returnState_Ice();

    // New virtuals
    STATE_VIRTUAL_FUNC_DECLARE(daEnBrosBase_c, Move);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBrosBase_c, Attack);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBrosBase_c, JumpSt);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBrosBase_c, Jump);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBrosBase_c, JumpEd);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBrosBase_c, AirAttack);

    virtual double getCreateWeaponFrm() const;
    virtual double getAttackFrm() const;
    virtual void setSpeed();
    virtual int checkAtkArea();
    virtual int getColor();
    virtual void setAtkTimer();
    virtual void getAdjustOffset();
    virtual void calcMoveDir();
    virtual void setWeaponPos();
    virtual void weaponCreate();
    virtual void weaponAttack();
    virtual void setJumpCnt();
    virtual void setJump();
    virtual void beginJump();
    virtual int isInvalidBg();
    virtual bool isAttackOK() const;
    virtual void beginAttk();
    virtual void setAttackAnm();
    virtual void initMoveCnt();
    virtual void initPosLv();
    virtual void initType();
    virtual void entryHIO();
    virtual void removeHIO();

    dHeapAllocator_c mAllocator;

    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mModel;
    m3d::anmChr_c mAnmChr;
    nw4r::g3d::ResAnmTexPat mResPat;
    m3d::anmTexPat_c mAnmTexPat;

    mMtx_c mMtx1;
    mMtx_c mMtx2;
    mMtx_c mMtx3;
    mMtx_c mMtx4;
    mMtx_c mMtx5;

    int mAttackTimer;
    int mJumpTimer;
    int mDirChanges;
    int mWalkBackwards;
    int mNotMoveTimer;
    int mAttackCount;
    int m_1d0;

    int m_1d4;
    float m_1d8, m_1dc;
    u16 m_1e0, m_1e2;
    mVec3_c mInitialPos;
    u8 mFacingDirection;
    fBaseID_e mWeaponID;

    nodeCallback_c mNodeCallback;

    mEf::levelEffect_c mEffect;
};