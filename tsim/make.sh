#!/bin/sh

if [ $# -eq 0 ] 
then
    echo "Compile a C file with tricore-gcc and run it with TSIM"
    echo "Usage: $0 <C source code file>"
    exit 1
fi



# path to tricore gcc
#TRICORE_GCC_PATH=${HOME}/.local/share/tricore-gcc-toolchain-11.3.0/INSTALL/bin/

# default tsim path from Infineon package
TSIM_PATH=/opt/Tools/TSIM-Tricore-instruction-set-simulator/1.18.196/bin/



name_dot_c=$1
name=${name_dot_c%.c}

mkdir -p build

${TRICORE_GCC_PATH}tricore-elf-gcc -mcpu=tc39xx -g -nostartfiles \
    -Wl,-Map,"build/$name.map" -T tsim.ld tsim_startup.c \
    -o "build/$name.elf" "$name_dot_c"


if [ -f ${TSIM_PATH}../config/tc162/tc39xx/MConfig ]
then
    # use the default configuration from Infineon
    ${TSIM_PATH}tsim16p_e -e -h -s -H -z \
        -MConfig ${TSIM_PATH}../config/tc162/tc39xx/MConfig \
        -OConfig ${TSIM_PATH}../config/tc162/tc39xx/OConfig \
        -o "build/$name.elf" -trace-instr-file "build/$name.tsim"
else
    # use a minimal configuration
    ${TSIM_PATH}tsim16p_e -e -h -s -H -z \
        -MConfig MConfig \
        -o "build/$name.elf" -trace-instr-file "build/$name.tsim"
fi
