; ZXDesk directory functions use ZX-UX filesystem calls.
; Directory records in ZX-UX are ten bytes (inode + eight-byte name).
        section text
        global ApiStSelect
        global ApiStIdent
        global ApiStCaps
        global ApiStDir
        global ApiStOpen
        global ApiStRead
        global ApiStWrite
        global ApiStClose
        extern zx_syscall
ApiStSelect:
        cp 2
        jr nc,StBad
        ld (StBackend),a
        or a
        ret
StBad:
        scf
        ret
ApiStIdent:
        ld a,(StBackend)
        ret
ApiStCaps:
        ld a,1
        ret
; A=one-based? Original routine uses zero-based entry index.
; Select root or /bin; returns HL=name, carry on end.
ApiStDir:
        ld (StWanted),a
        ld a,(StBackend)
        or a
        ld hl,StRoot
        jr z,SdPath
        ld hl,StBin
SdPath:
        ld de,0
        ld a,5
        call zx_syscall
        ret c
        ld (StFD),hl
        xor a
        ld (StIx),a
SdNext:
        ld hl,(StFD)
        ld de,StEntry
        ld bc,10
        ld a,3
        call zx_syscall
        jr c,SdEnd
        ld a,l
        cp 10
        jr nz,SdEnd
        ld hl,(StEntry)
        ld a,h
        or l
        jr z,SdNext
        ld a,(StIx)
        ld hl,StWanted
        cp (hl)
        jr z,SdFound
        ld hl,StIx
        inc (hl)
        jr SdNext
SdFound:
        ld hl,(StFD)
        ld a,6
        call zx_syscall
        ld hl,StEntry+2
        ld de,StName
        ld bc,8
        ldir
        xor a
        ld (StName+8),a
        ld hl,StName
        or a
        ret
SdEnd:
        ld hl,(StFD)
        ld a,6
        call zx_syscall
        scf
        ret
; HL=name, B=mode, compatible with ZX-UX kernel open/create.
ApiStOpen:
        ld a,b
        or a
        jr nz,StCreate
        ld de,0
        ld a,5
        call zx_syscall
        ret
StCreate:
        ld de,$01b6
        ld a,8
        call zx_syscall
        ret
; A=fd, HL=buffer, BC=count; out BC=count (or carry).
ApiStRead:
        ld e,l
        ld d,h
        ld l,a
        ld h,0
        ld a,3
        call zx_syscall
        ld b,h
        ld c,l
        ret
ApiStWrite:
        ld e,l
        ld d,h
        ld l,a
        ld h,0
        ld a,4
        call zx_syscall
        ld b,h
        ld c,l
        ret
ApiStClose:
        ld l,a
        ld h,0
        ld a,6
        jp zx_syscall
        section data
StBackend: db 0
StWanted: db 0
StIx: db 0
StFD: dw 0
StRoot: db '/',0
StBin: db '/bin',0
StEntry: ds 10
StName: ds 9
