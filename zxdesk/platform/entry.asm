; ZX-UX SSX1 process lifecycle, keyboard and event adapter for original ZXDesk.
; This is not a separate desktop, ROM or operating system.
        section text
        global start
        global DrawDesktop
        extern zx_syscall
        extern BuildScrTab
        extern EvPost
        extern EvNext
        extern DskInit
        extern DskPaintAll
        extern ClkInit
        extern ClkService
        extern WndInit
        extern WndOpen
        extern WndClose
        extern WndRepaintAll
        extern WndFocusTo
        extern WndCur
        extern WndCount
        extern WndZ
        extern WinX
        extern WinY
        extern WndFlush
        extern MenuOpen
        extern MenuOpenDrop
        extern MenuClose
        extern MenuPaint
        extern MnCount
        extern FillRowSolid
        extern PrintStrPx
        extern PxRow
        extern PrintInv
        extern AppCall
        extern ApiStSelect
        extern ApiStIdent
        extern CalNextDay

SCREEN equ $4000
ATTRS equ $5800
APP_KEY equ 8

start:
        ld hl,0
        ld de,oldtty
        ld a,32
        call zx_syscall
        jp c,done
        ld hl,0
        ld de,rawtty
        ld a,31
        call zx_syscall
        jp c,done
        ld hl,1
        ld a,39
        call zx_syscall
        jp c,restore
        ld a,1
        ld (owned),a
        ld a,e
        or a
        jp nz,release
        call BuildScrTab
        call DskInit
        call ClkInit
        call WndInit
        xor a
        call WndOpen
mainloop:
        ld hl,0
        ld de,key
        ld bc,1
        ld a,3
        call zx_syscall
        jp c,release
        ld a,h
        or l
        jp z,release
        call ClkService
        ld a,(key)
        ld b,a
        ld c,0
        ld a,4
        call EvPost
        call EvNext
        cp 4
        jr nz,mainloop
        ld a,b
        cp 7
        jp z,close_key
        cp 'q'
        jp z,quit_key
        cp 'Q'
        jp z,quit_key
        cp 'm'
        jp z,menu_key
        cp 'M'
        jp z,menu_key
        cp 6
        jp z,next_window
        ld b,a
        ld a,(MenuOpen)
        or a
        jp nz,menu_dispatch
        ld a,(WndCount)
        or a
        jr z,desktop_key
        ; Each window's key goes to its original application vector.
        ld a,b
        ld c,APP_KEY
        call AppCall
        jp repaint

desktop_key:
        ld a,b
        cp '1'
        jr nz,Dk2
        xor a
        jp open_key
Dk2:
        cp '2'
        jr nz,Dk3
        ld a,2
        jp open_key
Dk3:
        cp '3'
        jr nz,Dk4
        ld a,3
        jp open_key
Dk4:
        cp '4'
        jr nz,Dk5
        ld a,4
        jp open_key
Dk5:
        cp '5'
        jr nz,Dk6
        ld a,1
        jp open_key
Dk6:
        cp '6'
        jp nz,mainloop
        ld a,5
open_key:
        call WndOpen
        jp repaint
next_window:
        ld a,(WndCount)
        cp 2
        jp c,mainloop
        ld a,(WndZ+1)
        call WndFocusTo
        jp repaint
close_key:
        call MenuClose
        call WndClose
        jp repaint
quit_key:
        ld a,(WndCount)
        or a
        jp z,release
        ; q is part of a document while a window has focus.
        ld a,'q'
        ld c,APP_KEY
        call AppCall
        jp repaint
menu_dispatch:
        ld a,b
        cp 8
        jr z,menu_previous
        cp 9
        jr z,menu_next
        cp 13
        jr z,menu_choose
        jp mainloop
menu_previous:
        ld a,(MenuSel)
        or a
        jp z,mainloop
        dec a
        ld (MenuSel),a
        jp repaint
menu_next:
        ld a,(MenuSel)
        inc a
        ld b,a
        ld a,(MnCount)
        cp b
        jp z,mainloop
        jp c,mainloop
        ld a,b
        ld (MenuSel),a
        jp repaint
menu_choose:
        ld a,(MenuOpen)
        ld b,a
        ld a,(MenuSel)
        ld c,a
        call MenuClose
        ld a,b
        cp 1
        jr nz,McFile
        ld a,c
        or a
        jp z,open_about
        jp repaint
McFile:
        cp 2
        jr nz,McView
        ld a,c
        or a
        jp z,open_note
        cp 1
        jp z,open_files
        jp repaint
McView:
        cp 3
        jr nz,McHelp
        ld a,c
        or a
        jp z,open_clock
        cp 1
        jp z,open_calendar
        jp repaint
McHelp:
        ld a,c
        or a
        jp z,open_keys
open_about:
        ld a,1
        jp open_key
open_note:
        xor a
        jp open_key
open_clock:
        ld a,2
        jp open_key
open_calendar:
        ld a,3
        jp open_key
open_files:
        ld a,4
        jp open_key
open_keys:
        ld a,5
        jp open_key
menu_key:
        ld a,(MenuOpen)
        or a
        jr z,MkFirst
        inc a
        cp 5
        jr c,MkOpen
MkFirst:
        ld a,1
MkOpen:
        xor a
        ld (MenuSel),a
        ld a,(MenuOpen)
        or a
        jr z,MkZero
        inc a
        cp 5
        jr c,MkSet
MkZero:
        ld a,1
MkSet:
        call MenuOpenDrop
        jp repaint
repaint:
        call WndRepaintAll
        ld a,(MenuOpen)
        or a
        call nz,MenuPaint
        jp mainloop

release:
        ld a,(owned)
        or a
        jr z,restore
        ld hl,0
        ld a,39
        call zx_syscall
restore:
        ld hl,0
        ld de,oldtty
        ld a,31
        call zx_syscall
done:
        ld hl,0
        ld a,1
        call zx_syscall
        ret

; ZXDesk bitmap desktop under ZX-UX's claimed Spectrum screen.
DrawDesktop:
        ld hl,SCREEN
        ld de,SCREEN+1
        ld bc,6143
        ld (hl),0
        ldir
        ld hl,ATTRS
        ld de,ATTRS+1
        ld bc,767
        ld (hl),$78
        ldir
        xor a
        ld (PrintInv),a
        ld a,1
        ld (PxRow),a
        ld c,1
        ld hl,TxtMenu
        call PrintStrPx
        ld a,8
        call FillRowSolid
        ld a,183
        call FillRowSolid
        call DskPaintAll
        ld a,185
        ld (PxRow),a
        ld c,1
        ld hl,TxtStatus
        jp PrintStrPx

        section data
rawtty: db 0,0,0,0,$a0,0
owned: db 0
MenuSel: db 0
key: db 0
TxtMenu: db 'ZX DESK   FILE   VIEW   HELP',0
TxtStatus: db 'ZX-UX / ZXDESK',0
        section bss
oldtty: ds 6
