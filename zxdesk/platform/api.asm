; ZXDesk window API to ZX-UX-owned screen/SSX1 data.
; Window text vectors: HL=text, B=pixel row, C=column.
        section text
        global ApiWinPrint
        global ApiWinPrintInv
        global ApiWinPrintIf
        global ApiWinRows
        global ApiWinAddr
        global ApiOpenFile
        extern WinX
        extern WinY
        extern WinW
        extern WinH
        extern PrintInv
        extern PxRow
        extern PrintStrPx
        extern DevFillRect
        extern FrX
        extern FrY
        extern FrW
        extern FrH
        extern FrPat
        extern WinGrab
        extern AddrAt
        extern WndOpen
        extern WndClose
        extern WndRepaintAll
        extern NoteLoadAs
ApiWinPrint:
        xor a
        ld (PrintInv),a
ApiWinPrintGo:
        push hl
        ld a,(WinX)
        inc a
        add a,c
        ld c,a
        ld a,(WinY)
        add a,10
        add a,b
        ld (PxRow),a
        pop hl
        jp PrintStrPx
ApiWinPrintIf:
        or a
        jr z,ApiWinPrint
ApiWinPrintInv:
        ld a,1
        ld (PrintInv),a
        call ApiWinPrintGo
        xor a
        ld (PrintInv),a
        ret
ApiWinRows:
        ld a,(WinH)
        sub 10
        ret
ApiWinAddr:
        ld a,(WinX)
        inc a
        add a,c
        ld c,a
        ld a,(WinY)
        add a,10
        add a,b
        jp AddrAt
ApiOpenFile:
        push hl
        xor a
        call WndOpen
        pop hl
        ret c
        call NoteLoadAs
        jr c,OfBad
        call WndRepaintAll
        xor a
        ret
OfBad:
        call WndClose
        scf
        ret