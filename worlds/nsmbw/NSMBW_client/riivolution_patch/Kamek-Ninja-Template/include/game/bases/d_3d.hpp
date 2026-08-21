#pragma once
#include <game/mLib/m_3d.hpp>

namespace d3d {

class proc_c : public m3d::proc_c {

};

void setMatCullMode(m3d::bmdl_c *, int, _GXCullMode);

} // namespace d3d