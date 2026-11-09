; Port of Damian Cooper's original ZXDesk clock logic (clock.inc).
; Only the private IM2 counter and graphics API are redirected to ZX-UX.
        section text
        global ClkInit
        global ClkService
        global ClkDraw
        global ClkKey
        extern zx_syscall
        extern PrintStrPx
        extern PrintInv
        extern PxRow
        extern WinX
        extern WinY
CLKFRAC48 equ 8
CLKROW equ 4
ClkInit:
        ld a,12
        ld (ClkH),a
        xor a
        ld (ClkM),a
        ld (ClkS),a
        ld (ClkFrames),a
        ld (ClkFrac),a
        ld (ClkField),a
        ld a,50
        ld (ClkNeed),a
        ld a,CLKFRAC48
        ld (ClkFracAdd),a
        ld a,38
        call zx_syscall
        ld (ClkLast),hl
        ret

; ZXDesk interrupt-delta accumulator, supplied by ZX-UX _ticks.
ClkService:
ClkTick:
        ld a,38
        call zx_syscall
        ld de,(ClkLast)
        push hl
        or a
        sbc hl,de
        pop de
        ret z
        ld (ClkLast),de
ClkAccum:
        ld a,(ClkFrames)
        inc a
        ld (ClkFrames),a
        ld b,a
        ld a,(ClkNeed)
        cp b
        jr nz,ClkNoSec
        push hl
        call ClkSecond
        pop hl
ClkNoSec:
        dec hl
        ld a,h
        or l
        jr nz,ClkAccum
        ret
ClkSecond:
        ld hl,TickSecs
        inc (hl)
        xor a
        ld (ClkFrames),a
        ld a,(ClkFrac)
        ld b,a
        ld a,(ClkFracAdd)
        add a,b
        cp 100
        jr c,ClkNoExtra
        sub 100
        ld (ClkFrac),a
        ld a,51
        ld (ClkNeed),a
        jr ClkBump
ClkNoExtra:
        ld (ClkFrac),a
        ld a,50
        ld (ClkNeed),a
ClkBump:
        ld hl,ClkS
        inc (hl)
        ld a,(hl)
        cp 60
        ret c
        ld (hl),0
        ld a,1
        ld (ClkDirty),a
        ld hl,ClkM
        inc (hl)
        ld a,(hl)
        cp 60
        ret c
        ld (hl),0
        ld hl,ClkH
        inc (hl)
        ld a,(hl)
        cp 24
        ret c
        ld (hl),0
        ret

; Original ZXDesk clock-face formatting and field inversion.
ClkDraw:
        ld hl,ClkText
        ld a,(ClkH)
        call ClkPut2
        ld (hl),':'
        inc hl
        ld a,(ClkM)
        call ClkPut2
        ld (hl),0
        xor a
        ld (PrintInv),a
        ld a,(WinY)
        add a,WinCapH+CLKROW
        ld (PxRow),a
        ld a,(WinX)
        add a,2
        ld c,a
        ld hl,ClkText
        call PrintStrPx
        ld a,(ClkField)
        ld b,a
        add a,a
        add a,b
        ld e,a
        ld d,0
        ld hl,ClkText
        add hl,de
        ld a,(hl)
        ld (ClkPair),a
        inc hl
        ld a,(hl)
        ld (ClkPair+1),a
        ld a,(WinX)
        add a,2
        add a,e
        ld c,a
        ld a,(WinY)
        add a,WinCapH+CLKROW
        ld (PxRow),a
        ld a,1
        ld (PrintInv),a
        ld hl,ClkPair
        call PrintStrPx
        xor a
        ld (PrintInv),a
        ret

ClkPut2:
        ld b,'0'-1
ClkP2T:
        inc b
        sub 10
        jr nc,ClkP2T
        add a,10
        ld (hl),b
        inc hl
        add a,'0'
        ld (hl),a
        inc hl
        ret

; Same ZXDesk field-switch and set controls; ZX-UX arrows are 8..11.
ClkKey:
        cp 8
        jr nz,CkNotL
        ld a,(ClkField)
        or a
        ret z
        dec a
        ld (ClkField),a
        ret
CkNotL:
        cp 9
        jr nz,CkNotR
        ld a,(ClkField)
        cp 1
        ret nc
        inc a
        ld (ClkField),a
        ret
CkNotR:
        cp 11
        jr nz,CkNotU
        ld c,1
	jr ClkAdjust
CkNotU:
        cp 10
        ret nz
        ld c,0
ClkAdjust:
        ld a,(ClkField)
        ld hl,ClkH
        or a
        jr z,CkaGot
        inc hl
        dec a
        jr z,CkaGot
        inc hl
CkaGot:
        ld b,60
        ld a,(ClkField)
        or a
        jr nz,CkaMod
        ld b,24
CkaMod:
        ld a,c
        or a
        jr z,CkaDown
        ld a,(hl)
        inc a
        cp b
        jr c,CkaSet
        xor a
        jr CkaSet
CkaDown:
        ld a,(hl)
        or a
        jr nz,CkaDec
        ld a,b
CkaDec:
        dec a
CkaSet:
        ld (hl),a
        xor a
        ld (ClkFrames),a
        ld (ClkS),a
        ret

WinCapH equ 10
        section data
ClkText: db 0,0,0,0,0,0
ClkPair: db 0,0,0
ClkH: db 12
ClkM: db 0
ClkS: db 0
ClkField: db 0
ClkFrames: db 0
ClkNeed: db 50
ClkFrac: db 0
ClkFracAdd: db CLKFRAC48
ClkDirty: db 0
ClkLast: dw 0
TickSecs: db 0