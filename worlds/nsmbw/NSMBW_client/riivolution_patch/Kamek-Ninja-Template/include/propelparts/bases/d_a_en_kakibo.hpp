#pragma once
#include <game/bases/d_a_en_kuribo.hpp>

class daEnKakibo_c : public daEnKuribo_c {
public:
    enum KAKIBO_ANIM_ID_e {
        ANM_WALK,
        ANM_WALK0,
        ANM_WALK1,
    };

    virtual void finalUpdate();

    virtual void initializeState_DieOther();

    virtual void initializeState_DieFall();
    
    virtual void initializeState_Walk();
    virtual void executeState_Walk();

    virtual void executeState_Turn();

    virtual void createBodyModel();

    virtual void initialize();
    virtual void setTurnByEnemyHit();
    
    virtual void setWalkAnm();

    virtual bool isBgmSync() const;

    void setKakiboAnm(KAKIBO_ANIM_ID_e anmId);

    bool checkGround(float xDist);
    bool checkTurnSaka();
    bool checkLedge(float xOffset);

    void calcHa() {
        if (mBgmHoldTimer != 0) {
            mBgmHoldTimer--;
            mHaAngleZ = 0x1555; // 30 degrees
            mHaScale = 1.2f;
        } else {
            sLib::chaseAngle((short*)&mHaAngleZ, 0, 0x222); // 3 degrees per frame
            sLib::chase(&mHaScale, 1.0f, 0.02f);
        }
    }

    u8 mKakiboAnm;
    bool mIsWalk1;
    int mBgmHoldTimer;
    mAng mHaAngleZ;
    float mHaScale;
};