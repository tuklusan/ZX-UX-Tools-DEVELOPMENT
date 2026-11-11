; =====================================================================
; ZX-UX 48K Sinclair ZX Spectrum Unix.
; Copyright (c) 2026 Supratim Sanyal of SANYALnet Labs.
; Non-commercial use only under the repository LICENSE.
; Commercial use prohibited without separate written permission.
; =====================================================================

; =====================================================================
;  C support calls (ZX-UX v1, for programs from the ZX-UX SDK)
;   38 ticks    HL = 50 Hz frame counter
;   39 screen   HL = 1: the caller owns the screen (no status line, no
;               cursor) -> HL = the 4x8 font; HL = 0: give it back
;  Floats and BEEP need no kernel help: a program calls the ROM's
;  calculator itself, interrupts off, with STKBOT/STKEND/MEM pointing
;  into its own memory and ERR_SP at its own error handler (the kernel
;  never uses the calculator).  See sdk/lib/float.asm.
; =====================================================================

; systicks: 9 bytes. Ask the frame clock. It never takes sick leave.
systicks:
        ld hl,(fticks)
        ld de,0
        jp sysok

; Several programs may own the screen together (each draws its part, as hanoi and queens8 do); a claim
; returns E = 0 for the first owner. The console is silent until the last owner gives the screen back.
; sysscreen: 33 bytes. Share the screen; nobody gets a throne.
sysscreen:
        ld a,h
        or l
        jr z,.rel
        di
        xor a
        ld (cvis),a
        call cxoff              ; the cursor goes.
        ei
        call curbit
        ld hl,scrown
        ld e,(hl)               ; E = the owners before.
        or e
        ld (hl),a
        jr .ok
.rel:   call scrrel
.ok:    ld hl,FONT
        jp sysok

; curbit: A = the running process's bit (slot 0 → 1, 1 → 2...).
; curbit: 11 bytes. Pick the owner bit, not a favorite.
curbit: ld a,(cur)
        ld b,a
        inc b
        xor a
        scf
.l:     rla
        djnz .l
        ret

; scrrel: the running process gives up its share of the screen.
; scrrel: 11 bytes. One screen owner lets go. The last one cleans up.
scrrel: call curbit
        ld hl,scrown
        and (hl)
        ret z
        xor (hl)
        ld (hl),a
        ret nz

; scrfree: the screen goes back to the console: the picture stays (in white on black), the console
; continues on a new bottom line.
; scrfree: 44 bytes. The console gets its screen back. No deposit required.
scrfree:
        ld hl,ttop
        ld b,(hl)
        xor a
        ld (hl),a
        ld (scrown),a
        ld (cdrawn),a
        out (0FEh),a
        ld a,7                  ; ... and stays black (key click, beep): A stray key can still start a
                                ; riot.
        ld (SV_BORDCR),a        ; BORDCR as the ROM's BORDER 0 leaves it.
        ld a,TT_ECHO
        ld (ttymode),a
        ld hl,5800h
        call attr7
        inc b
        dec b
        ld a,TROWS-1
        ld (stdirty),a
        ret nz                  ; the console was at the bottom already.
        ld (trow),a
        jp tnl

; cstrip: may the running process use the console?  Z: yes; NZ: it owns
;   the screen, so the console keeps quiet.  Used while others own the
;   screen, the console takes rows 21-22 below their pictures (programs
;   draw rows 0-20 then) and the status line row 23.
; cstrip: 39 bytes. Decide who may draw. Shared screens need house rules.
cstrip: call curbit
        ld hl,scrown
        and (hl)
        ret nz
        or (hl)
        ret z
        ld a,(ttop)
        or a
        jr nz,attr7.z
        ld a,21
        ld (ttop),a
        ld (stdirty),a
        ld hl,TROWS-1           ; row 22, column 0.
        ld (trow),hl
        call tscrl              ; clear rows 21 and 22.
        call tscrl
        ld hl,5800h+21*32       ; white on black, the status row too.
; attr7: attributes from HL to the end: white on black → A = 0, Z.
; attr7: 10 bytes. Paint the rest of the attributes. White, black, done.
attr7:  ld (hl),7
        inc hl
        ld a,h
        cp 5Bh
        jr nz,attr7
.z:     xor a
        ret

