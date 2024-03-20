/*
 * malicious-rep-bin-party.cpp
 *
 */

#include "GC/ShareParty.h"
#include "GC/ShareParty.hpp"
#include "GC/ShareSecret.hpp"
#include "GC/MaliciousRepSecret.h"
#include "GC/RepPrep.h"

#include "GC/Machine.hpp"
#include "GC/Processor.hpp"
#include "GC/Program.hpp"
#include "GC/Thread.hpp"
#include "GC/ThreadMaster.hpp"
#include "GC/RepPrep.hpp"

#include "Processor/Instruction.hpp"
#include "Protocols/MaliciousRepMC.hpp"
#include "Protocols/MAC_Check_Base.hpp"
#include "Protocols/Beaver.hpp"

int main(int argc, const char** argv)
{
    GC::simple_binary_main<GC::MaliciousRepSecret>(argc, argv);
}
