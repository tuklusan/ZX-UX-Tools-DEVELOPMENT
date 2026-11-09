; Original ZXDesk desktop painting routines and four original bitmap
; shapes from upstream src/desktop.inc. Damian Cooper, MIT.
; The original desktop owns its image and labels; ZX-UX owns hardware.
        section text
        global DskInit
        global DskPaintAll
        global DskPaintOne
        global DskShapeAt
        global DskBlitShape
        global DskHit
        global DskSelected
        extern AddrAt
        extern PrintStrPx
        extern PrintInv
        extern PxRow
        extern SetJoyEnabled
DSKMAX equ 7
DSKENTSZ equ 8
DSKBITMAP equ 7
DSKLABEL equ 3
DSKICONH equ 16
DSKICONW equ 2
DSKSLOTH equ 25
DSKLABELY equ 17

DskInit:
        ld hl,DskDefault
        ld de,DskTab
        ld bc,DSKMAX*DSKENTSZ
        ldir
        xor a
        ld (DskSelected),a
        ret

DskEntry:
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,DskTab
        add hl,de
        ret

DskPaintAll:
        xor a
        ld (DskIx),a
DpaLoop:
        ld a,(DskIx)
        call DskEntry
        ld a,(hl)
        or a
        call nz,DskPaintOne
        ld hl,DskIx
        inc (hl)
        ld a,(hl)
        cp DSKMAX
        jr c,DpaLoop
        ret

DskPaintOne:
        push hl
        inc hl
        ld a,(hl)
        ld (DskPx),a
        inc hl
        ld a,(hl)
        ld (DskPy),a
        pop hl
        push hl
        ld de,DSKBITMAP
        add hl,de
        ld a,(hl)
        call DskShapeAt
        ld a,(DskPx)
        ld c,a
        ld a,(DskPy)
        call DskBlitShape
        pop hl
        push hl
        ld de,DSKLABEL
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        push hl
        call DskStrLen
        srl a
        ld b,a
        ld a,(DskPx)
        inc a
        sub b
        jr nc,DskLabX
        xor a
DskLabX:
        ld c,a
        ld a,(DskPy)
        add a,DSKLABELY
        ld (PxRow),a
        pop hl
        xor a
        ld (PrintInv),a
        ld a,(SetJoyEnabled)
        or a
        jr z,DskPrintLabel
        ld a,(DskIx)
        ld b,a
        ld a,(DskSelected)
        cp b
        jr nz,DskPrintLabel
        ld a,1
        ld (PrintInv),a
DskPrintLabel:
        call PrintStrPx
        xor a
        ld (PrintInv),a
        pop hl
        ret
DskStrLen:
        ld b,0
DslLoop:
        ld a,(hl)
        or a
        jr z,DslDone
        inc hl
        inc b
        jr DslLoop
DslDone:
        ld a,b
        ret

DskShapeAt:
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,DskShapes
        add hl,de
        ret
DskBlitShape:
        ld (DskShp),hl
        ld (DskRow),a
        ld a,c
        ld (DskCol),a
        ld b,DSKICONH
DbsRow:
        push bc
        ld a,(DskCol)
        ld c,a
        ld a,(DskRow)
        call AddrAt
        ex de,hl
        ld hl,(DskShp)
        ld a,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld (DskShp),hl
        ex de,hl
        ld (hl),a
        inc hl
        ld (hl),c
        ld hl,DskRow
        inc (hl)
        pop bc
        djnz DbsRow
        ret

 ; Original ZXDesk desktop icon hit-testing.
DskHit:
        ld a,b
        ld (DskHx),a
        ld a,c
        ld (DskHy),a
        xor a
        ld (DskIx),a
DhLoop:
        ld a,(DskIx)
        call DskEntry
        ld a,(hl)
        or a
        jr z,DhNext
        inc hl
        ld a,(hl)
        ld b,a
        inc hl
        ld c,(hl)
        ld a,(DskHx)
        sub b
        jr c,DhNext
        cp DSKICONW
        jr nc,DhNext
        ld a,(DskHy)
        sub c
        jr c,DhNext
        cp DSKSLOTH
        jr nc,DhNext
        ld a,(DskIx)
        inc a
        ret
DhNext:
        ld hl,DskIx
        inc (hl)
        ld a,(hl)
        cp DSKMAX
        jr c,DhLoop
        xor a
        ret

        section data
DskDefault:
        db 1,1,16
        dw TxtDskNote,0
        db 0
        db 1,1,48
        dw TxtDskClock,0
        db 1
        db 1,1,80
        dw TxtDskCal,0
        db 2
        db 1,1,112
        dw TxtDskFiles,0
        db 3
        db 1,1,144
        dw TxtDskAbout,0
        db 0
        db 1,4,144
        dw TxtDskSet,0
        db 0
        db 1,9,16
        dw TxtDskTerm,0
        db 3
TxtDskNote: db 'NOTE',0
TxtDskClock: db 'CLOCK',0
TxtDskCal: db 'CAL',0
TxtDskFiles: db 'FILES',0
TxtDskAbout: db 'ABOUT',0
TxtDskSet: db 'SETUP',0
TxtDskTerm: db 'CONSOLE',0
DskShapes:
        db $FF,$FF,$80,$01,$80,$01,$BF,$FD
        db $80,$01,$80,$01,$BF,$FD,$80,$01
        db $80,$01,$BF,$FD,$80,$01,$80,$01
        db $BF,$FD,$80,$01,$80,$01,$FF,$FF
        db $FF,$FF,$80,$01,$80,$01,$80,$01
        db $81,$01,$81,$01,$81,$01,$81,$01
        db $81,$F9,$80,$01,$80,$01,$80,$01
        db $80,$01,$80,$01,$80,$01,$FF,$FF
        db $FF,$FF,$FF,$FF,$FF,$FF,$80,$01
        db $91,$11,$80,$01,$80,$01,$91,$11
        db $80,$01,$80,$01,$91,$11,$80,$01
        db $80,$01,$80,$01,$80,$01,$FF,$FF
        db $FF,$FF,$80,$01,$80,$01,$80,$01
        db $80,$01,$80,$01,$80,$01,$FF,$FF
        db $80,$01,$83,$C1,$80,$01,$80,$01
        db $80,$01,$80,$01,$80,$01,$FF,$FF
DskSelected: db 0
DskIx: db 0
DskPx: db 0
DskPy: db 0
DskRow: db 0
DskCol: db 0
DskShp: dw 0
DskHx: db 0
DskHy: db 0
        section bss
DskTab: ds DSKMAX*DSKENTSZ
