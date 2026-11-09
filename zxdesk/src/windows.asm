; Original ZXDesk window edge and close-box drawing from src/zxdesk.asm.
; Damian Cooper (MIT); see zxdesk/NOTICE.txt.
; Screen is claimed by the ZX-UX process. No private interrupts or banking.
        section text
        global WinSetGeometry
        global WdEdges
        global WdCloseBox
        global WndRecAt
        global WndIsFront
        extern AddrAt
        extern ScrDown

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
WndZ:           db      0
WndCur:         db      0

        section bss
WndTab:         ds      4*WNDRECSZ
PxRow:         ds      1