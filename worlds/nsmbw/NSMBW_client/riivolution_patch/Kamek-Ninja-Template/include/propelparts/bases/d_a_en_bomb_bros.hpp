#pragma once
#include <game/bases/d_a_en_bros_base.hpp>
#include <propelparts/bases/d_a_bomb_projectile.hpp>

class daEnBombBros_c : public daEnBrosBase_c {
public:
    daEnBombBros_c();

    virtual bool hitCallback_Rolling(dCc_c *self, dCc_c *other);

    virtual void initializeState_Ice();

    virtual double getCreateWeaponFrm() const;
    virtual double getAttackFrm() const;
    virtual void setSpeed();
    virtual int checkAtkArea();
    virtual int getColor();
    virtual void setAtkTimer();

    virtual void weaponCreate();
    virtual void weaponAttack();
    virtual void setJumpCnt();
    virtual void setJump();
    virtual void beginJump();

    daBombProjectile_c *getProjectile();
};