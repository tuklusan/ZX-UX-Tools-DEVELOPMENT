; ZXDesk desktop adapted for ZX-UX's SSX1 process model.
; Based on the desktop, chrome and menu layout of Damian Cooper's ZX Desk.
; MIT license: see zxdesk/NOTICE.txt.
;
; The kernel owns interrupts, memory, terminal and cassette.
; All pointers in this file are relocated by the ZX-UX loader.

        section text
        global start
        extern zx_syscall
        extern EvPost
        extern EvNext
        extern BuildScrTab
        extern AddrAt
        extern ScrDown
        extern PrintChar
        extern FillRowSolid
        extern WinSetGeometry
        extern WdEdges
        extern WdCloseBox
        extern WinDraw
        extern WinSetTitle
        extern DskInit
        extern DskPaintAll
        extern ClkInit
        extern ClkService
        extern ClkDraw
        extern ClkKey
        extern WdAbout
        extern MenuOpenDrop
        extern MenuClose

SCREEN  equ $4000
ATTRS   equ $5800
FONT    equ $3d00

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
        call redraw
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
        ; The kernel input byte enters ZXDesk's original event ring.
        call ClkService
        ld a,(key)
        ld b,a
        ld c,0
        ld a,4                   ; original EV_KEY
        call EvPost
        call EvNext
        cp 4
        jp nz,mainloop
        ld a,b
        cp 7
        jp z,escape_key
        cp 13
        jp z,enter_key
        cp 8
        jp z,up_key
        cp 9
        jp z,down_key
        cp 10
        jp z,left_key
        cp 11
        jp z,right_key
        cp 12
        jp z,backspace_key
        cp 'm'
        jp z,menu_key
        cp 'M'
        jp z,menu_key
        ld b,a
        ld a,(window)
        cp 1
        jp z,note_key
        ld a,b
        cp '1'
        jp z,note_open
        cp '2'
        jp z,clock_open
        cp '3'
        jp z,files_open
        cp '4'
        jp z,about_open
        cp '5'
        jp z,setup_open
        cp 'n'
        jp z,note_open
        cp 'N'
        jp z,note_open
        cp 'c'
        jp z,clock_open
        cp 'C'
        jp z,clock_open
        cp 'f'
        jp z,files_open
        cp 'F'
        jp z,files_open
        cp 'a'
        jp z,about_open
        cp 'A'
        jp z,about_open
        cp 's'
        jp z,setup_open
        cp 'S'
        jp z,setup_open
        cp 'q'
        jp z,release
        cp 'Q'
        jp z,release
        jp mainloop

note_key:
        ld a,b
        cp 32
        jp c,mainloop
        cp 127
        jp nc,mainloop
        ld a,(note_len)
        cp 19
        jp nc,mainloop
        ld e,a
        ld d,0
        ld hl,note_text
        add hl,de
        ld (hl),b
        inc hl
        ld (hl),0
        ld a,(note_len)
        inc a
        ld (note_len),a
        jp repaint
backspace_key:
        ld a,(window)
        cp 1
        jp nz,mainloop
        ld a,(note_len)
        or a
        jp z,mainloop
        dec a
        ld (note_len),a
        ld e,a
        ld d,0
        ld hl,note_text
        add hl,de
        ld (hl),0
        jp repaint

menu_key:
        ld a,(menu)
        inc a
        cp 5
        jp c,menu_store
        xor a
menu_store:
        ld (menu),a
        jp repaint
escape_key:
        xor a
        ld (menu),a
        ld (window),a
        jp repaint
enter_key:
        ld a,(menu)
        or a
        jp z,open_selected
        cp 1
        jp z,note_open
        cp 2
        jp z,clock_open
        jp about_open
open_selected:
        ld a,(selected)
        jp select_open
up_key:
        ld a,(window)
        cp 2
        jr nz,not_clock_up_key
        ld a,8
        call ClkKey
        jp repaint
not_clock_up_key:
        ld a,(window)
        or a
        jp nz,win_up
        ld a,(selected)
        dec a
        jp nz,sel_store
        ld a,5
sel_store:
        ld (selected),a
        jp repaint
win_up:
        ld a,(wy)
        cp 3
        jp z,mainloop
        dec a
        ld (wy),a
        jp repaint
down_key:
        ld a,(window)
        cp 2
        jr nz,not_clock_down_key
        ld a,9
        call ClkKey
        jp repaint
not_clock_down_key:
        ld a,(window)
        or a
        jp nz,win_down
        ld a,(selected)
        inc a
        cp 6
        jp c,sel_store
        ld a,1
        jp sel_store
win_down:
        ld a,(wy)
        cp 10
        jp z,mainloop
        inc a
        ld (wy),a
        jp repaint
left_key:
        ld a,(window)
        cp 2
        jr nz,not_clock_left_key
        ld a,10
        call ClkKey
        jp repaint
not_clock_left_key:
        ld a,(window)
        or a
        jp z,up_key
        ld a,(wx)
        cp 1
        jp z,mainloop
        dec a
        ld (wx),a
        jp repaint
right_key:
        ld a,(window)
        cp 2
        jr nz,not_clock_right_key
        ld a,11
        call ClkKey
        jp repaint
not_clock_right_key:
        ld a,(window)
        or a
        jp z,down_key
        ld a,(wx)
        cp 8
        jp z,mainloop
        inc a
        ld (wx),a
        jp repaint

select_open:
        cp 1
        jp z,note_open
        cp 2
        jp z,clock_open
        cp 3
        jp z,files_open
        cp 4
        jp z,about_open
        jp setup_open
note_open:
        ld a,1
        jp set_window
clock_open:
        ld a,2
        jp set_window
files_open:
        ld a,3
        jp set_window
about_open:
        ld a,4
        jp set_window
setup_open:
        ld a,5
set_window:
        ld (window),a
        ld (selected),a
        xor a
        ld (menu),a
repaint:
        call redraw
        jp mainloop

release:
        ld a,(owned)
        or a
        jp z,restore
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

redraw:
        xor a
        ld (inverse),a
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
        ld a,0
        ld c,0
        ld hl,title
        call draw_at
        ; ZXDesk original FillRowSolid replaces fake ASCII rules.
        ld a,8
        call FillRowSolid
        ld a,183
        call FillRowSolid
        ld a,22
        ld c,0
        ld hl,helpbar
        call draw_at
        ld a,23
        ld c,0
        ld hl,helpbar2
        call draw_at
        ; Original ZXDesk desktop bitmap icons and labels.
        call DskPaintAll
        ld a,(window)
        or a
        call nz,draw_window
        ld a,(menu)
        or a
        call nz,MenuOpenDrop
        ret

draw_window:
        ld a,(wx)
        push af
        ld a,(wy)
        ld b,a
        pop af
        call WinSetGeometry
        ld a,(window)
        dec a
        ld e,a
        ld d,0
        ld hl,titles
        add hl,de
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        call WinSetTitle
        ; ZXDesk's original graphical window compositor replaces
        ; the ASCII frame drawing loop in this same change.
        call WinDraw
        ld a,(window)
        cp 1
        jp z,content_note
        cp 2
        jp z,content_clock
        cp 3
        jp z,content_files
        cp 4
        jp z,content_about
        jp content_setup
content_note:
        ld hl,note_caption
        call win_line3
        ld hl,note_text
        call win_line5
        ret
content_clock:
        jp ClkDraw
content_files:
        ld hl,files_caption
        call win_line3
        ld hl,files_caption2
        call win_line5
        ret
content_about:
        jp WdAbout
content_setup:
        ld hl,setup_caption
        call win_line3
        ld hl,setup_caption2
        call win_line5
        ret
win_line3:
        ld a,(wy)
        add a,3
        jp win_content
win_line5:
        ld a,(wy)
        add a,5
win_content:
        ld c,2
        call at_wx
        jp draw_at
at_wx:
        push af
        ld a,(wx)
        add a,c
        ld c,a
        pop af
        ret

; Draw a zero terminated string at A=row, C=column, HL=source.
draw_at:
        ld (penrow),a
        ld a,c
        ld (pencol),a
print_string:
        ld a,(hl)
        or a
        ret z
        ld a,(pencol)
        cp 32
        ret nc
        ld a,(hl)
        push hl
        call draw_char
        pop hl
        inc hl
        jp print_string

; Byte-cell renderer from the original desktop's 8-pixel font model.
; The ROM glyphs already live in the fixed 16K ROM.
draw_char:
        cp 32
        ret c
        push af
        push bc
        push de
        push hl
        ld d,a
        ld a,(pencol)
        ld c,a
        ld a,(penrow)
        ld b,a
        ld a,d
        ; Original PrintChar: A glyph, B character row, C byte column.
        call PrintChar
        ld a,(pencol)
        inc a
        ld (pencol),a
        pop hl
        pop de
        pop bc
        pop af
        ret

        section data
rawtty:  db 0,0,0,0,$a0,0
owned:   db 0
key:     db 0
window:  db 0
menu:    db 0
selected: db 1
wx:      db 4
wy:      db 4
note_len: db 0
note_text: db 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
penrow:  db 0
pencol:  db 0
inverse: db 0

title:  db 'ZX DESK   FILE   VIEW   HELP',0
rule:   db '--------------------------------',0
helpbar: db ' 1 NOTE 2 CLOCK 3 FILES 4 ABOUT ',0
helpbar2: db ' 5 SETUP M MENU  EDIT CLOSE     ',0
titles: dw title_note,title_clock,title_files,title_about,title_setup
title_note: db 'NOTEPAD          [EDIT]',0
title_clock: db 'CLOCK            [EDIT]',0
title_files: db 'FILES            [EDIT]',0
title_about: db 'ABOUT            [EDIT]',0
title_setup: db 'SETTINGS         [EDIT]',0
note_caption: db 'TYPE TEXT BELOW:',0
files_caption: db 'FILES BELONG TO ZX-UX',0
files_caption2: db 'USE /BIN/LS IN SHELL',0
setup_caption: db 'ARROWS MOVE WINDOWS',0
setup_caption2: db 'EDIT CLOSES WINDOW',0

        section bss
oldtty: ds 6