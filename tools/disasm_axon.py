#!/usr/bin/env python3
"""Disassemble selected AArch64 functions from libaxon3d.so with symbol labels."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, Cs
from capstone.arm64 import ARM64_OP_IMM
from cxxfilt import demangle
from elftools.elf.elffile import ELFFile


def load_elf(path: Path):
    stream = path.open("rb")
    elf = ELFFile(stream)
    symbols: dict[int, tuple[str, int]] = {}
    names: dict[str, tuple[int, int]] = {}
    for section_name in (".symtab", ".dynsym"):
        section = elf.get_section_by_name(section_name)
        if section is None:
            continue
        for symbol in section.iter_symbols():
            address = int(symbol.entry.st_value)
            size = int(symbol.entry.st_size)
            if not address or not symbol.name:
                continue
            try:
                display_name = demangle(symbol.name)
            except Exception:
                display_name = symbol.name
            symbols.setdefault(address, (display_name, size))
            names.setdefault(display_name, (address, size))
            names.setdefault(symbol.name, (address, size))
    plt = elf.get_section_by_name(".plt")
    relocations = elf.get_section_by_name(".rela.plt")
    dynamic_symbols = elf.get_section_by_name(".dynsym")
    if plt is not None and relocations is not None and dynamic_symbols is not None:
        # AArch64 ELF PLT uses a 32-byte resolver header and 16-byte entries.
        entry_address = int(plt["sh_addr"]) + 32
        for index, relocation in enumerate(relocations.iter_relocations()):
            symbol = dynamic_symbols.get_symbol(relocation.entry.r_info_sym)
            name = symbol.name
            try:
                display_name = demangle(name)
            except Exception:
                display_name = name
            symbols.setdefault(entry_address + index * 16, (f"{display_name}@plt", 16))
    return stream, elf, symbols, names


def virtual_bytes(elf: ELFFile, address: int, size: int) -> bytes:
    for segment in elf.iter_segments():
        start = int(segment["p_vaddr"])
        end = start + int(segment["p_filesz"])
        if start <= address and address + size <= end:
            offset = int(segment["p_offset"]) + address - start
            elf.stream.seek(offset)
            return elf.stream.read(size)
    raise ValueError(f"address range 0x{address:x}+0x{size:x} is not file-backed")


def nearest_symbol(symbols: dict[int, tuple[str, int]], address: int) -> str | None:
    addresses = sorted(symbols)
    index = bisect_right(addresses, address) - 1
    if index < 0:
        return None
    base = addresses[index]
    name, size = symbols[base]
    if address == base:
        return name
    if size and address < base + size:
        return f"{name}+0x{address - base:x}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", type=Path)
    parser.add_argument("functions", nargs="+", help="mangled or demangled function names")
    args = parser.parse_args()

    stream, elf, symbols, names = load_elf(args.library)
    disassembler = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    disassembler.detail = True

    try:
        for requested in args.functions:
            match = names.get(requested)
            if match is None:
                candidates = sorted(name for name in names if requested in name)
                if len(candidates) != 1:
                    print(f"Could not uniquely resolve {requested!r}")
                    for candidate in candidates[:20]:
                        print(f"  {candidate}")
                    continue
                requested = candidates[0]
                match = names[requested]
            address, size = match
            print(f"\n## {requested} @ 0x{address:x} ({size} bytes)")
            code = virtual_bytes(elf, address, size)
            for instruction in disassembler.disasm(code, address):
                suffix = ""
                if instruction.mnemonic in {"b", "bl"} and instruction.operands:
                    operand = instruction.operands[0]
                    if operand.type == ARM64_OP_IMM:
                        label = nearest_symbol(symbols, int(operand.imm))
                        if label:
                            suffix = f"  ; {label}"
                print(
                    f"0x{instruction.address:08x}: "
                    f"{instruction.mnemonic:<8} {instruction.op_str}{suffix}"
                )
    finally:
        stream.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
