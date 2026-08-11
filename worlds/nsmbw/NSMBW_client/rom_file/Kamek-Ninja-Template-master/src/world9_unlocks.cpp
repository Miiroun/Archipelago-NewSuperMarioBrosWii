#include <kamek.h>
#include <kamek_sdk.h>

// it happens at 0x808CE56C, the game checks if its world 9, then calls setSpecialWorldAnm() (0x808CED00)
// dWmLib::isSpecialWorldCourseOpen() just calls dWmLib::isRemainderCollectionCoin(), which returns if the collected number of star coins (for that world) is greater than or equal to the max number of coins

/*

// how to edit to easily change with dme?
kmBranchDefCpp(0x808ce57c, 0, daWmCourse_c *param_1)
{
    bool bVar1;
    uint courseIdx;

    courseIdx = (param_1->_)._.m_param & 0xff
    if ((courseIdx < 10) && (bVar1 = dWmLib::isSpecialWorldCourseOpen(int)(courseIdx), !bVar1)) {
        daWmCourse_c::setAnm(param_1, 0, 0.0, 0.0);
    }
    return;
}

*/

/* Original function
void daWmCourse_c::setSpecialWorldAnm(daWmCourse_c *param_1)
{
    bool bVar1;
    uint courseIdx;

    courseIdx = (param_1->_)._.m_param & 0xff
    if ((courseIdx < 10) && (bVar1 = dWmLib::isSpecialWorldCourseOpen(int)(courseIdx), !bVar1)) {
        daWmCourse_c::setAnm(param_1, 0, 0.0, 0.0);
    }
    return;
}
*/