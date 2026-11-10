; ZX-UX SSX1 process lifecycle, keyboard and event adapter for original ZXDesk.
; This is not a separate desktop, ROM or operating system.
        section text
        global start
        global clean_exit
        global SetJoyEnabled
        global DrawDesktop
        global MenuSel
        extern zx_syscall
        extern DskPaintAll
        extern DskSelected
        extern AppTerm
        extern WinApp
        extern ClkInit
        extern ClkService
        extern WndInit
        extern WndOpen
        extern WndClose
        extern WndRepaintAll
        extern WndFocusTo
        extern WndCount
        extern WndZ
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
        extern FontBase
        extern AppCall
        extern DlgUp
        extern WinX
        extern WinY
        extern WinW
        extern WinH
        extern DlgClose
        extern MenuIsSep
        extern RowAddr

SCREEN equ $4000
ATTRS equ $5800
APP_KEY equ 4
APP_CONSOLE equ 4

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
        ld (FontBase),hl       ; _screen returns the OS-owned font64
        ld a,e
        or a
        jp nz,release
        call ClkInit
        call WndInit
        ld a,APP_CONSOLE       ; the console is the default application
        call WndOpen
mainloop:
        ld hl,0
        ld de,key
        ld bc,1
        ld a,3
        call zx_syscall
        jp c,clean_exit
        ld a,h
        or l
        jp z,clean_exit
        call ClkService
        ld a,(key)
        ld b,a
        call JoyTranslate
        ld a,(DlgUp)
        or a
        jp nz,modal_dispatch
        ld a,(MoveMode)
        or a
        jp nz,move_key
        ld a,b
        cp 7                   ; EDIT = CAPS SHIFT+1 (ZX-UX raw key)
        jp z,menu_key
        ; An open menu owns the keyboard, so EDIT then Q reaches menu_dispatch
        ; even while windows are open.
        ld a,(MenuOpen)
        or a
        jp nz,menu_dispatch
        ld a,b
        cp 'q'
        jp z,quit_key
        cp 'Q'
        jp z,quit_key
        ; All ordinary letters, including M, reach the focused application.
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
        jp z,mainloop          ; apps launch from the ZX DESK menu
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
        jp mainloop
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
        ld a,5
JpDec:
        dec a
        ld (DskSelected),a
        jp repaint
JoyNext:
        ld a,(DskSelected)
        inc a
        cp 5
        jr c,JnSave
        xor a
JnSave:
        ld (DskSelected),a
        jp repaint
JoyActivate:
        ld a,(DskSelected)
        ld e,a
        ld d,0
        ld hl,JoyApps
        add hl,de
        ld a,(hl)
        jp open_key
next_window:
        ld a,(WndCount)
        cp 2
        jp c,repaint
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
        jp z,clean_exit
        ; q is part of a document while a window has focus.
        ld a,'q'
        ld c,APP_KEY
        call AppCall
        jp repaint
; EDIT (CAPS SHIFT+1) opens/cycles the menu and begins a shortcut.
; BREAK (CAPS SHIFT+SPACE) is reserved by the ZX-UX kernel.
menu_dispatch:
        ld a,b
        cp 'q'
        jp z,clean_exit
        cp 'Q'
        jp z,clean_exit
        cp 'm'
        jp z,move_start
        cp 'M'
        jp z,move_start
        cp 'n'
        jr z,menu_cycle
        cp 'N'
        jr z,menu_cycle
        cp 'x'
        jr z,menu_close_front
        cp 'X'
        jr z,menu_close_front
        jr menu_navigation
menu_cycle:
        call MenuClose
        jp next_window
menu_close_front:
        call MenuClose
        jp close_key
menu_navigation:
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
; Up/Down skip the dotted separator line.
menu_previous:
        ld a,(MenuSel)
        ld b,a
MpvLoop:
        ld a,b
        or a
        jp z,mainloop
        dec b
        ld c,b
        call MenuIsSep
        jr z,MpvLoop
        ld a,b
        ld (MenuSel),a
        jr repaint
menu_next:
        ld a,(MenuSel)
        ld b,a
MnxLoop:
        inc b
        ld a,(MnCount)
        cp b
        jp z,mainloop
        jp c,mainloop
        ld c,b
        call MenuIsSep
        jr z,MnxLoop
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
modal_dispatch:                ; a notice closes on Enter or EDIT
        ld a,b
        cp 7
        jr z,modal_close
        cp 13
        jp nz,mainloop
modal_close:
        call DlgClose
        jp mainloop
menu_key:
        xor a
        ld (MenuSel),a
        ld a,(MenuOpen)
        inc a
        cp 5
        jr c,MkSet
        ld a,1
MkSet:
        call MenuOpenDrop
repaint:
        ; A dialog opened by the key just handled stays on screen untouched.
        ld a,(DlgUp)
        or a
        jp nz,mainloop
        call WndRepaintAll
        ld a,(MenuOpen)
        or a
        call nz,MenuPaint
        jp mainloop

; EDIT then M: the arrow keys move the front window 8 pixels at a time, kept
; inside the desktop (x + width <= 32 bytes, 9 <= y, y + height <= 183).
; Enter or EDIT drops it.
move_start:
        call MenuClose
        ld a,(WndCount)
        or a
        jp z,repaint
        ld a,1
        ld (MoveMode),a
        jp repaint
move_key:
        ld a,b
        cp 7
        jr z,move_done
        cp 13
        jr z,move_done
        cp 8
        jr z,mv_left
        cp 9
        jr z,mv_right
        cp 11
        jr z,mv_up
        cp 10
        jp nz,mainloop
        ld a,(WinY)            ; down: y = min(y + 8, 183 - height)
        add a,8
        ld c,a
        ld a,183
        ld hl,WinH
        sub (hl)
        cp c
        jr nc,mv_dok
        ld c,a
mv_dok:
        ld a,c
        jr mv_putY
mv_up:
        ld a,(WinY)            ; up: y = max(y - 8, 9)
        sub 8
        jr c,mv_top
        cp 9
        jr nc,mv_putY
mv_top:
        ld a,9
mv_putY:
        ld (WinY),a
        jp repaint
mv_left:
        ld a,(WinX)
        or a
        jp z,mainloop
        dec a
mv_putX:
        ld (WinX),a
        jp repaint
mv_right:
        ld a,(WinX)
        ld hl,WinW
        add a,(hl)
        cp 32
        jp nc,mainloop
        ld a,(WinX)
        inc a
        jr mv_putX
move_done:
        xor a
        ld (MoveMode),a
        jp repaint
 ; Normal exit clears the application's bitmap before ZX-UX
; returns the screen to its text console. BREAK is a kernel kill
; and cannot execute this process-side cleanup.
clean_exit:
        ld hl,SCREEN
        ld de,SCREEN+1
        ld bc,6143
        xor a
        ld (hl),a
        ldir
        jp release

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
        ld hl,TxtStatus
        ld a,(MoveMode)
        or a
        jr z,DdStat
        ld hl,TxtMove
DdStat:
        ld c,1
        call PrintStrPx
        ld hl,ATTRS
        ld de,ATTRS+1
        ld bc,767
        ld (hl),$78
        ldir
        ret

 ; ZXDesk lattice: $88 on pixel rows modulo four 0 and $22 on 2.
; Draw only after ZX-UX grants the process the screen.
DrawLattice:
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
TxtMenu: db 'ZX DESK           FILE          VIEW          HELP',0
TxtStatus: db 'EDIT (CAPS+1): MENU THEN M=MOVE N=NEXT X=CLOSE Q=QUIT ZX DESK',0
TxtMove: db 'ARROWS MOVE THE WINDOW  ENTER=DONE',0
MoveMode: db 0
JoyApps: db 0,2,3,1,4          ; desktop icon order: Notes Clock Files About Console
SetJoyEnabled: db 0            ; Sinclair joystick navigation, toggled from the ZX DESK menu
        section bss
oldtty: ds 6