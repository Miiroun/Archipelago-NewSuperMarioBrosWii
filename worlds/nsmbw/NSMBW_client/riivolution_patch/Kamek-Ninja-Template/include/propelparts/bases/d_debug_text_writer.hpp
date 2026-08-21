#pragma once
#include <nw4r/ut.h>

// A simple class for writing text directly to the screen

class dDebugTextWriter_c : public nw4r::ut::TextWriter {
public:
    dDebugTextWriter_c();

    void Reset();
    void Print(f32 x, f32 y, const char *msg, ...);
    void Begin();
    void End();

    bool mIsInBegin;
};