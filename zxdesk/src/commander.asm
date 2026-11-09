; ZXDesk Commander two-pane model ported from src/commander.inc.
; Damian Cooper, MIT. The directory device vectors now use ZX-UX.
        section text
        global CmdState
        global CmdInit
        global CmdDraw
        global CmdKey
        extern ApiStIdent
        extern ApiStSelect
        extern ApiStCaps
        extern ApiStDir
        extern ApiWinRows
        extern ApiWinPrintIf
        extern ApiStOpen
        extern ApiStRead
        extern ApiStWrite
        extern ApiStClose
        extern ApiStDelete
        extern ApiOpenFile

CMDPANEW equ 28
CMDHEADY equ 12
CMDLISTY equ 22
WINCAPH equ 10
STCAP_DIR equ 1

CmdInit:
        call ApiStIdent
        ld (CmdBk0),a
        ld a,1
        ld (CmdBk1),a
        xor a
        ld (CmdSel0),a
        ld (CmdSel1),a
        ld (CmdActive),a
        ret
CmdUse:
        ld (CmdPane),a
        or a
        ld a,(CmdBk0)
        jr z,CmuGo
        ld a,(CmdBk1)
CmuGo:
        jp ApiStSelect
CmdSelAt:
        ld a,(CmdPane)
        or a
        ld hl,CmdSel0
        ret z
        ld hl,CmdSel1
        ret
CmdRows:
        call ApiWinRows
        sub CMDLISTY-WINCAPH+2
        jr c,CmrOne
        srl a
        srl a
        srl a
        jr z,CmrOne
        ret
CmrOne:
        ld a,1
        ret
CmdCount:
        call CmdUse
        call ApiStCaps
        and STCAP_DIR
        jr z,CmcNone
        ld b,0
CmcLoop:
        ld a,b
        push bc
        call ApiStDir
        pop bc
        jr c,CmcDone
        inc b
        ld a,b
        cp 99
        jr c,CmcLoop
CmcDone:
        ld a,b
        ret
CmcNone:
        xor a
        ret

; Original CmdDraw and CmdPane1: two independently selected panes.
CmdDraw:
        call ApiStIdent
        ld (CmdWasD),a
        xor a
        call CmdPane1
        ld a,1
        call CmdPane1
        ld a,(CmdWasD)
        jp ApiStSelect
CmdPane1:
        call CmdUse
        ld a,(CmdPane)
        or a
        ld a,0
        jr z,CmpLeft
        ld a,CMDPANEW+2
CmpLeft:
        ld (CmdCol),a
        ld c,a
        call CmdDevName
        ld a,(CmdPane)
        ld b,a
        ld a,(CmdActive)
        cp b
        ld a,0
        jr nz,CmpNotAct
        inc a
CmpNotAct:
        ld b,CMDHEADY-WINCAPH
        call ApiWinPrintIf
        call CmdRows
        ld (CmdN),a
        ld b,a
        call CmdSelAt
        ld a,(hl)
        sub b
        jr c,CmpTop0
        inc a
        jr CmpTopSet
CmpTop0:
        xor a
CmpTopSet:
        ld (CmdTop),a
        xor a
        ld (CmdRow),a
CmpRow:
        ld a,(CmdRow)
        push af
        ld hl,CmdTop
        add a,(hl)
        call ApiStDir
        jr nc,CmpPaint
        ld hl,TxtCmdBlank
CmpPaint:
        ld (CmdName),hl
        pop af
        ld b,a
        add a,a
        add a,a
        add a,a
        add a,CMDLISTY-WINCAPH
        ld (CmdPx),a
        ld a,(CmdTop)
        add a,b
        ld e,a
        call CmdSelAt
        ld a,(hl)
        cp e
        jr nz,CmpPlain
        ld a,(CmdPane)
        ld c,a
        ld a,(CmdActive)
        cp c
        jr nz,CmpPlain
        ld a,1
        jr CmpInv
CmpPlain:
        xor a
CmpInv:
        ld d,a
        ld a,(CmdPx)
        ld b,a
        ld a,(CmdCol)
        ld c,a
        ld hl,(CmdName)
        ld a,d
        call ApiWinPrintIf
        ld hl,CmdRow
        inc (hl)
        ld a,(hl)
        ld hl,CmdN
        cp (hl)
        jr c,CmpRow
        ret
CmdDevName:
        call ApiStIdent
        or a
        ld hl,TxtCmdRoot
        ret z
        ld hl,TxtCmdBin
        ret

; Original keyboard navigation, with filesystem actions handed to ZX-UX.
CmdKey:
        ld (CmdKeyCh),a
        call ApiStIdent
        ld (CmdWasK),a
        ld a,(CmdKeyCh)
        cp 11
        jr nz,CmkNotU
        ld a,(CmdActive)
        ld (CmdPane),a
        call CmdSelAt
        ld a,(hl)
        or a
        ret z
        dec (hl)
        ret
CmkNotU:
        cp 10
        jr nz,CmkNotD
        ld a,(CmdActive)
        call CmdCount
        ld b,a
        ld a,(CmdActive)
        ld (CmdPane),a
        call CmdSelAt
        ld a,(hl)
        inc a
        cp b
        ret nc
        ld (hl),a
        ret
CmkNotD:
        cp 8
        jr nz,CmkNotL
        xor a
        ld (CmdActive),a
        ret
CmkNotL:
        cp 9
        jr nz,CmkNotR
        ld a,1
        ld (CmdActive),a
        ret
CmkNotR:
        cp 13
	jr z,CmdOpen
        cp 'C'
        jr z,CmkCopy
        cp 'c'
        jr z,CmkCopy
        cp 'D'
        jr z,CmkDelete
        cp 'd'
        ret nz
CmkDelete:
        call CmdDelete
        jr CmdRepaint
CmkCopy:
        call CmdCopy
CmdRepaint:
        ld a,(CmdWasK)
        jp ApiStSelect

; Original ZXDesk Commander file selection and operations (commander.inc).
; Paths and handles are translated by the ZX-UX storage adapter.
CmdPicked:
        ld a,(CmdActive)
        call CmdUse
        call CmdSelAt
        ld a,(hl)
        call ApiStDir
        ret c
CmdNameCopy:
        ld de,CmdWork
        ld b,12
CmpkCopy:
        ld a,(hl)
        ld (de),a
        or a
        jr z,CmpkDone
        inc hl
        inc de
        djnz CmpkCopy
        xor a
        ld (de),a
CmpkDone:
        or a
        ret
CmdOpen:
        call CmdPicked
        ret c
        call CmdNameCopy
        ld hl,CmdWork
        call ApiOpenFile
        push af
        ld a,(CmdWasK)
        call ApiStSelect
        pop af
        ret
CmdCopy:
        call CmdPicked
        ret c
        call CmdNameCopy
        ld a,(CmdActive)
        call CmdUse
        ld hl,CmdWork
        ld b,0
        call ApiStOpen
        ret c
        ld (CmdHandle),a
        ld a,(CmdActive)
        xor 1
        call CmdUse
        ld hl,CmdWork
        ld b,1
        call ApiStOpen
        jr c,CmcNoRoom
        ld (CmdOut),a
CmcChunk:
        ld a,(CmdActive)
        call CmdUse
        ld a,(CmdHandle)
        ld hl,CmdBuf
        ld bc,64
        call ApiStRead
        jr c,CmcReadFailed
        ld (CmdGot),bc
        ld a,(CmdActive)
        xor 1
        call CmdUse
        ld bc,(CmdGot)
        ld a,b
        or c
        jr z,CmcCopied
        ld a,(CmdOut)
        ld hl,CmdBuf
        call ApiStWrite
        jr c,CmcWriteFailed
        ld hl,(CmdGot)
        or a
        sbc hl,bc
        jr z,CmcChunk
CmcWriteFailed:
        ld a,(CmdOut)
        call ApiStClose
        jr CmcScrap
CmcReadFailed:
        ld a,(CmdActive)
        xor 1
        call CmdUse
        jr CmcWriteFailed
CmcCopied:
        ld a,(CmdOut)
        call ApiStClose
        jr c,CmcScrap
        call CmcSrcClose
        or a
        ret
CmcNoRoom:
        ; Closing the source remains mandatory when opening the
        ; destination fails; no destination file was created.
        call CmcSrcClose
        scf
        ret
CmcScrap:
        ld hl,CmdWork
        call ApiStDelete
        call CmcSrcClose
        scf
        ret
CmcSrcClose:
        ld a,(CmdActive)
        call CmdUse
        ld a,(CmdHandle)
        jp ApiStClose
CmdDelete:
        call CmdPicked
        ret c
        call CmdNameCopy
        ld a,(CmdActive)
        call CmdUse
        ld hl,CmdWork
        call ApiStDelete
        ret c
        ld a,(CmdActive)
        call CmdCount
        ld b,a
        ld a,(CmdActive)
        ld (CmdPane),a
        call CmdSelAt
        ld a,(hl)
        cp b
        ret c
        ld a,b
        or a
        ret z
        dec a
        ld (hl),a
        ret

        section data
CmdState:
CmdBk0: db 0
CmdBk1: db 1
CmdSel0: db 0
CmdSel1: db 0
CmdActive: db 0
CmdPane: db 0
CmdCol: db 0
CmdPx: db 0
CmdRow: db 0
CmdN: db 0
CmdTop: db 0
CmdName: dw 0
CmdWasD: db 0
CmdKeyCh: db 0
CmdWasK: db 0
CmdHandle: db 0
CmdOut: db 0
CmdGot: dw 0
CmdWork: ds 13
CmdBuf: ds 64
TxtCmdRoot: db 'ROOT',0
TxtCmdBin: db 'BIN',0
TxtCmdBlank: db ' ',0