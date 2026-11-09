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

CMDPANEW equ 13
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
        ld a,(CmdCol)
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
        ld a,(CmdKeyCh)
        cp 8
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
        cp 9
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
        cp 10
        jr nz,CmkNotL
        xor a
        ld (CmdActive),a
        ret
CmkNotL:
        cp 11
        ret nz
        ld a,1
        ld (CmdActive),a
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
TxtCmdRoot: db 'ROOT',0
TxtCmdBin: db 'BIN',0
TxtCmdBlank: db ' ',0
