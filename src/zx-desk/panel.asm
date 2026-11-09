; ZXDesk D2 panel record, drawing and keyboard control from src/panel.inc.
; Damian Cooper (MIT); save-under and pointer calls become full redraws.
        section text
        global PnlPaint
        global PnlKey
        global PnlRowPaint
        global PnlX
        global PnlY
        global PnlW
        global PnlH
        global PnlRow0
        global PnlRows
        global PnlTab
        global PnlTitle
        global PnlAfter
        global PnlFocus
        global PnlPush
        global PnlPop
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
PT_ACTION equ 1
PT_CYCLE equ 2
PTSIZE equ 8
PNLMARGIN equ $30
PNLROWH equ 8
PnlRowAddr:
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,(PnlTab)
        add hl,de
        ret
PnlRowY:
        add a,a
        add a,a
        add a,a
        ld hl,PnlRow0
        add a,(hl)
        ret
PnlStrLen:
        push hl
        ld b,0
PslLoop:
        ld a,(hl)
        or a
        jr z,PslDone
        inc hl
        inc b
        jr PslLoop
PslDone:
        ld a,b
        pop hl
        ret
PnlValue:
        call PnlRowAddr
        ld a,(hl)
        cp PT_CYCLE
        jr z,PnvCycle
        ld hl,0
        ret
PnvCycle:
        push hl
        inc hl
        inc hl
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld a,(de)
        pop hl
        push af
        ld de,6
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        pop af
        add a,a
        ld l,a
        ld h,0
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        ret
PnlRowPaint:
        ld (PnlIdx),a
        call PnlRowY
        ld (FrY),a
        ld a,(PnlX)
        inc a
        ld (FrX),a
        ld a,(PnlW)
        sub 2
        ld (FrW),a
        ld a,PNLROWH
        ld (FrH),a
        ld hl,0
        ld (FrPat),hl
        call DevFillRect
        ld a,(PnlIdx)
        ld hl,PnlFocus
        cp (hl)
        jr nz,PrpLabel
        call PnlRowY
        ld (PxRow),a
        ld b,PNLROWH
PrpBar:
        push bc
        ld a,(PnlX)
        ld c,a
        ld a,(PxRow)
        call AddrAt
        ld a,(hl)
        or PNLMARGIN
        ld (hl),a
        ld a,(PxRow)
        inc a
        ld (PxRow),a
        pop bc
        djnz PrpBar
PrpLabel:
        ld a,(PnlIdx)
        call PnlRowY
        ld (PxRow),a
        ld a,(PnlIdx)
        call PnlRowAddr
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld a,d
        or e
        jr z,PrpValue
        ex de,hl
        ld a,(PnlX)
        inc a
        ld c,a
        call PrintStrPx
PrpValue:
        ld a,(PnlIdx)
        call PnlValue
        ld a,h
        or l
        ret z
        push hl
        call PnlStrLen
        ld (PnlLen),a
        ld a,(PnlX)
        ld hl,PnlW
        add a,(hl)
        dec a
        ld hl,PnlLen
        sub (hl)
        ld c,a
        ld a,(PnlIdx)
        call PnlRowY
        ld (PxRow),a
        pop hl
        jp PrintStrPx
PnlPaint:
        ld a,(PnlX)
        ld (FrX),a
        ld a,(PnlY)
        ld (FrY),a
        ld a,(PnlW)
        ld (FrW),a
        ld a,(PnlH)
        ld (FrH),a
        ld hl,$ffff
        ld (FrPat),hl
        call DevFillRect
        ld a,(PnlY)
        add a,9
        ld (FrY),a
        ld (PxRow),a
        ld a,(PnlH)
        sub 10
        ld (FrH),a
        ld b,a
        ld hl,0
        ld (FrPat),hl
        push bc
        call DevFillRect
        pop bc
PnpEdge:
        push bc
        ld a,(PnlX)
        ld c,a
        ld a,(PxRow)
        call AddrAt
        ld a,(hl)
        or $80
        ld (hl),a
        ld a,(PnlW)
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
        djnz PnpEdge
        ld a,1
        ld (PrintInv),a
        ld a,(PnlY)
        inc a
        ld (PxRow),a
        ld a,(PnlX)
        inc a
        ld c,a
        ld hl,(PnlTitle)
        call PrintStrPx
        xor a
        ld (PrintInv),a
        xor a
PnpRow:
        push af
        call PnlRowPaint
        pop af
        inc a
        ld hl,PnlRows
        cp (hl)
        jr c,PnpRow
        ret
PnlActivate:
        ld (PnlIdx),a
        call PnlRowAddr
        ld a,(hl)
        cp PT_CYCLE
        jr z,PnaCycle
        cp PT_ACTION
        ret nz
        inc hl
        inc hl
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld hl,PnaDone
        push hl
        ex de,hl
        jp (hl)
PnaCycle:
        push hl
        inc hl
        inc hl
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        ld a,(de)
        inc a
        cp c
        jr c,PnaStore
        xor a
PnaStore:
        ld (de),a
        pop hl
PnaDone:
        ld hl,(PnlAfter)
        ld a,h
        or l
        ret z
        ld a,(PnlIdx)
        jp (hl)
PnlKey:
        cp 8
        jr z,PnkCycle
        cp 9
        jr z,PnkCycle
        cp 11
        jr z,PnkUp
        cp 10
        jr z,PnkDown
        cp 13
        jr z,PnkEnter
        ret
PnkCycle:
        ld a,(PnlFocus)
        call PnlRowAddr
        ld a,(hl)
        cp PT_CYCLE
        ret nz
        ld a,(PnlFocus)
	jr PnlActivate
PnkUp:
        ld a,(PnlFocus)
        or a
        ret z
        dec a
        ld (PnlFocus),a
        jp PnlPaint
PnkDown:
        ld a,(PnlFocus)
        inc a
        ld hl,PnlRows
        cp (hl)
        ret nc
        ld (PnlFocus),a
        jp PnlPaint
PnkEnter:
        ld a,(PnlFocus)
	jr PnlActivate
 ; Original ZXDesk D3 nested-panel record swap.
PNLRECSZ equ 13
PNLDEPTH equ 3
PnlPush:
        ld a,(PnlRecDep)
        cp PNLDEPTH
        jr nc,PnlStkErr
        call PnlRecSlot
        ex de,hl
        ld hl,PnlX
        ld bc,PNLRECSZ
        ldir
        ld hl,PnlRecDep
        inc (hl)
        or a
        ret
PnlPop:
        ld a,(PnlRecDep)
        or a
        jr z,PnlStkErr
        dec a
        ld (PnlRecDep),a
        call PnlRecSlot
        ld de,PnlX
        ld bc,PNLRECSZ
        ldir
        or a
        ret
PnlStkErr:
        scf
        ret
PnlRecSlot:
        ld l,a
        ld h,0
        ld de,PNLRECSZ
        ld b,a
        ld hl,PnlRecStk
        or a
        ret z
PrsLoop:
        add hl,de
        djnz PrsLoop
        ret
        section data
PnlX: db 0
PnlY: db 0
PnlW: db 0
PnlH: db 0
PnlRow0: db 0
PnlRows: db 0
PnlTab: dw 0
PnlTitle: dw 0
PnlAfter: dw 0
PnlFocus: db 0
PnlIdx: db 0
PnlLen: db 0
PnlRecDep: db 0
        section bss
PnlRecStk: ds PNLDEPTH*PNLRECSZ