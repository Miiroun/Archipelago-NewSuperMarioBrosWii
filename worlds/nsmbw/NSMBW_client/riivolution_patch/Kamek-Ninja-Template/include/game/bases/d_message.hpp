#pragma once

#include <lib/egg/core/eggMsgRes.h>
#include <game/bases/d_dvd.hpp>

class MsgRes_c : public EGG::MsgRes {
public:
    MsgRes_c(const void *, EGG::Heap *);

    u8 getFont(ulong messageGroup, ulong messageID);
    u16 getScale(ulong messageGroup, ulong messageID);
};

class dMessage_c {
public:
    void buildMsgRes(EGG::Heap *, int index); // @unofficial

    static MsgRes_c *getMesRes();
    static MsgRes_c *getPropelMsgRes(); // @unofficial

    static const wchar_t *getMsg(unsigned long group, unsigned long messageID);
    static const wchar_t *getPropelMsg(unsigned long group, unsigned long messageID); // @unofficial

    dDvd::loader_c mMsgLoader;
    void *mpFile;
    MsgRes_c *mpMsgRes;

    // @unofficial
    void *mpPropelFile;
    MsgRes_c *mpPropelMsgRes;
};

extern dMessage_c l_dMessage_obj;
