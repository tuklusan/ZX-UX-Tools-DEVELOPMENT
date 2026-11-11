; =====================================================================
; ZX-UX 48K Sinclair ZX Spectrum Unix.
; Copyright (c) 2026 Supratim Sanyal of SANYALnet Labs.
; Non-commercial use only under the repository LICENSE.
; Commercial use prohibited without separate written permission.
; =====================================================================

; ZX-UX boot-only cassette bootstrap.
; The cassette's 24 turbo blocks are received by the turbo loader of the 1985
; game Brian Bloodaxe (The Edge): its 256-byte routine, copied byte for byte
; from the REM line of that tape's second BASIC program and run at FF00h (see
; bloodaxe_loader.bin: code FF00-FFB3, "LD ERR" message FFB4-FFBA). Only three
; things in it are patched, all at run time below:
;   FF04  the end of its block table (it took two blocks, now 24),
;   FF07  its block count,
;   FF8C  the code after each block (POP HL, POP BC, then DEC B) becomes a jump
;         to part_done, which does the same and draws the progress row.
; A block is the data followed by one parity byte, so that the XOR of all of its
; bytes is zero. The loader reads straight into the final addresses, checks that
; parity, and on any error prints "LD ERR" and stops (there is no retry).
; Assembled from a staged copy with generated turbo_table.inc, turbo_lines.inc.
; This code D000..; the loader FF00.. and its stack FFFF; the image below D000.
;
        org 0D000h
LOADER  equ 0FF00h
COUNT   equ 24              ; the 24 blocks (turbo_segments.COUNT)
; start: Begin. The cassette is in charge.
start:  di
        ld sp,0CEFFh
        ld iy,05C3Ah
        xor a
        out (0FEh),a
; BASIC has just performed CLS and drawn the four ribbon cells; preserve its bitmap and attributes during
; all 24 progress rows.
        ld (row_index),a
; Show the heading before block 1. This leaves the final information line visible while block 24 is
; still loading.
        ld hl,progress_lines
        call render_text_row
        ld (text_cursor),hl
        ld a,1
        ld (row_index),a
        ld hl,loader_image
        ld de,LOADER
        ld bc,loader_end-loader_image
        ldir
        ld hl,block_table_end
        ld (LOADER+04h),hl
        ld a,COUNT
        ld (LOADER+07h),a
        ld a,0C3h                ; JP part_done in place of POP HL, POP BC, DEC B
        ld (LOADER+8Ch),a
        ld hl,part_done
        ld (LOADER+8Dh),hl
        jp LOADER

; part_done: the loader has read and checked a block. On the stack, as it left them: its table pointer, then
; its remaining block count (in B).
part_done:
        pop hl
        pop bc
        dec b
        jr z,all_loaded
        push bc
        push hl
; Blocks 1..23 verified: draw rows 2..24. Never delay the final handover to draw a line after block 24: it
; must already be visible while loading.
        ld hl,(text_cursor)
        call render_text_row
        ld (text_cursor),hl
        ld a,(row_index)
        inc a
        ld (row_index),a
        pop hl
        pop bc
        jp LOADER+08h            ; the loader's loop for the next block

all_loaded:
        ld iy,05C3Ah
        ei
        ld de,250
        ld hl,407
        call 03B5h
        ld b,25
.dwell: halt
        djnz .dwell
        xor a
        out (0FEh),a             ; black border at ZX-UX handover.
        ld (05C48h),a            ; BORDCR internal attribute must match black.
; The kernel clears the bitmap but not the attributes: give it the white-on-black screen it expects, not the
; banner's colours.
        ld hl,05800h
        ld de,05801h
        ld bc,002FFh
        ld (hl),7
        ldir
        jp 06000h

; render_text_row: 132 bytes. Draw one text line. The pixels get their jobs.
render_text_row:
; 4x8 font from the existing ZX-UX SDK (96 glyphs). Each 4-pixel character follows the previous one. Only
; the left half of the row is drawn (32 glyphs = 16 screen bytes) and only its 16 attribute cells are
; painted: the right half belongs to the banner the BASIC loader printed, and is never touched.
        push hl
        pop ix
        ld a,(row_index)
        ld l,a
        ld h,0
        add hl,hl
        ld de,video_rows
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (screen_pos),de
        ld c,16                  ; 16 screen bytes = 32 glyphs.
.pair:
        push bc
        ld a,(ix+0)
        inc ix
        call glyph_address
        push hl                  ; left glyph.
        ld a,(ix+0)
        inc ix
        call glyph_address
        ex de,hl                 ; right glyph.
        pop hl                   ; left glyph.
        ld b,4                   ; two scanlines per packed font byte.
.scan:
        ld a,(hl)
        and 0F0h
        ld c,a
        ld a,(de)
        rrca
        rrca
        rrca
        rrca
        and 00Fh
        or c
        push de
        ld de,(screen_pos)
        ld (de),a
        inc d                    ; ULA next pixel scanline.
        ld (screen_pos),de
        pop de
        ld a,(hl)
        and 00Fh
        rlca
        rlca
        rlca
        rlca
        ld c,a
        ld a,(de)
        and 00Fh
        or c
        push de
        ld de,(screen_pos)
        ld (de),a
        inc d
        ld (screen_pos),de
        pop de
        inc hl
        inc de
        djnz .scan
        ld de,(screen_pos)
        ld a,d
        sub 8
        ld d,a
        inc de
        ld (screen_pos),de
        pop bc
        dec c
        jr nz,.pair
; Paint only the 16 attribute cells of the left half.
        ld a,7
        call paint_attribute
        push ix
        pop hl
        ret

; glyph_address: 17 bytes. Find the font glyph. Every dot has a seat.
glyph_address:
        sub 32
        cp 96
        jr c,.ok
        xor a
.ok:    ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        ld bc,font4x8
        add hl,bc
        ret

; paint_attribute: 35 bytes. Color the cell. The border keeps its own rules.
paint_attribute:
        push af
        ld a,(row_index)
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,05800h
        add hl,de
        pop af
        ld b,16
.attr: ld (hl),a
        inc hl
        djnz .attr
        ret

row_index: db 0
screen_pos: dw 0
text_cursor: dw progress_lines
; video_rows: 48 bytes. Store the screen rows. A very small stage.
video_rows:
        dup 24, n
        dw 04000h + ((n / 8) * 0800h) + ((n % 8) * 32)
        edup
; loader_image: the Bloodaxe loader, unmodified here (it is patched after the copy to FF00h).
loader_image:
        incbin "bloodaxe_loader.bin"
loader_end:
; block_table: for each block the data length and the address it is read to (and two unused bytes), in
; the order the loader walks it: from the last entry back to the first, so block 1 is the last entry.
block_table:
        include "turbo_table.inc"
block_table_end:
        assert block_table_end-block_table == COUNT*6
; progress_lines: the progress text. The tape still has to finish.
progress_lines:
        include "turbo_lines.inc"
        align 4
; font4x8: 384 bytes. Four-by-eight font. Every pixel on salary.
font4x8:
        incbin "font4x8.bin",8,384
boot_end:
        assert boot_end < 0E000h
        assert LOADER+(loader_end-loader_image) <= 0FFB4h+7
