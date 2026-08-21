#pragma once

#include <game/bases/d_player_model_base.hpp>

class dPlayerMdl_c : public dPyMdlBase_c {
public:
    ///< @unofficial
    enum MODEL_e {
        MODEL_NORMAL = 0,
        MODEL_SMALL = 1,
        MODEL_PROPELLER = 2,
        MODEL_PENGUIN = 3,

        MODEL_COUNT = 4,
    };

    ///< @unofficial
    struct ModelData {
        const char* mResName;
        const char* mAnmResName;
        const char* mBodyModels[MODEL_COUNT];
        const char* mHeadModels[MODEL_COUNT];
        float m_28;
        float m_2c;
        float m_30;
        float m_34;
    };

    ///< @unofficial
    struct modelCntr_c {
        m3d::mdl_c mBody;
        m3d::mdl_c mHead;
    };

    dPlayerMdl_c(u8 index);
    virtual ~dPlayerMdl_c();

    virtual int getFaceJointIdx() const;
    virtual void createModel();
    virtual void initialize();
    virtual void play();
    virtual void _calc();
    virtual void calc2();
    virtual void draw();
    virtual m3d::mdl_c *getBodyMdl();
    virtual const void *getAnmResFile() const;
    virtual void setPlayerMode(int);
    virtual void setColorType(u8);
    virtual void setDark(int);

    virtual void onStarAnm();
    virtual void offStarAnm();

    virtual bool getHeadPropelJointMtx(mMtx_c *);
    virtual void vf58(); ///< @unofficial

    virtual bool setPersonalAnm(int, nw4r::g3d::ResAnmChr *, int);

    virtual void copyAnm();
    virtual void _setFootAnm(nw4r::g3d::ResAnmChr &, m3d::playMode_e, float, float, float);
    virtual void _setBodyAnm(nw4r::g3d::ResAnmChr &, m3d::playMode_e, float, float, float);
    virtual void setAnmBind();
    virtual void setPersonalRideAnm(int, nw4r::g3d::ResAnmChr *);

    virtual void setTexAnmType(TexAnmType_e);
    virtual void setPropelRollSpeed(s16);
    virtual s16 getPropelRollSpeed() const;
    virtual void setPropelRollAngle(s16);
    virtual s16 getPropelRollAngle() const;
    virtual void setPropelScale(float);
    virtual float *getLegLengthP(u8);

    ///< @unofficial
    virtual void setCurrentModel(MODEL_e model);
    virtual void callbackTimingA(nw4r::g3d::ChrAnmResult *, nw4r::g3d::ResNode);
    virtual float getAimMotionShareScale();
    virtual void createPlayerModel();

    m3d::anmTexPat_c *getHeadTexAnm();

    nw4r::g3d::ResFile mModelResFile;
    nw4r::g3d::ResFile mCommonAnimResFile;
    nw4r::g3d::ResFile mAnimResFile;
    u8 mPad[0x250];
    modelCntr_c mModels[MODEL_COUNT];
    m3d::anmTexPat_c mBodySwitchAnim;
    m3d::anmMatClr_c mBodyStarAnim;
    m3d::anmTexPat_c mHeadSwitchAnim;
    m3d::anmTexPat_c mPropelHeadSwitchAnim;
    m3d::anmTexPat_c mPenguinHeadSwitchAnim;
    m3d::anmMatClr_c mHeadStarAnim;
    MODEL_e mModelIdx;
    MODEL_e mLastModelIdx;
    const ModelData* mpModelData;
    u32 mFaceJointIdx;
    s16 mPropelRollAngle;
    u16 mPropelRollSpeed;
    float mPropelScale;
    u8 mPad2[0x9C];
};