; ZXDesk window API to ZX-UX-owned screen/SSX1 data.
; Window text vectors: HL=text, B=pixel row, C=column.
        section text
        global ApiWinPrint
        global ApiWinPrintInv
        global ApiWinPrintIf
        global ApiWinRows
        global ApiOpenFile
        extern WinX
        extern WinY
        extern WinH
        extern PrintInv
        extern PxRow
        extern PrintStrPx
        extern PrintStrPxHalf
        extern WndOpen
        extern WndRepaintAll
        extern NoteLoadAs
        extern NoteModified
        extern DlgAlert
        extern ApiStOpen
        extern ApiStClose
        extern CmdBuf
        extern zx_syscall
ApiWinPrint:
        xor a
        ld (PrintInv),a
ApiWinPrintGo:
        push hl
        ld a,c
        and 1
        push af
        srl c               ; two native font64 columns per screen byte
        ld a,(WinX)
        inc a
        add a,c
        ld c,a
        ld a,(WinY)
        add a,10
        add a,b
        ld (PxRow),a
        pop af
        pop hl
        or a
        jp nz,PrintStrPxHalf
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
; HL = basename in the selected directory. Notes are exactly 256 bytes, so
; anything else (a directory, a longer or shorter file) is refused up front:
; loading it would truncate it on SAVE. Unsaved note text is never replaced.
ApiOpenFile:
        ld a,(NoteModified)
        or a
        ld de,TxtOfBusy
        jr nz,OfAlert
        push hl
        call ApiCheckNote
        pop hl
        ld de,TxtOfNot
        jr c,OfAlert
        push hl
        xor a
        call WndOpen
        pop hl
        ret c
        call NoteLoadAs
        ld de,TxtOfBad
        jr c,OfAlert
        call WndRepaintAll
        xor a
        ret
OfAlert:
        ex de,hl
        ld de,0
        call DlgAlert
        scf
        ret
; HL = basename. NC only for a regular file of exactly 256 bytes (fstat via
; the Commander scratch buffer: 2-byte inode number, then the 32-byte inode).
ApiCheckNote:
        ld b,0
        call ApiStOpen
        ret c
        ld (ApiFd),a
        ld l,a
        ld h,0
        ld de,CmdBuf
        ld a,28
        call zx_syscall
        push af
        ld a,(ApiFd)
        call ApiStClose
        pop af
        ret c
        ld hl,(CmdBuf+6)
        ld de,256
        or a
        sbc hl,de
        jr nz,AcBad
        ld a,(CmdBuf+3)
        and $40
        ret z
AcBad:
        scf
        ret
        section data
ApiFd: db 0
TxtOfBusy: db 'SAVE OR CLOSE NOTE FIRST',0
TxtOfNot: db 'NOT A 256 BYTE NOTE',0
TxtOfBad: db 'COULD NOT OPEN',0