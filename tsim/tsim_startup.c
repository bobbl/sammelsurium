/* Minimal startup code for Infineon's tsim Tricore simulator
 *
 * Memory map:
 * 0x7000'0000 ... 0x7003'BFFF 240 KiByte RAM
 * 0x7003'A000 ... 0x7003'BFFF   8 KiByte for CSAs
 * 0x7003'9000 ... 0x7003'9FFF   4 KiByte for Stack
 * 0x8000'0000 ... 0x003F'FFFF   4 MiByte Flash ROM
 */

#include <stdlib.h>
#include <machine/intrinsics.h>


int main();


void __startup() __attribute__((used,noinline,noreturn)) ;
void __startup()
{
    /* Setup the context save area linked list. */
    unsigned int csa_addr  = 0x7003A000;
    unsigned int csa_end   = 0x7003C000;
    unsigned int next_pcxi = ((csa_addr & 0xF0000000) >> 12) | /* segment */
                             ((csa_addr & 0X003FFFC0) >> 6);   /* offset */

    _mtcr(0xFE38/*FCX*/, next_pcxi); /* store 1st PCXI value in FCX */

    while (csa_addr < csa_end) {
        next_pcxi++;
        *(unsigned int *)csa_addr = next_pcxi;
        csa_addr += 64;
    }
    *(unsigned int *)(csa_end - 64) = 0; /* mark end of CSA list */

    /* When the CSA that LCX points to is reached, a depletion trap is
       triggered. Therefore LCX points 2 CSA earlier than the end so
       that the trap can use the two remaining CSAs. */
    _mtcr(0xFE3C/*LCX*/, next_pcxi - 3);
    _dsync();

    exit(main());
}


void _start( void ) __attribute__((used,noinline)) ;
void _start(void)
{
    asm("movh.a   %a10, hi:(0x7003A000)           \n\t" \
        "lea      %a10, [%a10]lo:(0x7003A000)     \n\t" \
        "dsync                                    \n\t" \
        "movh.a   %a15,  hi:(__startup)           \n\t" \
        "lea      %a15, [%a15]lo:(__startup)      \n\t" \
        "ji %a15");
}

