; ZXDesk original Settings record and D2 settings panel (settings.inc,
; dlgset.inc). Damian Cooper, MIT. Pointer/ULA hooks are deliberately
; excluded: ZX-UX owns those devices, and the panel remains modal.
        section text
        global SetDefaults
        global SetLoad
        global SetSave
        global SetApply
        global SetLattice
        global DlgOpen
        global DlgClose
        global DlgKey
        global DlgUp
        extern ApiStSelect
        extern ApiStIdent
        extern ApiStOpen
        extern ApiStRead
        extern ApiStWrite
        extern ApiStClose
        extern PnlPaint
        extern PnlKey
        extern PnlX
        extern PnlY
        extern PnlW
        extern PnlH
        extern PnlRow0
        extern PnlRows
        extern PnlTab
        extern PnlTitle
        extern PnlAfter
        extern PnlFocus
        extern WndRepaintAll
SETMAGIC equ $5a
SETVERSION equ 3
SETSIZE equ 8
DLGX equ 9
DLGY equ 40
DLGW equ 16
DLGH equ 68
DLGROW0 equ DLGY+10
DLGLINES equ 7
PT_ACTION equ 1
PT_CYCLE equ 2
SetDefaults:
        ld a,SETMAGIC
        ld (SetRec),a
        ld a,SETVERSION
        ld (SetRec+1),a
        ld a,1
        ld (SetSpeed),a
        ld (SetInvertY),a
        ld (SetLattice),a
        ld (SetKeyPtr),a
        ld (SetSound),a
        xor a
        ld (SetRec+7),a
        ret
SetLoad:
        ld hl,SetName
        ld b,0
        call ApiStOpen
        jr c,SetlNone
        ld (SetHandle),a
        ld hl,SetRec
        ld bc,SETSIZE
        ld a,(SetHandle)
        call ApiStRead
        ld (SetGot),bc
        ld a,(SetHandle)
        call ApiStClose
        ld hl,(SetGot)
        ld a,h
        or a
        jr nz,SetlBad
        ld a,l
        cp SETSIZE
        jr nz,SetlBad
        ld a,(SetRec)
        cp SETMAGIC
        jr nz,SetlBad
        ld a,(SetRec+1)
        cp SETVERSION
        jr nz,SetlBad
        or a
        ret
SetlBad:
SetlNone:
        call SetDefaults
        scf
        ret
SetSave:
        call ApiStIdent
        ld (SetWasBackend),a
        xor a
        call ApiStSelect
        ld a,SETMAGIC
        ld (SetRec),a
        ld a,SETVERSION
        ld (SetRec+1),a
        ld hl,SetName
        ld b,1
        call ApiStOpen
        jr c,SetsOpenFail
        ld (SetHandle),a
        ld hl,SetRec
        ld bc,SETSIZE
        ld a,(SetHandle)
        call ApiStWrite
        jr c,SetsWriteFail
        ld (SetGot),bc
        ld a,(SetHandle)
        call ApiStClose
        jr c,SetsFail
        ld hl,(SetGot)
        ld a,h
        or a
        jr nz,SetsFail
        ld a,l
        cp SETSIZE
        jr nz,SetsFail
        ld a,(SetWasBackend)
        call ApiStSelect
        or a
        ret
SetsWriteFail:
        ld a,(SetHandle)
        call ApiStClose
SetsOpenFail:
SetsFail:
        ld a,(SetWasBackend)
        call ApiStSelect
        scf
        ret
; Clamp the original preference record. Private acceleration, banking,
; beeper and self-patching ULA hooks are not installed into ZX-UX.
SetApply:
        ld a,(SetSpeed)
        cp 3
        jr c,SetaSpeedOk
        ld a,1
        ld (SetSpeed),a
SetaSpeedOk:
        ld a,(SetInvertY)
        cp 2
        jr c,SetaInvOk
        ld a,1
        ld (SetInvertY),a
SetaInvOk:
        ld a,(SetLattice)
        cp 2
        jr c,SetaDeskOk
        ld a,1
        ld (SetLattice),a
SetaDeskOk:
        ld a,(SetKeyPtr)
        cp 3
        jr c,SetaKeyOk
        ld a,1
        ld (SetKeyPtr),a
SetaKeyOk:
        ld a,(SetSound)
        cp 2
        ret c
        ld a,1
        ld (SetSound),a
        ret
DlgOpen:
        ld a,1
        ld (DlgUp),a
        ld a,DLGX
        ld (PnlX),a
        ld a,DLGY
        ld (PnlY),a
        ld a,DLGW
        ld (PnlW),a
        ld a,DLGH
        ld (PnlH),a
        ld a,DLGROW0
        ld (PnlRow0),a
        ld a,DLGLINES
        ld (PnlRows),a
        ld hl,DlgRows
        ld (PnlTab),hl
        ld hl,TxtDlgTitle
        ld (PnlTitle),hl
        ld hl,DlgAfter
        ld (PnlAfter),hl
        xor a
        ld (PnlFocus),a
        jp PnlPaint
DlgClose:
        ld a,(DlgUp)
        or a
        ret z
        xor a
        ld (DlgUp),a
        ld hl,0
        ld (PnlAfter),hl
        jp WndRepaintAll
DlgKey:
        jp PnlKey
DlgAfter:
        ld a,(DlgUp)
        or a
        ret z
        call SetApply
        call WndRepaintAll
        jp PnlPaint
DlgSave:
        call SetSave
        ld a,0
        jr nc,DlgsOk
        ld a,1
DlgsOk:
        ld (DlgResult),a
        ret
        section data
DlgRows:
        db PT_CYCLE
        dw TxtDlgSpeed,SetSpeed
        db 3
        dw NmSpeed
        db PT_CYCLE
        dw TxtDlgInv,SetInvertY
        db 2
        dw NmOffOn
        db PT_CYCLE
        dw TxtDlgLat,SetLattice
        db 2
        dw NmDesk
        db PT_CYCLE
        dw TxtDlgKeys,SetKeyPtr
        db 3
        dw NmKeys
        db PT_CYCLE
        dw TxtDlgSnd,SetSound
        db 2
        dw NmOffOn
        db PT_ACTION
        dw TxtDlgSave,DlgSave
        db 0
        dw 0
        db PT_ACTION
        dw TxtDlgDone,DlgClose
        db 0
        dw 0
TxtDlgTitle: db 'SETTINGS',0
TxtDlgSpeed: db 'SPEED',0
TxtDlgInv: db 'INVERT Y',0
TxtDlgLat: db 'DESKTOP',0
TxtDlgKeys: db 'KEY PTR',0
TxtDlgSnd: db 'SOUND',0
TxtDlgSave: db 'SAVE',0
TxtDlgDone: db 'DONE',0
TxtOff: db 'OFF',0
TxtOn: db 'ON',0
TxtSlow: db 'SLOW',0
TxtMed: db 'MED',0
TxtFast: db 'FAST',0
TxtExt: db 'EXT',0
TxtAll: db 'ALL',0
TxtPlain: db 'PLAIN',0
TxtDots: db 'DOTS',0
NmOffOn: dw TxtOff,TxtOn
NmSpeed: dw TxtSlow,TxtMed,TxtFast
NmKeys: dw TxtOff,TxtExt,TxtAll
NmDesk: dw TxtPlain,TxtDots
DlgUp: db 0
DlgResult: db 0
SetName: db 'SETTINGS',0
SetWasBackend: db 0
SetHandle: db 0
SetGot: dw 0
SetRec: db SETMAGIC,SETVERSION
SetSpeed: db 1
SetInvertY: db 1
SetLattice: db 1
SetKeyPtr: db 1
SetSound: db 1
        db 0
