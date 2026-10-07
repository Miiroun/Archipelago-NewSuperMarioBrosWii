// [Gecko]
// $Fall Damage [mkwcat]
// *Adds aggressive fall damage to the game. Can currently be cheesed using
// *Yoshi or Mini Mushroom. Note some levels may be impossible without
// *[Allow-Movement-During-Cutscenes](Allow-Movement-During-Cutscenes.md).
// *
// *Adds unique death messages for [Death-Messages](Death-Messages.md).


#include <types.h>

//#include "d_pl_base.hpp"
//#include "d_a_player_base.hpp"
#include "d_actor.hpp"

#include <kamek.h>
//#include <kameksdk.h>
#include "mem.h"

#include <sound.hpp>


class daPlBase_c : public dActor_c
{
public:
    enum DamageType_e {
            DAMAGE_NORMAL = 0,
            DAMAGE_NORMAL2 = 1,
            DAMAGE_KNOCKBACK_AND_HURT = 2,
            DAMAGE_KNOCKBACK_LONG = 3, // Player does not take damage
            DAMAGE_KNOCKBACK_LONG2 = 4, // Player does not take damage
            DAMAGE_KNOCKBACK_SHORT = 5, // Player does not take damage
            DAMAGE_KNOCKBACK_SHORT2 = 6, // Player does not take damage
            DAMAGE_LAVA = 7,
            DAMAGE_FIRE = 8, // Looks the same as DAMAGE_NORMAL?
            DAMAGE_ELEC_SHOCK = 9,
            DAMAGE_POISON_WATER = 10,
            DAMAGE_CRUSH = 11,
            DAMAGE_EAT_DIE = 12,
            DAMAGE_EAT_DIE2 = 13, // Like DAMAGE_EAT_DIE but does not stop the music
            DAMAGE_UNKNOWN = 14,
            DAMAGE_FREEZE = 15,
            DAMAGE_FREEZE2 = 16,
            DAMAGE_BOUNCE = 17, // Makes the player do a squishy animation
            DAMAGE_POISON_FOG = 18,
        };

    virtual bool setDamage2(dActor_c *, daPlBase_c::DamageType_e);

    static const float sc_DirSpeed[];
    static const float sc_JumpSpeed;
    static const float sc_JumpSpeedNuma1;
    static const float sc_JumpSpeedNuma2;
    static const float sc_WaterWalkSpeed;
    static const float sc_WaterSwimSpeed;
    static const float sc_WaterJumpSpeed;
    static const float sc_WaterMaxFallSpeed;
    static const float sc_MaxFallSpeed;
    static const float sc_MaxFallSpeed_Foot;
    static const float sc_MaxFallDownSpeed;
    static const float scTurnPowerUpRate;
    static const float scDokanInSpeedX;
    static const float scDokanInWidthX;
    static const float scDokanInMoveSpeed;
    static const float scDokanWaitAnmFixFrame;

    // [Inofficial constants]

    /// Number of walking frames before being able to enter a pipe.
    /// @see mDokanCounterL, mDokanCounterR
    static const int sc_DokanEnterThreshold = 10;
    static const int sc_DemoWaitDuration = 10; ///< Number of frames to wait before transitioning from StateID_DemoWait.
    static const int sc_DemoPoleWaitTurn = 5; ///< Number of frames to wait before turning towards the screen in the goal pole animation.
    static const int sc_DemoPoleWaitEnd = 7; ///< Number of frames to wait before doing the course clear pose in the goal pole animation.
};




extern "C" void HandleGroundPoundLand(daPlBase_c* player)
{
    player->setDamage2(nullptr, daPlBase_c::DAMAGE_CRUSH);
}

extern "C" void HandleNormalLand(daPlBase_c* player)
{
    float accel = player->mSpeed.y;

    // Deal damage based on how fast the player was falling
    if (accel >= -3.5) {
        return;
    }

    player->setDamage2(nullptr, daPlBase_c::DAMAGE_BOUNCE);

    if (accel <= -7.4) {
        //player->playSound(SE_PLY_PRPL_LETDOWN_FAST_LAND, 0);
        //dAcPy_c::sDeathMessageOverride = "%s fell from a high place";
        player->setDamage2(nullptr, daPlBase_c::DAMAGE_CRUSH);
    } else if (accel <= -5.8) {
        //dAcPy_c::sDeathMessageOverride = "%s hit the ground too hard";
        player->setDamage2(nullptr, daPlBase_c::DAMAGE_NORMAL);
    }
}

/*
kmBranchDefAsm(0x8004939C, 0x800493A0)
{
    mr      r3, r31
    bl      HandleGroundPoundLand
    addi    r3, r31, 0xEA4 // Original instruction
    blr
}


kmBranchDefAsm(0x800550B4, 0x800550B8)
{
    mr      r3, r31
    bl      HandleNormalLand
    lwz     r3, 0x10D4(r31) // Original instruction
    blr
}
*/