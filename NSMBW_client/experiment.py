# should not be included in build but is for testing writing python code that easier to test here
from geckolibs.geckocode import *
from geckolibs.gct import *

gct = GeckoCodeTable.from_bytes(b"C205FBFC 00000004 3EC0803A 82D61AC8 72D60A00 4182000C")

print(gct)
for command in gct:
    print(command)