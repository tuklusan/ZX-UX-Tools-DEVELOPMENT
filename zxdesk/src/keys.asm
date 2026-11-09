; Original ZXDesk keyboard shortcut viewer (src/shortcut.inc), MIT.
        section text
        global KeysDraw
        extern WinY
        extern WinX
        extern PxRow
        extern PrintInv
        extern PrintStrPx
KeysDraw:
        ld a,(WinY)
        add a,12
        ld (KeyRow),a
        ld hl,KeysText
KdLoop:
        ld a,(hl)
        or a
        ret z
        push hl
        ld a,(KeyRow)
        ld (PxRow),a
        ld a,(WinX)
        inc a
        ld c,a
        pop hl
        push hl
        xor a
        ld (PrintInv),a
        call PrintStrPx
        pop hl
KdSkip:
        ld a,(hl)
        inc hl
        or a
        jr nz,KdSkip
        ld a,(KeyRow)
        add a,8
        ld (KeyRow),a
        jr KdLoop
        section data
KeyRow: db 0
KeysText:
        db 'NEW NOTE',0
        db 'FILES',0
        db 'SAVE',0
        db 'CLOSE',0
        db 'NEXT WINDOW',0
        db 'CLOCK',0
        db 'CALENDAR',0
        db 'DESKTOP',0
        db 'SETTINGS',0
        db 'ABOUT',0
        db 0
