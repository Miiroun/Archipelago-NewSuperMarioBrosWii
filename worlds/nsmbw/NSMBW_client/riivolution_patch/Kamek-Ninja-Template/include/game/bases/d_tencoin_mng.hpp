#pragma once

#include <game/mLib/m_vec.hpp>

class dTenCoinMng_c {
public:
    int tencoin_check(mVec3_c *, int, int);

    static dTenCoinMng_c *m_instance;
};