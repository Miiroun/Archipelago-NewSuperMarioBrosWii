#pragma once
#include <game/bases/d_enemy.hpp>

class daNetEnemy_c : public dEn_c {
public:
    virtual int execute();

    virtual ~daNetEnemy_c();

    STATE_VIRTUAL_FUNC_DECLARE(daNetEnemy_c, NetWait);
    STATE_VIRTUAL_FUNC_DECLARE(daNetEnemy_c, NetMove);

    virtual void mdlPlay();
    virtual void calcMdl();

    static void setWireTurn(int);

    u32 mIsNetTurn;
};