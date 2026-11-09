; ZX-UX SSX1 process lifecycle, keyboard and event adapter for original ZXDesk.
; This is not a separate desktop, ROM or operating system.
        section text
        global start
        global DrawDesktop
        global MenuSel
        extern zx_syscall
        extern BuildScrTab
        extern DskInit
        extern DskPaintAll
        extern DskSelected
        extern AppNote
        extern AppTerm
        extern WinApp
        extern SetJoyEnabled
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
        extern MenuAction
        extern MnLastMenu
        extern MnCount
        extern FillRowSolid
        extern PrintStrPx
        extern PxRow
        extern PrintInv
        extern AppCall
        extern ApiStSelect
        extern ApiStIdent
        extern CalNextDay
        extern SetDefaults
        extern SetLoad
        extern SetApply
        extern SetLattice
        extern DlgUp
        extern DlgClose
        extern DlgKey
        extern DgEscape
        extern RowAddr

SCREEN equ $4000
ATTRS equ $5800
APP_KEY equ 4

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
        call SetDefaults
        call SetLoad
        call SetApply
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
        call JoyTranslate
        ld a,(DlgUp)
        or a
        jp nz,modal_dispatch
        ld a,b
        cp 7
        jp z,close_key
        cp 'q'
        jp z,quit_key
        cp 'Q'
        jp z,quit_key
        cp 'M'
        jp z,menu_key
        cp 'm'
        jr nz,normal_key
        ; Lowercase m is text inside Note and Console. Uppercase M
        ; remains the explicit menu shortcut when editing text.
        ld a,(WndCount)
        or a
        jp z,menu_key
        ld hl,(WinApp)
        ld de,AppNote
        or a
        sbc hl,de
        jr z,normal_key
        ld hl,(WinApp)
        ld de,AppTerm
        or a
        sbc hl,de
        jr z,normal_key
        jp menu_key
normal_key:
        ld a,b
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
        ld a,(SetJoyEnabled)
        or a
        jr z,desktop_keys
        ld a,b
        cp '0'
        jp z,JoyActivate
        cp '6'
        jp z,JoyPrevious
        cp '9'
        jp z,JoyPrevious
        cp '7'
        jp z,JoyNext
        cp '8'
        jp z,JoyNext
desktop_keys:
        ld a,b
        cp '1'
        jr nz,Dk2
        xor a
	jr open_key
Dk2:
        cp '2'
        jr nz,Dk3
        ld a,2
	jr open_key
Dk3:
        cp '3'
        jr nz,Dk4
        ld a,3
	jr open_key
Dk4:
        cp '4'
        jr nz,Dk5
        ld a,4
	jr open_key
Dk5:
        cp '5'
        jr nz,Dk6
        ld a,1
	jr open_key
Dk6:
        cp '6'
        jr nz,Dk7
        ld a,5
	jr open_key
Dk7:
        cp '7'
        jp nz,mainloop
        ld a,6
open_key:
        call WndOpen
        jp repaint
; Interface 2 joystick 1 electrically acts as the digit keys 6/7/8/9/0.
; No direct port reads. Never translate digits when typing Note/Console.
; Elsewhere: 6=left, 7=right, 8=down, 9=up, 0=enter.
JoyTranslate:
        ld a,(SetJoyEnabled)
        or a
        ret z
        ld a,(WndCount)
        or a
        ret z                      ; desktop selection uses the raw digits
        ld a,(DlgUp)
        or a
        jr nz,JtMap
        ld a,(MenuOpen)
        or a
        jr nz,JtMap
        ld hl,(WinApp)
        ld de,AppNote
        or a
        sbc hl,de
        ret z
        ld hl,(WinApp)
        ld de,AppTerm
        or a
        sbc hl,de
        ret z
JtMap:
        ld a,b
        cp '6'
        jr z,JtLeft
        cp '7'
        jr z,JtRight
        cp '8'
        jr z,JtDown
        cp '9'
        jr z,JtUp
        cp '0'
        ret nz
        ld b,13
        ret
JtLeft:
        ld b,8
        ret
JtRight:
        ld b,9
        ret
JtDown:
        ld b,10
        ret
JtUp:
        ld b,11
        ret

; Selected desktop icon has the original inverted-label focus marker.
; Linear navigation is reliable even with the unequal icon positions.
JoyPrevious:
        ld a,(DskSelected)
        or a
        jr nz,JpDec
        ld a,7
JpDec:
        dec a
        ld (DskSelected),a
        jp repaint
JoyNext:
        ld a,(DskSelected)
        inc a
        cp 7
        jr c,JnSave
        xor a
JnSave:
        ld (DskSelected),a
        jp repaint
JoyActivate:
        ld a,(DskSelected)
        cp 5
        jr z,JoySettings
        cp 6
        jr z,JoyConsole
        cp 4
        jr z,JoyAbout
        cp 3
        jr z,JoyFiles
        cp 2
        jr z,JoyCalendar
        cp 1
        jr z,JoyClock
        xor a
        jp open_key
JoyClock:
        ld a,2
        jp open_key
JoyCalendar:
        ld a,3
        jp open_key
JoyFiles:
        ld a,4
        jp open_key
JoyAbout:
        ld a,1
        jp open_key
JoyConsole:
        ld a,6
        jp open_key
JoySettings:
        call DlgOpen
        jp mainloop
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
        ld a,(DlgUp)
        or a
        jp nz,mainloop
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
	jr z,menu_left_tab
        cp 9
	jr z,menu_right_tab
        cp 11
        jr z,menu_previous
        cp 10
        jr z,menu_next
        cp 13
        jr z,menu_choose
        jp mainloop
menu_left_tab:
        ld a,(MenuOpen)
        dec a
        jr nz,menu_tab_set
        ld a,4
        jr menu_tab_set
menu_right_tab:
        ld a,(MenuOpen)
        inc a
        cp 5
        jr c,menu_tab_set
        ld a,1
menu_tab_set:
        push af
        xor a
        ld (MenuSel),a
        pop af
        call MenuOpenDrop
	jr repaint
menu_previous:
        ld a,(MenuSel)
        or a
        jp z,mainloop
        dec a
        ld (MenuSel),a
	jr repaint
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
	jr repaint
menu_choose:
        ld a,(MenuOpen)
        ld (MnLastMenu),a
        ld a,(MenuSel)
        push af
        call MenuClose
        call WndRepaintAll
        pop af
        call MenuAction
        jp mainloop
modal_dispatch:
        ld a,b
        cp 7
        jr z,modal_close
        call DlgKey
        jp mainloop
modal_close:
        call DgEscape
        jp mainloop
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
	jp zx_syscall

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
        call DrawLattice
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

 ; ZXDesk lattice: $88 on pixel rows modulo four 0 and $22 on 2.
; Draw only after ZX-UX grants the process the screen.
DrawLattice:
        ld a,(SetLattice)
        cp 1
        ret nz
        ld a,9
LdRow:
        ld (BgRow),a
        and 3
        ld c,0
        jr z,LdDotA
        cp 2
        jr z,LdDotB
        jr LdNext
LdDotA:
        ld c,$88
        jr LdPaint
LdDotB:
        ld c,$22
LdPaint:
        ld a,(BgRow)
        push bc
        call RowAddr
        pop bc
        ld a,c
        ld b,32
LdFill:
        ld (hl),a
        inc hl
        djnz LdFill
LdNext:
        ld a,(BgRow)
        inc a
        cp 183
        jr c,LdRow
        ret

        section data
rawtty: db 0,0,0,0,$a0,0
owned: db 0
MenuSel: db 0
BgRow: db 0
key: db 0
TxtMenu: db 'ZX DESK   FILE   VIEW   HELP',0
TxtStatus: db 'ZX-UX / ZXDESK',0
        section bss
oldtty: ds 6