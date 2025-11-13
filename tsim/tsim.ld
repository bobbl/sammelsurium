OUTPUT_FORMAT("elf32-tricore")
OUTPUT_ARCH(tricore)

HEAP_SIZE    = 64k;

MEMORY
{
    data_scratchpad_ram (w!xp): org = 0x70000000, len = 240k
    program_flash_rom   (rx!p): org = 0x80000000, len = 4M
}

SECTIONS
{
    .heap : FLAGS(aw)
    {
        . = ALIGN(4);
        __HEAP = .;
        . += HEAP_SIZE;
        __HEAP_END = .;
    } > data_scratchpad_ram
}

