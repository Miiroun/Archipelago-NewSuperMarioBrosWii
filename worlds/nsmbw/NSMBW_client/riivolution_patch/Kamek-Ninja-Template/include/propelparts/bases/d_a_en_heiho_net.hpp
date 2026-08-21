#pragma once
#include <game/bases/d_a_net_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>

class daEnHeihoNet_c : public daNetEnemy_c {
public:
    virtual int create();
    virtual int draw();

    virtual void finalUpdate();

    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual void initializeState_DieFumi();
    virtual void executeState_DieFumi();

    virtual void initializeState_DieFall();
    virtual void executeState_DieFall();

    virtual bool createIceActor();

    virtual void finalizeState_NetMove();

    virtual void mdlPlay();
    virtual void calcMdl();

    void loadModel();
    void playChrAnim(const char* name, m3d::playMode_e playMode, float blendFrame, float rate);
    void playClimbAnim();

    int wireBgCheck(const mVec2_c &offset);

    void setMoveState();

    void checkAttack();
    bool isPlayerInAttackRange();
    void attackPlayer();

    STATE_FUNC_DECLARE(daEnHeihoNet_c, MoveUD);
	STATE_FUNC_DECLARE(daEnHeihoNet_c, Turn_St);
    STATE_FUNC_DECLARE(daEnHeihoNet_c, Turn_Ed);
    STATE_FUNC_DECLARE(daEnHeihoNet_c, MoveLR);
    STATE_FUNC_DECLARE(daEnHeihoNet_c, Turn);
    STATE_FUNC_DECLARE(daEnHeihoNet_c, Attack);

    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mRes;
    nw4r::g3d::ResMdl mResMdl;
    m3d::mdl_c mHeihoModel;
    m3d::anmChr_c mAnmChr;
    m3d::anmTexPat_c mAnmTexPat;

    int mColor;
    bool mVertical;
    bool mAttacks;

    float mTargetYPos;
    u32 mTurnDirection;
    int mTurnTimer;
    s16 mTurnStep;

    int mAttackTimer;

    static const float smc_CLIMB_SPEED;
};

extern const s16 l_heiho_net_angleY[];
extern const float l_heiho_net_Z_pos[];
extern const mVec2_c l_heiho_net_offset_UD[];
extern const mVec2_c l_heiho_net_offset_LR[];
extern const m3d::playMode_e l_heiho_net_playmode[];