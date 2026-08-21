#pragma once
#include <game/mLib/m_3d.hpp>

// Actor spawn point/size rendering

class dActorSpawnRender_c : public m3d::proc_c {
public:
    dActorSpawnRender_c();

    virtual void drawOpa();
    virtual void drawXlu();

    static dActorSpawnRender_c m_instance;
};