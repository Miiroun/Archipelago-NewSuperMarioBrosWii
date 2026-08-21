#pragma once
#include <game/bases/d_a_en_kuribo.hpp>

class daEnKabochan_c : public daEnKuribo_c {
public:
    // dEn_c overrides
    virtual bool hitCallback_HipAttk(dCc_c *self, dCc_c *other);

    virtual void setDeathSound_HipAttk();

    virtual void initializeState_DieOther();

    virtual void hipatkEffect(const mVec3_c &pos);

    virtual bool createIceActor();

    virtual void fumiSE(dActor_c *actor);

    // daEnKuriboBase_c overrides
    virtual void reactFumiProc(dActor_c* player);

    virtual void createBodyModel();

    virtual void setWalkSpeed();
    virtual void playWalkAnm();
    virtual void setWalkAnm();

    bool mIsCracked;
    m3d::anmMatClr_c mAnmClr;

    mEf::levelEffect_c mBreakEffect;
};

const float l_splunkin_speeds[2][2] = {{0.5, -0.5},{0.75, -0.75}};