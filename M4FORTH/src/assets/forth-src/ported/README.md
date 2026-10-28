# Ported programs

- `hufdemo.fth` — F83 Huffman bitstream port.  It substitutes a target-memory
  byte stream for the original CP/M file interface, encodes `BANANA_BANDANA`,
  then decodes and prints it. The five-symbol codebook is fixed so the sample
  remains small enough for the ZX-UX arena.
- `worms.fth` — six-turn console port of the MIT Worms? movement loop. Press
  `W`, `A`, `S`, or `D`; the board and head coordinates update after each turn.
