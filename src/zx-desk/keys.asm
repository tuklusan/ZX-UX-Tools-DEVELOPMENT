; Original ZXDesk keyboard shortcut viewer (src/shortcut.inc), MIT.
        section text
        global KeysDraw
        extern WinY
        extern WinH
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
        ; Do not let the final eight scanlines cross this window's bottom.
        ; Pixel rows 192+ map into the Spectrum's attribute memory.
        ld a,(WinY)
        ld b,a
        ld a,(WinH)
        add a,b
        ld b,a
        ld a,(KeyRow)
        add a,7
        cp b
        ret nc
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
        db 'EDIT = CAPS SHIFT+1',0
        db 'EDIT 1: NOTE',0
        db 'EDIT 2: CLOCK',0
        db 'EDIT 3: CALENDAR',0
        db 'EDIT 4: FILES',0
        db 'EDIT 5: ABOUT',0
        db 'EDIT 6: KEYS',0
        db 'EDIT 7: CONSOLE',0
        db 'EDIT M: MENU Q: QUIT',0
        db 'EDIT N: NEXT WINDOW',0
        db 'EDIT X: CLOSE WINDOW',0
        db 0
