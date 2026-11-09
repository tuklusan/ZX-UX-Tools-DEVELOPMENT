; ZXDesk Notepad, transplanted from Damian Cooper's src/note.inc (MIT).
; The original 16x16 document, editing routines and pixel-row cursor model.
; ZX-UX supplies memory and screen services through window app adapters.
        section text
        global NoteState
        global NoteInit
        global NoteDrawInterior
        global NoteKey
        global NoteNew
        global NoteModified
        extern WinH
        extern ApiWinPrint
        extern ApiWinPrintInv

NOTECOLS equ 14
NOTELAST equ 13
NOTEROWS equ 16
NOTELASTROW equ 15
NOTESTRIDE equ 16
NOTETOP equ 12
NOTEREFLOW equ 2

; Original NoteRowAddr / NoteCurAddr / view helpers.
NoteRowAddr:
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,NoteBuf
        add hl,de
        ret
NoteCurAddr:
        ld a,(NoteCY)
        jp NoteRowAddr
NoteVisRows:
        ld a,(WinH)
        sub 14
        jr c,NvrOne
        srl a
        srl a
        srl a
        jr z,NvrOne
        cp NOTEROWS
        ret c
        ld a,NOTEROWS
        ret
NvrOne:
        ld a,1
        ret
NoteRowPx:
        ld c,a
        ld a,(NoteTop)
        ld b,a
        ld a,c
        sub b
        ret c
        push af
        call NoteVisRows
        ld b,a
        pop af
        cp b
        ccf
        ret c
        add a,a
        add a,a
        add a,a
        add a,2
        or a
        ret
NoteScroll:
        ld a,(NoteCY)
        ld c,a
        ld a,(NoteTop)
        cp c
        jr z,NsSame
        jr c,NsBelowTop
        ld a,c
        ld (NoteTop),a
        or 1
        ret
NsBelowTop:
        call NoteVisRows
        ld b,a
        ld a,(NoteTop)
        add a,b
        dec a
        cp c
        jr nc,NsSame
        ld a,c
        sub b
        inc a
        ld (NoteTop),a
        or 1
        ret
NsSame:
        xor a
        ret
NoteColByte:
        ld c,a
        ret

; Original ZXDesk's visible-row painter and cursor inversion.
NoteDrawLine:
        push af
        call NoteRowPx
        jr c,NdlOff
        ld b,a
        xor a
        call NoteColByte
        pop af
        push bc
        call NoteRowAddr
        pop bc
        jp ApiWinPrint
NdlOff:
        pop af
        ret
NoteDrawInterior:
        call NoteDrawAll
        jp NoteCurDraw
NoteDrawAll:
        call NoteVisRows
        ld b,a
        ld a,(NoteTop)
        ld c,a
NdaLoop:
        push bc
        ld a,c
        call NoteDrawLine
        pop bc
        inc c
        ld a,c
        cp NOTEROWS
        ret nc
        djnz NdaLoop
        ret
NoteCurDraw:
        ld a,(NoteCY)
        call NoteRowPx
        ret c
        ld b,a
        ld a,(NoteCX)
        call NoteColByte
        push bc
        call NoteCurAddr
        ld a,(NoteCX)
        ld e,a
        ld d,0
        add hl,de
        ld a,(hl)
        ld (NoteCell),a
        pop bc
        ld hl,NoteCell
        jp ApiWinPrintInv

; NoteNew, insertion and movement are copied from the original
; editor's buffer interface; they neither own the screen nor interrupts.
NoteInit:
        call NoteNew
        ld hl,TxtNoteName
        ld de,NoteName
        ld bc,5
        ldir
        ret
NoteNew:
        xor a
        ld (NoteRowIx),a
        ld b,NOTEROWS
NnRow:
        push bc
        ld a,(NoteRowIx)
        call NoteBlankRow
        ld a,(NoteRowIx)
        inc a
        ld (NoteRowIx),a
        pop bc
        djnz NnRow
        xor a
        ld (NoteCX),a
        ld (NoteCY),a
        ld (NoteTop),a
        ld (NoteEdited),a
        ld (NoteDirty),a
        ld (NoteModified),a
        ret
NoteInsert:
        ld (NoteChar),a
        call NoteCurAddr
        ld (NoteLine),hl
        ld a,NOTELAST
        ld c,a
        ld a,(NoteCX)
        cp c
        jr nc,NiPut
        ld b,a
        ld a,NOTELAST-1
        sub b
        inc a
        ld c,a
        ld b,0
        ld hl,(NoteLine)
        ld de,NOTELAST-1
        add hl,de
        ld d,h
        ld e,l
        inc de
        lddr
NiPut:
        ld hl,(NoteLine)
        ld a,(NoteCX)
        ld e,a
        ld d,0
        add hl,de
        ld a,(NoteChar)
        ld (hl),a
        ld a,1
        ld (NoteEdited),a
        ld (NoteModified),a
        ld a,(NoteCX)
        inc a
        cp NOTECOLS
        jr c,NiSetX
        ld a,(NoteCY)
        inc a
        cp NOTEROWS
        jr nc,NiEnd
        ld (NoteCY),a
        xor a
NiSetX:
        ld (NoteCX),a
        ret
NiEnd:
        ld a,NOTELAST
        ld (NoteCX),a
        ret
NoteBlankRow:
        call NoteRowAddr
        ld b,NOTECOLS
        ld a,' '
NbrLoop:
        ld (hl),a
        inc hl
        djnz NbrLoop
        ld (hl),0
        inc hl
        ld (hl),0
        ret
NoteLineLen:
        call NoteRowAddr
        ld de,NOTELAST
        add hl,de
        ld b,NOTECOLS
NllLoop:
        ld a,(hl)
        cp ' '
        jr nz,NllGot
        dec hl
        djnz NllLoop
        xor a
        ret
NllGot:
        ld a,b
        ret
NoteOpenRow:
        ld (NoteRowIx),a
        ld a,NOTELASTROW
        ld (NoteRowDst),a
NorLoop:
        ld a,(NoteRowDst)
        ld hl,NoteRowIx
        cp (hl)
        ret z
        dec a
        call NoteRowAddr
        push hl
        ld a,(NoteRowDst)
        call NoteRowAddr
        ex de,hl
        pop hl
        ld bc,NOTESTRIDE
        ldir
        ld a,(NoteRowDst)
        dec a
        ld (NoteRowDst),a
        jr NorLoop
NoteCloseRow:
        ld (NoteRowDst),a
NcrLoop:
        ld a,(NoteRowDst)
        cp NOTELASTROW
        jr nc,NcrBlank
        inc a
        call NoteRowAddr
        push hl
        ld a,(NoteRowDst)
        call NoteRowAddr
        ex de,hl
        pop hl
        ld bc,NOTESTRIDE
        ldir
        ld a,(NoteRowDst)
        inc a
        ld (NoteRowDst),a
        jr NcrLoop
NcrBlank:
        ld a,NOTELASTROW
        jp NoteBlankRow
NoteBack:
        ld a,(NoteCX)
        or a
        jr z,NbEdge
        dec a
        ld (NoteCX),a
        ld c,a
        call NoteCurAddr
        ld e,c
        ld d,0
        add hl,de
        ld d,h
        ld e,l
        inc hl
        ld a,NOTELAST
        sub c
        ld c,a
        ld b,0
        or a
        jr z,NbTail
        ldir
NbTail:
        call NoteCurAddr
        ld de,NOTELAST
        add hl,de
        ld (hl),' '
        ld a,1
        ld (NoteEdited),a
        ld (NoteModified),a
        ret
NbEdge:
        ld a,(NoteCY)
        or a
        ret z
        dec a
        call NoteLineLen
        ld (NoteJoinAt),a
        ld a,(NoteCY)
        call NoteLineLen
        ld c,a
        ld a,(NoteJoinAt)
        add a,c
        cp NOTECOLS+1
        jr nc,NbMoveOnly
        ld a,c
        or a
        jr z,NbJoinEmpty
        ld b,0
        ld a,(NoteCY)
        call NoteRowAddr
        push hl
        ld a,(NoteCY)
        dec a
        call NoteRowAddr
        ld a,(NoteJoinAt)
        ld e,a
        ld d,0
        add hl,de
        ex de,hl
        pop hl
        ldir
NbJoinEmpty:
        ld a,(NoteCY)
        call NoteCloseRow
        ld hl,NoteCY
        dec (hl)
        ld a,(NoteJoinAt)
        ld (NoteCX),a
        ld a,NOTEREFLOW
        ld (NoteEdited),a
        ld a,1
        ld (NoteModified),a
        ret
NbMoveOnly:
        ld hl,NoteCY
        dec (hl)
        ld a,NOTELAST
        ld (NoteCX),a
        ret
NoteEnter:
        ld a,(NoteCY)
        cp NOTELASTROW
        ret nc
        inc a
        call NoteOpenRow
        ld a,(NoteCY)
        inc a
        call NoteBlankRow
        ld a,NOTECOLS
        ld c,a
        ld a,(NoteCX)
        neg
        add a,c
        ld (NoteRowDst),a
        or a
        jr z,NeNoTail
        ld c,a
        ld b,0
        ld a,(NoteCY)
        call NoteRowAddr
        ld a,(NoteCX)
        ld e,a
        ld d,0
        add hl,de
        push hl
        ld a,(NoteCY)
        inc a
        call NoteRowAddr
        ex de,hl
        pop hl
        ldir
        ld a,(NoteCY)
        call NoteRowAddr
        ld a,(NoteCX)
        ld e,a
        ld d,0
        add hl,de
        ld a,(NoteRowDst)
        ld b,a
        ld a,' '
NeBlank:
        ld (hl),a
        inc hl
        djnz NeBlank
NeNoTail:
        ld hl,NoteCY
        inc (hl)
        xor a
        ld (NoteCX),a
        ld a,NOTEREFLOW
        ld (NoteEdited),a
        ld a,1
        ld (NoteModified),a
        ret
NoteLeft:
        ld a,(NoteCX)
        or a
        ret z
        dec a
        ld (NoteCX),a
        ret
NoteRight:
        ld a,(NoteCX)
        cp NOTELAST
        ret nc
        inc a
        ld (NoteCX),a
        ret
NoteUp:
        ld a,(NoteCY)
        or a
        ret z
        dec a
        ld (NoteCY),a
        ret
NoteDown:
        ld a,(NoteCY)
        cp NOTELASTROW
        ret nc
        inc a
        ld (NoteCY),a
        ret

; Original key-event dispatch; key constants map to ZX-UX raw terminal.
NoteKey:
        ld (NoteChar),a
        xor a
        ld (NoteEdited),a
        ld a,(NoteChar)
        cp 10
        jr nz,NkNotL
        call NoteLeft
        jr NkView
NkNotL:
        cp 11
        jr nz,NkNotR
        call NoteRight
        jr NkView
NkNotR:
        cp 8
        jr nz,NkNotU
        call NoteUp
        jr NkView
NkNotU:
        cp 9
        jr nz,NkNotD
        call NoteDown
        jr NkView
NkNotD:
        cp 12
        jr nz,NkNotBs
        call NoteBack
        jr NkView
NkNotBs:
        cp 13
        jr nz,NkNotEnt
        call NoteEnter
        jr NkView
NkNotEnt:
        cp ' '
        ret c
        cp 128
        ret nc
        call NoteInsert
NkView:
        call NoteScroll
        ret z
        ld a,NOTEREFLOW
        ld (NoteEdited),a
        ret

        section data
TxtNoteName: db 'NOTE',0
NoteRowIx: db 0
NoteRowDst: db 0
NoteJoinAt: db 0
NoteChar: db 0
NoteLine: dw 0
NoteCell: db ' ',0
        section bss
NoteState:
NoteBuf: ds 256
NoteName: ds 11
NoteCX: ds 1
NoteCY: ds 1
NoteTop: ds 1
NoteEdited: ds 1
NoteDirty: ds 1
NoteModified: ds 1
