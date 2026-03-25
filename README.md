# Chocofi ZMK Config

ZMK keymap for the [Chocofi](https://github.com/pashutk/chocofi) split keyboard with nice!nano v2 controllers and nice!view displays.

- **Layout**: Spanish-Catalan (macOS ISO)
- **Firmware**: [ZMK](https://zmk.dev)
- **Build**: GitHub Actions

## Cheatsheet

Interactive layer reference: **https://jsmont.github.io/zmk-config/**

## Flashing

Download the latest firmware from [Actions](../../actions), then:

1. Double-press reset on the left half to enter bootloader (appears as USB drive)
2. Copy `chocofi_left.uf2` to it
3. Repeat for the right half with `chocofi_right.uf2`
