; Original ZXDesk control-table hit testing (src/hittest.inc), MIT.
; ZX-UX owns input; events feed pointer positions when supported.
        section text
        global HitTest
        global CtlSync
        extern MenuOpen
        extern MnX
        extern MnY
        extern MnW
        extern MnH
CTL_NONE equ 0
CTL_MENUBAR equ 4
CTL_DESKTOP equ 5
CTL_MENUDROP equ 6
CTLSIZE equ 5
SCRCOLS equ 32
MENUH equ 9
STATRULE equ 183
CtlSync:
        ld a,(MnX)
        ld (CtlDrop),a
        ld a,(MnY)
        ld (CtlDrop+1),a
        ld a,(MnW)
        ld (CtlDrop+2),a
        ld a,(MenuOpen)
        or a
        ld a,0
        jr z,CsShut
        ld a,(MnH)
CsShut:
        ld (CtlDrop+3),a
        ret
HitTest:
        call CtlSync
        ld hl,CtlTable
HtLoop:
        ld a,(hl)
        inc a
        jr z,HtMiss
        ld a,(hl)
        cp b
        jr z,HtXlo
        jr nc,HtNext
HtXlo:
        inc hl
        inc hl
        add a,(hl)
        dec hl
        dec hl
        cp b
        jr z,HtNext
        jr c,HtNext
        inc hl
        ld a,(hl)
        cp c
        jr z,HtYlo
        jr nc,HtNextDec
HtYlo:
        inc hl
        inc hl
        add a,(hl)
        dec hl
        dec hl
        cp c
        jr z,HtNextDec
        jr c,HtNextDec
        dec hl
        ld de,4
        add hl,de
        ld a,(hl)
        ret
HtNextDec:
        dec hl
HtNext:
        ld de,CTLSIZE
        add hl,de
        jr HtLoop
HtMiss:
        xor a
        ret
        section data
CtlTable:
CtlDrop: db 0,0,0,0,CTL_MENUDROP
CtlMenu: db 0,0,SCRCOLS,MENUH,CTL_MENUBAR
CtlDesk: db 0,MENUH,SCRCOLS,STATRULE-MENUH,CTL_DESKTOP
        db $ff
