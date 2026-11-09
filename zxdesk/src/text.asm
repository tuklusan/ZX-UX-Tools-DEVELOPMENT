; Original ZXDesk PrintChar from upstream src/zxdesk.asm.
; Damian Cooper, MIT; see zxdesk/NOTICE.txt.
; ROM character font is an outstanding platform dependency.
        section text
        global PrintChar
        global PrintCharPx
        global PrintStrPx
        global PrintInv
        global PxRow
        extern AddrAt
        extern ScrDown
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

; Original ZXDesk pixel-row text entry points.
; A=character, C=column, PxRow=pixel row.
PrintCharPx:
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,CHARSET
        add hl,de
        push hl
        ld a,(PxRow)
        call AddrAt
        pop de
        ld b,8
PcpRow:
        ld a,(de)
        ld c,a
        ld a,(PrintInv)
        or a
        jr z,PcpNorm
        ld a,c
        cpl
        ld c,a
PcpNorm:
        ld a,c
        ld (hl),a
        inc de
        call ScrDown
        djnz PcpRow
        ret

; Original ZXDesk string loop with pixel-accurate line placement.
PrintStrPx:
        ld a,(hl)
        or a
        ret z
        push hl
        push bc
        call PrintCharPx
        pop bc
        pop hl
        inc hl
        inc c
        jr PrintStrPx

        section data
PrintInv: db 0
PxRow: db 0