#pragma once
#include <game/bases/d_scene.hpp>
#include <game/bases/d_info.hpp>

class dScRestartCrsin_c : public dScene_c {
public:
    static void startTitle(unsigned char, bool);
    static void reStartPeachCastle();

    static dInfo_c::StartGameInfo_s m_startGameInfo;
};
