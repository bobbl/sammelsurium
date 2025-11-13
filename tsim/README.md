User-mode emulation for Tricore with TSIM
=========================================

QEMU User-mode Emulation is a practical solution for testing algorithms
directly without having to set up a microcontroller system and boot it every
time you test. Unfortunately, [QEMU](https://www.qemu.org/) only supports full
system emulation of Aurix microcontrollers with TriCore instruction set.
User-mode emulation is not available for TriCore.

Since Infineon's Tricore instruction set simulator
[TSIM](https://softwaretools.infineon.com/tools/com.ifx.tb.tool.tsimtricoreinstructionsetsimulator)
has a virtual I/O feature that can be used for user-mode emulation.

Compile a C source code file with the Tricore gcc and run it with TSIM in
user-mode:

    ./make.sh test.c

Details on the auxiliary files can be found in
[this blog article](https://bobbl.github.io/tricore/2025/11/12/tricore-user-mode-emulation.html)
