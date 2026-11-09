; ZXDesk original window record, ordering and repaint model (src/zxdesk.asm).
; SSX1 adaptation: storage for buffers/state belongs to the process,
; not the Spectrum's fixed heap/banks. Damian Cooper, MIT.
        section text
        global WndInit
        global WndOpen
        global WndClose
        global WndCloseNow
        global WndSelect
        global WndRepaintAll
        global WndFocusTo
        global WinGrab
        global WndPaintOne
        extern WndRecAt
        extern WndFlush
        extern WndRaise
        extern WndIsFront
        extern WinDraw
        extern WinRec
        extern WinX
        extern WinY
        extern WinW
        extern WinH
        extern WinTitle
        extern WinBufP
        extern WinApp
        extern WinStateP
        extern WinOldX
        extern WinOldY
        extern WinMoved
        extern WndTab
        extern WndZ
        extern WndCount
        extern WndCur
        extern AppAt
        extern AppCall
        extern AppSave
        extern AppLoad
        extern DrawDesktop
        extern AddrAt
        extern ScrDown

WNDRECSZ equ 15
WNDMAX equ 4
APP_TITLE equ 10
APP_X equ 12
APP_DRAW equ 6
APP_INIT equ 4

WndInit:
        xor a
        ld (WndCount),a
        ld (WndCur),a
        ld (WndUsed),a
        ld hl,0
        ld (WinApp),hl
        ret

; Original WndSelect: swap the live descriptor and application state.
WndSelect:
        ld hl,WndCur
        cp (hl)
        ret z
        push af
        call WndFlush
        pop af
        ld (WndCur),a
        call WndRecAt
        ld de,WinRec
        ld bc,WNDRECSZ
        ldir
        jp AppLoad

; One window per slot. Values in the original WinRec fields are retained;
; the fixed process-local arenas replace ZXDesk's physical heap.
; A = original application kind 0..6.
WndOpen:
        ld (WndWantKind),a
        cp 7
        jp nc,WndNoRoom
        ld a,(WndCount)
        cp WNDMAX
        jp nc,WndNoRoom
        or a
        call nz,WndFlush
        ; Slots are selected from the currently unused part of a bitmap.
        ld a,(WndUsed)
        ld b,a
        ld c,0
WoFind:
        bit 0,b
        jr z,WoGot
        srl b
        inc c
        ld a,c
        cp WNDMAX
        jp nc,WndNoRoom
        jr WoFind
WoGot:
        ld a,c
        ld (WndCur),a
        ld b,a
        or a
        ld a,1
        jr z,WoBitReady
WoBitLoop:
        add a,a
        djnz WoBitLoop
WoBitReady:
        ld b,a
        ld a,(WndUsed)
        or b
        ld (WndUsed),a
        ld a,(WndWantKind)
        call AppAt
        ld (WinApp),hl
        ld de,APP_TITLE
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ex de,hl
        ld (WinTitle),hl
        ex de,hl
        push hl
        inc hl
        inc hl
        ld a,(hl)
        ld (WinW),a
        inc hl
        ld a,(hl)
        ld (WinH),a
        pop hl
        ld a,(WndCount)
        add a,a
        add a,(hl)
        ld c,a
        ld a,(WinW)
        neg
        add a,32
        cp c
        jr nc,WoXok
        ld c,a
WoXok:
        ld a,c
        ld (WinX),a
        ld (WinOldX),a
        inc hl
        ld a,(WndCount)
        add a,a
        add a,a
        add a,a
        add a,(hl)
        ld c,a
        ld a,(WinH)
        neg
        add a,183
        cp c
        jr nc,WoYok
        ld c,a
WoYok:
        ld a,c
        ld (WinY),a
        ld (WinOldY),a
        xor a
        ld (WinMoved),a
        ; Each slot gets its own screen buffer and app state.
        ld a,(WndCur)
        call WndArenaAt
        ld (WinBufP),hl
        ld a,(WndCur)
        call WndStateAt
        ld (WinStateP),hl
        ld c,APP_INIT
        call AppCall
        ; Fresh app state is now in the live copy. Save before changing.
        call AppSave
        ld a,(WndCount)
        or a
        jr z,WoFirst
        ld e,a
        ld d,0
        ld hl,WndZ
        add hl,de
        ld d,h
        ld e,l
        dec hl
        ld b,a
WoShift:
        ld a,(hl)
        ld (de),a
        dec hl
        dec de
        djnz WoShift
WoFirst:
        ld a,(WndCur)
        ld (WndZ),a
        ld hl,WndCount
        inc (hl)
        call WndRepaintAll
        or a
        ret
WndNoRoom:
        scf
        ret

; Original close-on-front / z-list shift (with process-local slot release).
WndCloseNow:
        ld a,1
        ld (WndForce),a
        jp WndClose
WndClose:
        ld a,(WndCount)
        or a
        ret z
        ld a,(WndZ)
        ld (WndClosing),a
        call WndSelect
        ld a,(WndForce)
        or a
        jr nz,WcGo
        ld c,16
        call AppCall
        ret c
WcGo:
        xor a
        ld (WndForce),a
        ld a,(WndCount)
        dec a
        jr z,WcShifted
        ld b,a
        ld hl,WndZ
        ld de,WndZ+1
WcShift:
        ld a,(de)
        ld (hl),a
        inc hl
        inc de
        djnz WcShift
WcShifted:
        ld a,(WndClosing)
        ld b,a
        or a
        ld a,1
        jr z,WcUnflag
WcMaskLoop:
        add a,a
        djnz WcMaskLoop
WcUnflag:
        cpl
        ld b,a
        ld a,(WndUsed)
        and b
        ld (WndUsed),a
        ld hl,WndCount
        dec (hl)
        jr z,WcNoWindow
        ld a,(WndZ)
        ld (WndCur),a
        call WndRecAt
        ld de,WinRec
        ld bc,WNDRECSZ
        ldir
        call AppLoad
        jp WndRepaintAll
WcNoWindow:
        ld hl,0
        ld (WinApp),hl
        ld (WinStateP),hl
        ld (WinBufP),hl
        jp DrawDesktop

WndFocusTo:
        ld (WndFocusSlot),a
        call WndRaise
        jp WndRepaintAll

; Original back-to-front composition via the live record and application
; vectors. Screen buffers are grabbed after each window, in process RAM.
WndRepaintAll:
        call WndFlush
        call DrawDesktop
        ld a,(WndCount)
        or a
        ret z
        ld b,a
WraPaint:
        push bc
        ld a,b
        dec a
        ld e,a
        ld d,0
        ld hl,WndZ
        add hl,de
        ld a,(hl)
        call WndSelect
        call WndPaintOne
        pop bc
        djnz WraPaint
        ret
WndPaintOne:
        call WinDraw
        ld c,APP_DRAW
        call AppCall
        jp WinGrab


; A window surface is composed back-to-front on each change. Keeping
; several full bitmap copies would exceed the ZX-UX process RAM limit.
; Native window descriptors and per-application state remain independent.
WinGrab:
        ret
WndArenaAt:
        ld hl,0
        ret
WndStateAt:
        ld hl,WndStates
        or a
        ret z
        ld de,273
        ld b,a
WsNext:
        add hl,de
        djnz WsNext
        ret

        section data
WndUsed: db 0
WndForce: db 0
WndWantKind: db 0
WndClosing: db 0
WndFocusSlot: db 0
GrabDst: dw 0
GrabY: db 0
GrabCount: db 0
        section bss
WndStates: ds 4*273
