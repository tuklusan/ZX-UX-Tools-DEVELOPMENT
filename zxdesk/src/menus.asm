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
        global MenuEnabled
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
        extern PrintDim
        extern WinApp
        extern AppNote
        extern WndCount
        extern WndZ
        extern WndRecAt
        extern AppAt
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
        xor a
        ld (MnPaintIndex),a
        ld a,(MnCount)
        ld b,a
MpItem:
        push bc
        ld hl,(MnItemPtr)
        ld a,(MnPaintIndex)
        add a,a
        ld e,a
        ld d,0
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        push hl
        xor a
        ld (PrintInv),a
        ld (PrintDim),a
        ld a,(MnPaintIndex)
        ld c,a
        ld a,(MenuOpen)
        ld b,a
        push hl
        call MenuEnabled
        pop hl
        or a
        jr nz,MpAvailable
        ld a,1
        ld (PrintDim),a
        jr MpNotSelected
MpAvailable:
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
        ld (PrintDim),a
        pop hl
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
; B=menu ID, C=item index. Returns A=1 if available, 0 if dimmed.
; The action dispatcher calls this again, so dimmed items never execute.
MenuEnabled:
        ld a,b
        cp 2
        jr z,MeFile
        cp 3
        jr z,MeView
        ld a,1
        ret
MeFile:
        ld a,c
        cp 3
        jp nc,MeNo          ; SAVE AS, PRINT, DELETE, LOAD unavailable
        cp 2
        jr z,MeSave
        or a
        jr z,MeNote
        ld a,4             ; FILE/OPEN launches Commander
        jp MeHasSlot
MeNote:
        xor a              ; FILE/NEW launches Notes
        jp MeHasSlot
MeSave:
        ld a,(WndCount)
        or a
        jr z,MeNo
        ld hl,(WinApp)
        ld de,AppNote
        or a
        sbc hl,de
        jr nz,MeNo
        ld a,1
        ret
MeView:
        ld a,c
        cp 5
        jr z,MeNo         ; DESKTOP not implemented
        cp 3
        jr nc,MeLayout
        or a
        jr z,MeCalendar
        cp 1
        jr z,MeClock
        ld a,6            ; CONSOLE
        jp MeHasSlot
MeCalendar:
        ld a,3
        jp MeHasSlot
MeClock:
        ld a,2
        jp MeHasSlot
MeLayout:
        ld a,(WndCount)
        cp 2
        jr c,MeNo
        ld a,1
        ret
; A=application kind. At four windows, only an existing app may open.
MeHasSlot:
        push af
        ld a,(WndCount)
        cp 4
        jr nc,MeFull
        pop af
        ld a,1
        ret
MeFull:
        pop af
        call AppAt
        ld (MeTarget),hl
        ld a,(WndCount)
        ld b,a
        ld hl,WndZ
MeScan:
        ld a,(hl)
        push bc
        push hl
        call WndRecAt
        ld de,6            ; WinApp field in the 11-byte record
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld hl,(MeTarget)
        or a
        sbc hl,de
        pop hl
        pop bc
        jr z,MeYes
        inc hl
        djnz MeScan
MeNo:
        xor a
        ret
MeYes:
        ld a,1
        ret
MenuAction:
        ld c,a
        ld a,(MnLastMenu)
        ld b,a
        push bc
        call MenuEnabled
        pop bc
        or a
        ret z
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
        dw MnPtrs1
        db 10,6,8,7
        dw MnPtrs2
        db 17,6,10,6
        dw MnPtrs3
        db 24,6,8,2
        dw MnPtrs4
MnPtrs1: dw MnAb, MnSettings
MnPtrs2: dw MnNew, MnOpen, MnSave, MnSaveAs, MnPrint, MnDelete, MnLoad
MnPtrs3: dw MnCalendar, MnClock, MnConsole, MnCascade, MnTile, MnDesktop
MnPtrs4: dw MnKeys, MnAbout
MnAb: db 'ABOUT',0
MnSettings: db 'SETTINGS',0
MnNew: db 'NEW',0
MnOpen: db 'OPEN',0
MnSave: db 'SAVE',0
MnSaveAs: db 'SAVE AS',0
MnPrint: db 'PRINT',0
MnDelete: db 'DELETE',0
MnLoad: db 'LOAD',0
MnCalendar: db 'CALENDAR',0
MnClock: db 'CLOCK',0
MnConsole: db 'CONSOLE',0
MnCascade: db 'CASCADE',0
MnTile: db 'TILE',0
MnDesktop: db 'DESKTOP',0
MnKeys: db 'KEYS',0
MnAbout: db 'ABOUT',0
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
        dw WndOpenCal
        db 3,1
        dw ClockOpen
        db 3,2
        dw TermOpen
        db 3,3
        dw WndCascade
        db 3,4
        dw WndTile
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
MeTarget: dw 0