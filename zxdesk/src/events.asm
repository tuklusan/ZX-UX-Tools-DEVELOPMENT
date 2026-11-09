; ZXDesk event ring, ported from Damian Cooper's src/events.inc.
; ZX-UX supplies input; no direct ROM, ports, or interrupt ownership.
; MIT: see zxdesk/NOTICE.txt.
        section text
        global EvPost
        global EvNext

EVSLOTS         equ     16
EVMASK          equ     EVSLOTS-1

EV_PTRMOVE      equ     1               ; B = PtrX, C = PtrY
EV_BTNDOWN      equ     2               ; B = button mask
EV_BTNUP        equ     3
EV_KEY          equ     4               ; B = key code
EV_TYPES        equ     4

; A = type, B and C = parameters. Carry set if it was dropped.
EvPost:
                push    bc
                push    af
                ld      a,(EvHead)
                inc     a
                and     EVMASK
                ld      hl,EvTail
                cp      (hl)
                jr      z,EvpFull
                ld      e,a
                ld      a,(EvHead)
                ld      l,a
                ld      h,0
                add     hl,hl
                add     hl,hl
                ld      bc,EvQueue
                add     hl,bc
                pop     af
                ld      (hl),a
                inc     hl
                pop     bc
                ld      (hl),b
                inc     hl
                ld      (hl),c
                ld      a,e
                ld      (EvHead),a
                or      a
                ret
EvpFull:
                pop     af
                pop     bc
                scf
                ret

; Returns A = type, or zero when the queue is empty. B and C carry
; the parameters.
EvNext:
                ld      a,(EvTail)
                ld      hl,EvHead
                cp      (hl)
                jr      z,EvnEmpty
                ld      l,a
                ld      h,0
                add     hl,hl
                add     hl,hl
                ld      bc,EvQueue
                add     hl,bc
                ld      a,(EvTail)
                inc     a
                and     EVMASK
                ld      (EvTail),a
                ld      a,(hl)
                inc     hl
                ld      b,(hl)
                inc     hl
                ld      c,(hl)
                ret
EvnEmpty:
                xor     a
                ret


        section data
EvHead:         defb    0
EvTail:         defb    0
EvLastBtn:      defb    $FF             ; nothing pressed, active low
EvLastX:        defb    120
EvLastY:        defb    90
EvQueue:        defs    EVSLOTS*4
