; Original ZXDesk window edge and close-box drawing from src/zxdesk.asm.
; Damian Cooper (MIT); see zxdesk/NOTICE.txt.
; Screen is claimed by the ZX-UX process. No private interrupts or banking.
        section text
        global WinSetGeometry
        global WdEdges
        global WdCloseBox
        global WndRecAt
        global WndIsFront
        global WinDraw
        global WinX
        global WinY
        global WdFills
        global WndRaise
        global WndFlush
        global WndHitTest
        global WinSetTitle
        global WndSetCount
        global WdAbout
        extern AddrAt
        extern ScrDown
        extern DevFillRect
        extern FrX
        extern FrY
        extern FrW
        extern FrH
        extern FrPat
        extern PrintStrPx
        extern PrintInv
        extern PxRow

WinCapH equ 10
WNDRECSZ equ 15

; Translate the current temporary desktop window's character position to
; the original ZXDesk byte-column/pixel-row geometry model.
; A = byte column, B = character row.
WinSetGeometry:
        ld (WinX),a
        ld a,b
        add a,a
        add a,a
        add a,a
        ld (WinY),a
        ret

; Original ZXDesk: left/right window edges in pixel coordinates.
WdEdges:
                ld      a,(WinY)
                add     a,WinCapH
                ld      (PxRow),a
                ld      a,(WinH)
                sub     WinCapH+1
                ld      b,a
WdEdge:
                push    bc
                ld      a,(WinX)
                ld      c,a
                ld      a,(PxRow)
                call    AddrAt
                ld      a,(hl)
                or      $80
                ld      (hl),a
                ld      a,(WinW)
                dec     a
                ld      e,a
                ld      d,0
                add     hl,de
                ld      a,(hl)
                or      $01
                ld      (hl),a
                ld      a,(PxRow)
                inc     a
                ld      (PxRow),a
                pop     bc
                djnz    WdEdge
                ret

; Original ZXDesk: close-box image on the window title cap.
WdCloseBox:
                ld      a,(WinX)
                ld      c,a
                ld      a,(WinY)
                inc     a
                call    AddrAt
                ld      de,CloseBox
                ld      b,8
WdClose:
                ld      a,(de)
                ld      (hl),a
                inc     de
                call    ScrDown
                djnz    WdClose
                ret

; Original ZXDesk descriptor indexing and focus test.
; A = window slot, HL = descriptor in WndTab.
WndRecAt:
                ld      l,a
                ld      h,0
                ld      de,WNDRECSZ
                ld      b,a
                ld      hl,WndTab
                or      a
                ret     z
WraLoop:
                add     hl,de
                djnz    WraLoop
                ret

WinSetTitle:
        ld (WinTitle),hl
        ret
WndSetCount:
        ld (WndCount),a
        ret

; Original ZXDesk window composition: fill, edges, close box, title.
WinDraw:
        call WdFills
        call WdEdges
        call WdCloseBox
        call WdText
        ret

; ZXDesk WdFills, with the hardware-specific fill behind DevFillRect.
WdFills:
        ld a,(WinX)
        ld (FrX),a
        ld a,(WinY)
        ld (FrY),a
        ld a,(WinW)
        ld (FrW),a
        ld a,WinCapH
        ld (FrH),a
        ld hl,$ffff
        ld (FrPat),hl
        call DevFillRect
        call WndIsFront
        jr z,WdfCapDone
        ld a,(WinY)
        inc a
        ld (FrY),a
        ld a,WinCapH-2
        ld (FrH),a
        ld hl,0
        ld (FrPat),hl
        call DevFillRect
        ld a,(WinY)
        inc a
        ld (PxRow),a
        ld b,WinCapH-2
WdfCapEdge:
        push bc
        ld a,(WinX)
        ld c,a
        ld a,(PxRow)
        call AddrAt
        ld a,(hl)
        or $80
        ld (hl),a
        ld a,(WinW)
        dec a
        ld e,a
        ld d,0
        add hl,de
        ld a,(hl)
        or $01
        ld (hl),a
        ld a,(PxRow)
        inc a
        ld (PxRow),a
        pop bc
        djnz WdfCapEdge
        ld a,(WinX)
        ld (FrX),a
        ld a,(WinW)
        ld (FrW),a
WdfCapDone:
        ld a,(WinX)
        ld (FrX),a
        ld a,(WinY)
        add a,WinCapH
        ld (FrY),a
        ld a,(WinW)
        ld (FrW),a
        ld a,(WinH)
        sub WinCapH
        ld (FrH),a
        ld hl,0
        ld (FrPat),hl
        call DevFillRect
        ld a,(WinY)
        ld c,a
        ld a,(WinH)
        add a,c
        dec a
        ld (FrY),a
        ld a,1
        ld (FrH),a
        ld hl,$ffff
        ld (FrPat),hl
        jp DevFillRect

; ZXDesk's original static About window application (WdAbout).
WdAbout:
        ld a,(WinY)
        add a,WinCapH+3
        ld (PxRow),a
        ld hl,AboutLines
WdaLoop:
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,d
        or e
        ret z
        push hl
        ld a,(WinX)
        add a,2
        ld c,a
        ex de,hl
        call PrintStrPx
        ld a,(PxRow)
        add a,9
        ld (PxRow),a
        pop hl
        jr WdaLoop

; Original ZXDesk title cap rendering via its pixel-font interface.
WdText:
        call WndIsFront
        ld a,1
        jr z,WdtInv
        xor a
WdtInv:
        ld (PrintInv),a
        ld a,(WinY)
        inc a
        ld (PxRow),a
        ld a,(WinX)
        add a,2
        ld c,a
        ld hl,(WinTitle)
        call PrintStrPx
        xor a
        ld (PrintInv),a
        ret

; Original ZXDesk z-order shuffle.
WndRaise:
        ld b,a
        ld a,(WndZ)
        cp b
        ret z
        ld hl,WndZ
        ld c,0
WrFind:
        ld a,(hl)
        cp b
        jr z,WrFound
        inc hl
        inc c
        ld a,c
        ld de,WndCount
        ld a,(de)
        cp c
        jr nz,WrFind
        ret
WrFound:
        ld a,c
        or a
        ret z
WrShift:
        dec hl
        ld a,(hl)
        inc hl
        ld (hl),a
        dec hl
        dec c
        jr nz,WrShift
        ld (hl),b
        ret

; Window record synchronization; ZX-UX app state is separate.
WndFlush:
        ld a,(WndCur)
        call WndRecAt
        ex de,hl
        ld hl,WinRec
        ld bc,WNDRECSZ
        ldir
        ret

; Original ZXDesk window hit-test, with a ZX-UX-owned record table.
; Input: B=byte column, C=pixel row; output A=control id.
WndHitTest:
        ld a,b
        ld (WhtCol),a
        ld a,c
        ld (WhtRow),a
        call WndFlush
        ld a,(WndCount)
        or a
        jr z,WhtNone
        ld b,a
        ld c,0
WhtLoop:
        push bc
        ld e,c
        ld d,0
        ld hl,WndZ
        add hl,de
        ld a,(hl)
        ld (WndHit),a
        call WndRecAt
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld a,(WhtCol)
        sub e
        jr c,WhtNext
        cp c
        jr nc,WhtNext
        ld a,(WhtRow)
        sub d
        jr c,WhtNext
        cp b
        jr nc,WhtNext
        cp WinCapH
        jr nc,WhtBody
        ld d,a
        ld a,(WhtCol)
        sub e
        jr nz,WhtTitle
        ld a,d
        or a
        jr z,WhtTitle
        cp 9
        jr nc,WhtTitle
        ld a,1
        jr WhtDone
WhtTitle:
        ld a,2
        jr WhtDone
WhtBody:
        ld d,a
        add a,8
        cp b
        jr c,WhtScrollTest
        ld a,(WhtCol)
        sub e
        inc a
        cp c
        jr c,WhtScrollTest
        ld a,8
        jr WhtDone
WhtScrollTest:
        ld a,(WhtCol)
        sub e
        add a,2
        cp c
        jr nz,WhtInterior
        ld a,9
        jr WhtDone
WhtInterior:
        ld a,3
WhtDone:
        pop bc
        ret
WhtNext:
        pop bc
        inc c
        djnz WhtLoop
WhtNone:
        xor a
        ret

WndIsFront:
                ld      a,(WndZ)
                ld      hl,WndCur
                cp      (hl)
                ret

        section data
; Original 13-byte WinRec record with platform-owned pointers initially null.
WinRec:
WinX:           db      4
WinY:           db      32
WinW:           db      24
WinH:           db      88
WinTitle:       dw      0
WinBufP:        dw      0
WinApp:         dw      0
WinStateP:      dw      0
WinOldX:       db      4
WinOldY:       db      32
WinMoved:      db      0
CloseBox:       db      $FF,$81,$BD,$BD,$BD,$BD,$81,$FF
AboutLines: dw TxtAb1, TxtAb2, TxtAb3, TxtAb4,0
TxtAb1: db 'ZX DESK',0
TxtAb2: db '48K, Z80',0
TxtAb3: db 'MONOCHROME',0
TxtAb4: db 'PIXEL EXACT',0
WndZ:           db      0,1,2,3
WndCount:       db      1
WndHit:         db      0
WhtCol:         db      0
WhtRow:         db      0
WndCur:         db      0

        section bss
WndTab:         ds      4*WNDRECSZ