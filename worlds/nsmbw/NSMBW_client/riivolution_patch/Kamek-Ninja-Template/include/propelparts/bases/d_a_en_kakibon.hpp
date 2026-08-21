#pragma once
#include <propelparts/bases/d_a_en_kuribon.hpp>

class daEnKakibon_c : public daEnKuribon_c {
public:
    virtual void executeState_Walk();

    virtual void createBodyModel();

    virtual bool isBgmSync() const;

    bool checkLedge(float xOffset);
};