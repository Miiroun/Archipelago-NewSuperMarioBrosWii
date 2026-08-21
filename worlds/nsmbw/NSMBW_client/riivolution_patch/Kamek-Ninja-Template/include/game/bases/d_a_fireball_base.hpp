#pragma once

#include <game/bases/d_actor_state.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_circle_light_mask.hpp>
#include <game/mLib/m_effect.hpp>

class daFireBall_Base_c : public dActorState_c {
public:
    virtual int create();

    virtual int doDelete();

    virtual int execute();
    virtual int preExecute();

    virtual int draw();

    virtual void deleteReady();

    virtual ~daFireBall_Base_c();
    
    virtual void setEatTongue(dActor_c *eatingActor);
    virtual void setEatTongueOff(dActor_c *eatingActor);

    // New vfuncs
    STATE_VIRTUAL_FUNC_DECLARE(daFireBall_Base_c, Move);
    STATE_VIRTUAL_FUNC_DECLARE(daFireBall_Base_c, Kill);
    STATE_VIRTUAL_FUNC_DECLARE(daFireBall_Base_c, EatIn);
    STATE_VIRTUAL_FUNC_DECLARE(daFireBall_Base_c, EatNow);

    virtual bool initialize();
    virtual bool createCheck();
    virtual void setCc();
    virtual void setBc();
    virtual void chgZpos();
    virtual void fireEffect();
    virtual void beginSplash(float);
    virtual void beginYoganSplash(float);
    virtual void beginPoisonSplash(float);
    virtual float getLightRad() const;
    virtual void entryHIOnode();
    virtual void retireHIOnode();

    void kill();

    dHeapAllocator_c mAllocator;
    dCircleLightMask_c mLight;
    u32 mDidSplash;
    u32 mKillCountDownToDestroy;
    u32 mLiquidStat;
    u32 m_414;
    float mLiquidHeight;
    mVec3_c mStartPos;
    u32 m_428;
    mEf::levelEffect_c mEffect;
};