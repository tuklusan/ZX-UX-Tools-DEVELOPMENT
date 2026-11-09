; Original ZXDesk application descriptor interface from src/app.inc.
; Damian Cooper, MIT. Window state is owned by the SSX1 process.
        section text
        global AppAt
        global AppCall
        global AppSave
        global AppLoad
        global AppStateAt
        global AppNote
        global AppAbout
        global AppClock
        global AppCal
        global AppCmd
        global AppKeys
        extern WinApp
        extern WinStateP
        extern NoteState
        extern NoteInit
        extern NoteDrawInterior
        extern NoteKey
        extern WdAbout
        extern ClkDraw
        extern ClkKey
        extern CalState
        extern CalInit
        extern CalDraw
        extern CalKey
        extern CmdState
        extern CmdInit
        extern CmdDraw
        extern CmdKey
        extern KeysDraw

APP_STSZ equ 0
APP_LIVE equ 2
APP_INIT equ 4
APP_DRAW equ 6
APP_KEY equ 8
APP_TITLE equ 10
APP_X equ 12
APP_Y equ 13
APP_W equ 14
APP_H equ 15
APP_CLOSE equ 16
APP_SCROLL equ 18
APP_SCROLLTO equ 20
APP_TICK equ 22
APPSIZE equ 24
APP_NOTE equ 0
APP_ABOUT equ 1
APP_CLOCK equ 2
APP_CAL equ 3
APP_CMD equ 4
APP_KEYS equ 5

; Original ZXDesk AppAt / AppCall / state swapping routines.
AppAt:
        ld hl,AppTable
        or a
        ret z
        ld b,a
        ld de,APPSIZE
AppAtLoop:
        add hl,de
        djnz AppAtLoop
        ret
AppCall:
        push af
        ld hl,(WinApp)
        ld a,h
        or l
        jr z,AcNone
        ld e,c
        ld d,0
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld a,d
        or e
        jr z,AcNone
        pop af
        ex de,hl
        jp (hl)
AcNone:
        pop af
        ret
AppSave:
        call AppStateAt
        ret z
        ldir
        ret
AppLoad:
        call AppStateAt
        ret z
        ex de,hl
        ldir
        ret
AppStateAt:
        ld hl,(WinApp)
        ld a,h
        or l
        ret z
        ld c,(hl)
        inc hl
        ld b,(hl)
        inc hl
        ld a,b
        or c
        ret z
        ld e,(hl)
        inc hl
        ld d,(hl)
        push de
        ld de,(WinStateP)
        ld a,d
        or e
        pop hl
        ret

        section data
; Original 24-byte ZXDesk descriptor layout. Size and location of the
; per-window state are unchanged; the allocator is ZX-UX process local.
AppTable:
AppNote:
        dw 273,NoteState,NoteInit,NoteDrawInterior,NoteKey,TxtWinTitle
        db 8,48,18,72
        dw 0,0,0,0
AppAbout:
        dw 0,0,0,WdAbout,0,TxtAboutTitle
        db 14,92,15,52
        dw 0,0,0,0
AppClock:
        dw 0,0,0,ClkDraw,ClkKey,TxtClockTitle
        db 18,40,8,30
        dw 0,0,0,0
AppCal:
        dw 3,CalState,CalInit,CalDraw,CalKey,TxtCalTitle
        db 4,32,23,82
        dw 0,0,0,0
AppCmd:
        dw 5,CmdState,CmdInit,CmdDraw,CmdKey,TxtCmdTitle
        db 1,24,30,112
        dw 0,0,0,0
AppKeys:
        dw 0,0,0,KeysDraw,0,TxtKeysTitle
        db 14,20,17,100
        dw 0,0,0,0
TxtWinTitle: db 'NOTES',0
TxtAboutTitle: db 'ABOUT',0
TxtClockTitle: db 'CLOCK',0
TxtCalTitle: db 'CALENDAR',0
TxtCmdTitle: db 'FILES',0
TxtKeysTitle: db 'KEYS',0
