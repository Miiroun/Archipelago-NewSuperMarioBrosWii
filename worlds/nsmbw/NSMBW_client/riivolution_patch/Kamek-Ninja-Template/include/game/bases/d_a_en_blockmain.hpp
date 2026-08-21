#pragma once
#include <game/bases/d_enemy.hpp>
#include <game/bases/d_bg_ctr.hpp>

class daEnBlockMain_c : public dEn_c {
public:
    virtual ~daEnBlockMain_c(); 

    virtual void initialize_upmove();
    virtual void initialize_downmove();

    virtual void block_upmove();
    virtual void block_upmove_diff();
    virtual void block_downmove();
    virtual void block_downmove_end();
    virtual void block_downmove_diff();
    virtual void block_downmove_diffend();

    virtual void block_scale_set(u8 movingDown);

    STATE_VIRTUAL_FUNC_DECLARE(daEnBlockMain_c, UpMove);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBlockMain_c, DownMove);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBlockMain_c, DownMoveEnd);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBlockMain_c, UpMove_Diff);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBlockMain_c, DownMove_Diff);
    STATE_VIRTUAL_FUNC_DECLARE(daEnBlockMain_c, DownMove_DiffEnd);

    void Block_CreateClearSet(float initialY);
    void Block_ExecuteClearSet();
    u8 ObjBgHitCheck();
    int YoshiEggCreateCheck(int);
    void jumpdai_set();
    void item_ivy_set(u8, u8);
    void yossy_set(ulong);
    void item_sound_set(mVec3_c& position, int type, s8 player_no, u8, u8);
    bool item_start_check(int);
    void continue_star_check(int *item_type, s8 player_no);
    int player_bigmario_check(s8 player_no);
    int playernumber_set();

    static bool checkRevFoot(dActor_c*, dActor_c*);
    static bool checkRevHead(dActor_c*, dActor_c*);
    static bool checkRevWall(dActor_c*, dActor_c*, u8);

    static void callBackF(dActor_c*, dActor_c*);
    static void callBackH(dActor_c*, dActor_c*);
    static void callBackW(dActor_c*,dActor_c*, u8);

    u8 mPad[0x10];
    dBg_ctr_c mBg;
    u8 mPad2[0x18];
    float mInitialY;
    float mMoveAccel;
    float m_114, m_118, m_11c;
    u32 mDownMoveCounter;
    float m_124, m_128;
    u32 mAmountOfItems;
    u8 mPad3[0xC];
    short mTimer;
    u8 mPad4[0x27];
    u8 mIsGroundPound, mAnotherFlag;
    u8 m_167, m_168, m_169;
    u8 mPad5[0x6];
    u8 mPlayerID;
    u8 mPad6[0x3];
};

extern const u32 l_item_values[18];