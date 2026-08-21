#pragma once

#include <game/mLib/m_vec.hpp>

class dObjBlockMng_c {
public:
    void set_objblock_check(mVec3_c *, u16, int, int);
    int create_objblock_check(mVec3_c *, u16);

    static dObjBlockMng_c *m_instance;
};