#pragma once
#include <game/bases/d_a_fireball_base.hpp>

class daFireBall_Nipper_c : public daFireBall_Base_c {
public:
    void executeState_Move();

    bool initialize();
    
    void setCc();
};

const float l_nipper_fire_speeds[4] = {0.453125, 0.90625, 1.359375, 1.8125};