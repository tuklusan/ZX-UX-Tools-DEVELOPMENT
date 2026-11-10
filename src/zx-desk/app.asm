; Original ZXDesk application descriptor interface from src/app.inc (12 bytes:
; init, draw, key, title, x, y, w, h).
; Damian Cooper, MIT. Each app owns one exact-size live state record.
        section text
        global AppAt
        global AppCall
        global AppTerm
        extern WinApp
        extern NoteInit
        extern NoteDrawInterior
        extern NoteKey
        extern WdAbout
        extern ClkDraw
        extern ClkKey
        extern CmdInit
        extern CmdDraw
        extern CmdKey
        extern TermInit
        extern TermDraw
        extern TermKey

APP_INIT equ 0
APP_DRAW equ 2
APP_KEY equ 4
APP_TITLE equ 6
APP_X equ 8
APP_Y equ 9
APP_W equ 10
APP_H equ 11
APPSIZE equ 12
APP_NOTE equ 0
APP_ABOUT equ 1
APP_CLOCK equ 2
APP_CMD equ 3
APP_TERM equ 4

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
        section data
 ; One descriptor per app. No duplicate state-copy metadata or unused callbacks.
AppTable:
        dw NoteInit,NoteDrawInterior,NoteKey,TxtWinTitle
        db 8,48,18,72
        dw 0,WdAbout,0,TxtAboutTitle
        db 10,44,21,92
        dw 0,ClkDraw,ClkKey,TxtClockTitle
        db 18,40,8,30
        dw CmdInit,CmdDraw,CmdKey,TxtCmdTitle
        db 1,24,30,112
AppTerm:
        dw TermInit,TermDraw,TermKey,TxtTermTitle
        db 11,48,20,72
TxtWinTitle: db 'NOTES',0
TxtAboutTitle: db 'ABOUT',0
TxtClockTitle: db 'CLOCK',0
TxtCmdTitle: db 'FILES',0
TxtTermTitle: db 'CONSOLE',0