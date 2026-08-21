#pragma once
#include <game/bases/d_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>

class daEnStarCoinFake_c : public dEn_c {
public:
    // fBase_c overrides
    virtual int create();
    virtual int execute();
    virtual int draw();

    // dEn_c overrides
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual bool hitCallback_Star(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Shell(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Fire(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Ice(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_YoshiFire(dCc_c *self, dCc_c *other);

    void collect();

    dHeapAllocator_c mAllocator;
    m3d::mdl_c mModel;

    bool mRotateX;
};