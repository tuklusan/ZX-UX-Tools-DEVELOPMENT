; ZXDesk window API to ZX-UX-owned screen/SSX1 data.
; Window text vectors: HL=text, B=pixel row, C=column.
        section text
        global ApiWinPrint
        global ApiWinPrintInv
        global ApiWinPrintIf
        global ApiWinClear
        global ApiWinRows
        global ApiWinGrab
        global ApiWinAddr
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
        jp ApiWinPrintInv
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
ApiWinClear:
        ld a,(WinX)
        inc a
        ld (FrX),a
        ld a,(WinY)
        add a,10
        ld (FrY),a
        ld a,(WinW)
        sub 2
        ld (FrW),a
        ld a,(WinH)
        sub 11
        ld (FrH),a
        ld hl,0
        ld (FrPat),hl
        jp DevFillRect
ApiWinAddr:
        ld a,(WinX)
        inc a
        add a,c
        ld c,a
        ld a,(WinY)
        add a,10
        add a,b
        jp AddrAt
ApiWinGrab:
        jp WinGrab
