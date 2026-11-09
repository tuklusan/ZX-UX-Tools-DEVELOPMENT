; Original ZXDesk screen-addressing routines from src/zxdesk.asm.
; Damian Cooper, MIT; see zxdesk/NOTICE.txt.
; ZX-UX holds screen ownership. No private ROM/IM2 or fixed code origin.
        section text
        global BuildScrTab
        global CalcScr
        global RowAddr
        global ScrDown
        global AddrAt

SCRROWS equ 192
SCRCOLS equ 32

BuildScrTab:
                ld      hl,ScrTab
                xor     a
                ld      (TmpY),a
BstLoop:
                ld      a,(TmpY)
                call    CalcScr
                ld      (hl),e
                inc     hl
                ld      (hl),d
                inc     hl
                ld      a,(TmpY)
                inc     a
                ld      (TmpY),a
                cp      SCRROWS
                jr      nz,BstLoop
                ret

; in: A = pixel row, out: DE = screen address of column 0
CalcScr:
                ld      d,a
                and     $07
                ld      e,a
                ld      a,d
                and     $38
                rlca
                rlca
                ld      c,a
                ld      a,d
                and     $c0
                rrca
                rrca
                rrca
                or      e
                or      $40
                ld      d,a
                ld      e,c
                ret

; in: A = pixel row, out: HL = screen address of column 0
RowAddr:
                ld      l,a
                ld      h,0
                add     hl,hl
                ld      de,ScrTab
                add     hl,de
                ld      e,(hl)
                inc     hl
                ld      d,(hl)
                ex      de,hl
                ret

; Step HL down one pixel row. Touches only A and HL.
ScrDown:
                inc     h
                ld      a,h
                and     7
                ret     nz
                ld      a,l
                add     a,SCRCOLS
                ld      l,a
                ret     c
                ld      a,h
                sub     8
                ld      h,a
                ret

; in: A = pixel row, C = byte column, out: HL = screen address
AddrAt:
                call    RowAddr
                ld      e,c
                ld      d,0
                add     hl,de
                ret

        section bss
ScrTab:         ds SCRROWS*2
TmpY:           ds 1
