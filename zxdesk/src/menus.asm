; ZXDesk original drop-down menu geometry and painter from menus.inc.
; Hardware pointer saving is replaced by ZX-UX-owned full redraw.
; Damian Cooper, MIT; see zxdesk/NOTICE.txt.
        section text
        global MenuOpenDrop
        global MenuPaint
        global MenuClose
        global MenuOpen
        global MnCount
        global MnX
        global MnY
        global MnW
        global MnH
        global MenuAction
        global MnLastMenu
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
        extern WndOpen
        extern NoteMenuSave
        extern DlgOpen
        extern WndCascade
        extern WndTile
        extern MenuSel
MENUH equ 9
SCRCOLS equ 32
MNCOUNT equ 4
MNDEFSZ equ 6
MNITEMH equ 8
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
	jr MenuPaint
MenuClose:
        xor a
        ld (MenuOpen),a
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
        xor a
        ld (MnPaintIndex),a
        ld a,(MnCount)
        ld b,a
MpItem:
        push bc
        push hl
        xor a
        ld (PrintInv),a
        ld a,(MnPaintIndex)
        ld c,a
        ld a,(MenuSel)
        cp c
        jr nz,MpNotSelected
        ld a,1
        ld (PrintInv),a
MpNotSelected:
        ld a,(MnX)
        inc a
        ld c,a
        call PrintStrPx
        xor a
        ld (PrintInv),a
        pop hl
MpSkip:
        ld a,(hl)
        inc hl
        or a
        jr nz,MpSkip
        ld a,(PxRow)
        add a,MNITEMH
        ld (PxRow),a
        ld hl,MnPaintIndex
        inc (hl)
        pop bc
        djnz MpItem
        ret

; Original ZXDesk table-driven menu action dispatcher from menus.inc.
; The unsupported OS-dependent actions are not advertised as complete.
MenuAction:
        ld c,a
        ld a,(MnLastMenu)
        ld b,a
        ld hl,MnActions
MnaLoop:
        ld a,(hl)
        cp $ff
        ret z
        cp b
        jr nz,MnaNext
        inc hl
        ld a,(hl)
        cp c
        jr nz,MnaNext2
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        jp (hl)
MnaNext2:
        dec hl
MnaNext:
        ld de,4
        add hl,de
        jr MnaLoop
; Application opening uses the upstream ZXDesk indices (not menu IDs).
NoteMenuNew:
        xor a
        jp WndOpen
AboutOpen:
        ld a,1
        jp WndOpen
ClockOpen:
        ld a,2
        jp WndOpen
WndOpenCal:
        ld a,3
        jp WndOpen
CmdOpenWin:
        ld a,4
        jp WndOpen
KeysOpen:
        ld a,5
        jp WndOpen
TermOpen:
        ld a,6
        jp WndOpen

        section data
MenuDefs:
        db 1,8,10,2
        dw MnItems1
        db 10,6,8,7
        dw MnItems2
        db 17,6,10,6
        dw MnItems3
        db 24,6,8,2
        dw MnItems4
MnItems1:
        db 'ABOUT',0,'SETTINGS',0
MnItems2:
        db 'NEW',0,'OPEN',0,'SAVE',0,'SAVE AS',0
        db 'PRINT',0,'DELETE',0,'LOAD',0
MnItems3:
        db 'CLOCK',0,'CALENDAR',0,'CASCADE',0,'TILE',0,'DESKTOP',0,'CONSOLE',0
MnItems4:
        db 'KEYS',0,'ABOUT',0
; menu, item, routine. Original table format and supported actions.
MnActions:
        db 1,0
        dw AboutOpen
        db 1,1
        dw DlgOpen
        db 2,0
        dw NoteMenuNew
        db 2,1
        dw CmdOpenWin
        db 2,2
        dw NoteMenuSave
        db 3,0
        dw ClockOpen
        db 3,1
        dw WndOpenCal
        db 3,2
        dw WndCascade
        db 3,3
        dw WndTile
        db 3,5
        dw TermOpen
        db 4,0
        dw KeysOpen
        db 4,1
        dw AboutOpen
        db $ff
MnPaintIndex: db 0
MnLastMenu: db 0
MenuOpen: db 0
MnX: db 0
MnY: db 0
MnW: db 0
MnH: db 0
MnCount: db 0
MnItemPtr: dw 0