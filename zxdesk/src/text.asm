; Original ZXDesk PrintChar from upstream src/zxdesk.asm.
; Damian Cooper, MIT; see zxdesk/NOTICE.txt.
; ROM character font is an outstanding platform dependency.
        section text
        global PrintChar
        extern AddrAt
CHARSET equ $3c00

; in: A = char code, B = char row, C = char column
PrintChar:
                ld      l,a
                ld      h,0
                add     hl,hl
                add     hl,hl
                add     hl,hl
                ld      de,CHARSET
                add     hl,de
                push    hl
                ld      a,b
                add     a,a
                add     a,a
                add     a,a
                call    AddrAt
                pop     de
                ld      b,8
PcRow:
                ld      a,(de)
                ld      (hl),a
                inc     de
                inc     h
                djnz    PcRow
                ret