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
        ; Deliver ZX-UX input through ZXDesk's original event ring.
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
        cp 4
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
        ld a,1
        ld c,0
        ld hl,rule
        call draw_at
        ld a,21
        ld c,0
        ld hl,rule
        call draw_at
        ld a,22
        ld c,0
        ld hl,helpbar
        call draw_at
        ld a,23
        ld c,0
        ld hl,helpbar2
        call draw_at
        ld a,5
        ld c,2
        ld hl,icons1
        call draw_at
        ld a,6
        ld c,2
        ld hl,icons2
        call draw_at
        ld a,7
        ld c,2
        ld hl,icons3
        call draw_at
        ld a,12
        ld c,2
        ld hl,icons4
        call draw_at
        ld a,13
        ld c,2
        ld hl,icons5
        call draw_at
        ld a,14
        ld c,2
        ld hl,icons6
        call draw_at
        call draw_selection
        ld a,(window)
        or a
        call nz,draw_window
        ld a,(menu)
        or a
        call nz,draw_menu
        ret

draw_selection:
        ld a,(window)
        or a
        ret nz
        ld a,(selected)
        dec a
        ld e,a
        ld d,0
        ld hl,selcols
        add hl,de
        ld c,(hl)
        ld a,(selected)
        cp 4
        jp c,sel_top
        ld a,12
        jp sel_mark
sel_top:
        ld a,5
sel_mark:
        ld hl,selectmark
        jp draw_at

draw_window:
        ld a,(wy)
        ld c,0
        call at_wx
        ld hl,frame_top
        call draw_at
        ld a,(wy)
        inc a
        ld (workrow),a
        ld a,9
        ld (count),a
win_lines:
        ld a,(workrow)
        ld c,0
        call at_wx
        ld hl,frame_body
        call draw_at
        ld a,(workrow)
        inc a
        ld (workrow),a
        ld a,(count)
        dec a
        ld (count),a
        jp nz,win_lines
        ld a,(workrow)
        ld c,0
        call at_wx
        ld hl,frame_bot
        call draw_at
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
        ld a,(wy)
        inc a
        ld c,2
        call at_wx
        call draw_at
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
        ld a,38
        call zx_syscall
        call make_tick_hex
        ld hl,clock_caption
        call win_line3
        ld hl,ticks_text
        call win_line5
        ret
content_files:
        ld hl,files_caption
        call win_line3
        ld hl,files_caption2
        call win_line5
        ret
content_about:
        ld hl,about_caption
        call win_line3
        ld hl,about_caption2
        call win_line5
        ret
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

draw_menu:
        cp 1
        jp z,menu_file
        cp 2
        jp z,menu_view
        ld hl,menu_help
        ld c,22
        jp menu_paint
menu_file:
        ld hl,menu_file_text
        ld c,5
        jp menu_paint
menu_view:
        ld hl,menu_view_text
        ld c,12
menu_paint:
        ld a,2
        call draw_at
        ret

; A = 0..65535 in HL from the tick syscall, render four hex digits.
make_tick_hex:
        ld a,h
        ld de,ticks_text+7
        call hex_byte
        ld a,l
        call hex_byte
        ret
hex_byte:
        push af
        rrca
        rrca
        rrca
        rrca
        call hex_digit
        pop af
        call hex_digit
        ret
hex_digit:
        and 15
        add a,'0'
        cp '9'+1
        jp c,hex_digit_store
        add a,7
hex_digit_store:
        ld (de),a
        inc de
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
        sub 32
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,FONT
        add hl,de
        ; Use original ZXDesk bitmap address/row traversal.
        push hl
        ld a,(pencol)
        ld c,a
        ld a,(penrow)
        add a,a
        add a,a
        add a,a
        call AddrAt
        ex de,hl
        pop hl
        ld b,8
glyph_row:
        ld a,(hl)
        ld (de),a
        inc hl
        ex de,hl
        call ScrDown
        ex de,hl
        djnz glyph_row
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
workrow: db 0
count:   db 0
selcols: db 2,12,22,2,12

title:  db ' ZXDESK   FILE    VIEW    HELP  ',0
rule:   db '--------------------------------',0
helpbar: db ' 1 NOTE 2 CLOCK 3 FILES 4 ABOUT ',0
helpbar2: db ' 5 SETUP M MENU  EDIT CLOSE     ',0
icons1: db ' +-----+   +-----+   +-----+ ',0
icons2: db ' |NOTE |   |CLOCK|   |FILES| ',0
icons3: db ' +-----+   +-----+   +-----+ ',0
icons4: db ' +-----+   +-----+           ',0
icons5: db ' |ABOUT|   |SETUP|           ',0
icons6: db ' +-----+   +-----+           ',0
selectmark: db '>',0
frame_top: db '+----------------------+',0
frame_body: db '|                      |',0
frame_bot: db '+----------------------+',0
titles: dw title_note,title_clock,title_files,title_about,title_setup
title_note: db 'NOTEPAD          [EDIT]',0
title_clock: db 'CLOCK            [EDIT]',0
title_files: db 'FILES            [EDIT]',0
title_about: db 'ABOUT            [EDIT]',0
title_setup: db 'SETTINGS         [EDIT]',0
note_caption: db 'TYPE TEXT BELOW:',0
clock_caption: db 'ZX-UX FRAME COUNTER',0
ticks_text: db 'TICKS: 0000',0
files_caption: db 'FILES BELONG TO ZX-UX',0
files_caption2: db 'USE /BIN/LS IN SHELL',0
about_caption: db 'ZX DESK ON ZX-UX',0
about_caption2: db 'GUI: DAMIAN COOPER',0
setup_caption: db 'ARROWS MOVE WINDOWS',0
setup_caption2: db 'EDIT CLOSES WINDOW',0
menu_file_text: db '1 NOTE  3 FILES',0
menu_view_text: db '2 CLOCK  5 SETUP',0
menu_help: db '4 ABOUT',0

        section bss
oldtty: ds 6
