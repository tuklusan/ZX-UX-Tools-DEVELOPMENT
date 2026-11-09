; ZXDesk original drop-down menu geometry and painter from menus.inc.
; Hardware pointer saving is replaced by ZX-UX-owned full redraw.
; Damian Cooper, MIT; see zxdesk/NOTICE.txt.
        section text
        global MenuOpenDrop
        global MenuPaint
        global MenuClose
        global MenuHitTitle
        global MenuItemAt
        global MenuOpen
        global MnCount
        global MnX
        global MnY
        global MnW
        global MnH
        extern DevFillRect
        extern FrX
        extern FrY
        extern FrW
        extern FrH
        extern FrPat
        extern AddrAt
        extern PxRow
        extern PrintInv
        extern PrintStrPx
MENUH equ 9
SCRCOLS equ 32
MNCOUNT equ 4
MNDEFSZ equ 6
MNITEMH equ 8
MenuHitTitle:
        ld hl,MenuDefs
        ld c,1
MhtLoop:
        ld a,c
        cp MNCOUNT+1
        jr nc,MhtNone
        ld a,(hl)
        cp b
        jr z,MhtIn
        jr nc,MhtNext
MhtIn:
        inc hl
        add a,(hl)
        dec hl
        cp b
        jr z,MhtNext
        jr c,MhtNext
        ld a,c
        ret
MhtNext:
        ld de,MNDEFSZ
        add hl,de
        inc c
        jr MhtLoop
MhtNone:
        xor a
        ret

; Original ZXDesk menu geometry, with pointer/save-under calls removed.
MenuOpenDrop:
        ld (MenuOpen),a
        dec a
        ld hl,MenuDefs
        or a
        jr z,MoGot
        ld b,a
        ld de,MNDEFSZ
MoSkip:
        add hl,de
        djnz MoSkip
MoGot:
        ld a,(hl)
        ld (MnX),a
        inc hl
        inc hl
        ld a,(hl)
        ld (MnW),a
        inc hl
        ld a,(hl)
        ld (MnCount),a
        add a,a
        add a,a
        add a,a
        add a,2
        ld (MnH),a
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (MnItemPtr),de
        ld a,MENUH
        ld (MnY),a
        ld a,(MnX)
        ld b,a
        ld a,(MnW)
        add a,b
        cp SCRCOLS+1
        jr c,MoFits
        ld a,(MnW)
        neg
        add a,SCRCOLS
        ld (MnX),a
MoFits:
        jp MenuPaint
MenuClose:
        xor a
        ld (MenuOpen),a
        ret
MenuItemAt:
        ld a,(MnY)
        inc a
        ld b,a
        ld a,c
        sub b
        jr c,MiaNone
        srl a
        srl a
        srl a
        ld b,a
        ld a,(MnCount)
        cp b
        jr z,MiaNone
        jr c,MiaNone
        ld a,b
        ret
MiaNone:
        ld a,$ff
        ret
MenuPaint:
        ld a,(MnX)
        ld (FrX),a
        ld a,(MnY)
        ld (FrY),a
        ld a,(MnW)
        ld (FrW),a
        ld a,(MnH)
        ld (FrH),a
        ld hl,$ffff
        ld (FrPat),hl
        call DevFillRect
        ld a,(MnY)
        inc a
        ld (FrY),a
        ld a,(MnH)
        sub 2
        ld (FrH),a
        ld hl,0
        ld (FrPat),hl
        call DevFillRect
        ld a,(MnY)
        inc a
        ld (PxRow),a
        ld a,(MnH)
        sub 2
        ld b,a
MpEdge:
        push bc
        ld a,(MnX)
        ld c,a
        ld a,(PxRow)
        call AddrAt
        ld a,(hl)
        or $80
        ld (hl),a
        ld a,(MnW)
        dec a
        ld e,a
        ld d,0
        add hl,de
        ld a,(hl)
        or $01
        ld (hl),a
        ld a,(PxRow)
        inc a
        ld (PxRow),a
        pop bc
        djnz MpEdge
        ld a,(MnY)
        inc a
        ld (PxRow),a
        ld hl,(MnItemPtr)
        ld a,(MnCount)
        ld b,a
MpItem:
        push bc
        push hl
        xor a
        ld (PrintInv),a
        ld a,(MnX)
        inc a
        ld c,a
        call PrintStrPx
        pop hl
MpSkip:
        ld a,(hl)
        inc hl
        or a
        jr nz,MpSkip
        ld a,(PxRow)
        add a,MNITEMH
        ld (PxRow),a
        pop bc
        djnz MpItem
        ret

        section data
MenuDefs:
        db 1,8,10,2
        dw MnItems1
        db 10,6,8,7
        dw MnItems2
        db 17,6,10,5
        dw MnItems3
        db 24,6,8,2
        dw MnItems4
MnItems1:
        db 'ABOUT',0,'SETTINGS',0
MnItems2:
        db 'NEW',0,'OPEN',0,'SAVE',0,'SAVE AS',0
        db 'PRINT',0,'DELETE',0,'LOAD',0
MnItems3:
        db 'CLOCK',0,'CALENDAR',0,'CASCADE',0,'TILE',0,'DESKTOP',0
MnItems4:
        db 'KEYS',0,'ABOUT',0
MenuOpen: db 0
MnX: db 0
MnY: db 0
MnW: db 0
MnH: db 0
MnCount: db 0
MnItemPtr: dw 0
