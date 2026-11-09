; ZXDesk D3 modal Confirm / Save3 / Alert (src/dialog.inc), MIT.
; ZX-UX adaptation: overlay restoration via back-to-front recomposition,
; not private screen save-under or pointer/beeper hardware access.
        section text
        global DlgConfirm
        global DlgSave3
        global DlgAlert
        global DgEscape
        extern PnlPush
        extern PnlPop
        extern PnlPaint
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
        extern DlgUp
        extern DlgClose
        extern WndRepaintAll
DGX equ 10
DGY equ 52
DGW equ 14
DGROW0 equ DGY+10
DGH equ 52
PT_LABEL equ 0
PT_ACTION equ 1
PTSIZE equ 8
DlgConfirm:
        ld (DgLine1),hl
        ld (DgLine2),de
        ld (DgAfter),bc
        ld hl,DgConfirmRows
        ld (DgTab),hl
        ld a,4
        ld (DgCount),a
        ld a,2
        ld (DgFocus),a
        ld hl,TxtDdConfirm
        ld (DgTitle),hl
        jr DgOpen
DlgSave3:
        ld (DgLine1),hl
        ld (DgLine2),de
        ld (DgAfter),bc
        ld hl,DgSaveRows
        ld (DgTab),hl
        ld a,5
        ld (DgCount),a
        ld a,2
        ld (DgFocus),a
        ld hl,TxtDdSave
        ld (DgTitle),hl
        jr DgOpen
DlgAlert:
        ld (DgLine1),hl
        ld (DgLine2),de
        ld hl,0
        ld (DgAfter),hl
        ld hl,DgAlertRows
        ld (DgTab),hl
        ld a,3
        ld (DgCount),a
        ld a,2
        ld (DgFocus),a
        ld hl,TxtDdAlert
        ld (DgTitle),hl
DgOpen:
        ld hl,(DgTab)
        inc hl
        ld de,(DgLine1)
        ld (hl),e
        inc hl
        ld (hl),d
        ld hl,(DgTab)
        ld de,PTSIZE+1
        add hl,de
        ld de,(DgLine2)
        ld (hl),e
        inc hl
        ld (hl),d
        call PnlPush
        ret c
        ld hl,DlgUp
        inc (hl)
        ld hl,DgDepth
        inc (hl)
        ld a,DGX
        ld (PnlX),a
        ld a,DGY
        ld (PnlY),a
        ld a,DGW
        ld (PnlW),a
        ld a,DGH
        ld (PnlH),a
        ld a,DGROW0
        ld (PnlRow0),a
        ld a,(DgCount)
        ld (PnlRows),a
        ld hl,(DgTab)
        ld (PnlTab),hl
        ld hl,(DgTitle)
        ld (PnlTitle),hl
        ld hl,0
        ld (PnlAfter),hl
        ld a,(DgFocus)
        ld (PnlFocus),a
        jp PnlPaint
DgSave:
        ld a,2
        jr DgAnswer
DgDiscard:
        ld a,1
        jr DgAnswer
DgCancel:
        xor a
        jr DgAnswer
DgYes:
        ld a,1
        jr DgAnswer
DgNo:
        xor a
        jr DgAnswer
DgOk:
        xor a
DgAnswer:
        ld (DgResult),a
        call DgClose
        ld hl,(DgAfter)
        ld a,h
        or l
        ret z
        ld a,(DgResult)
        jp (hl)
DgClose:
        ld a,(DgDepth)
        or a
        ret z
        dec a
        ld (DgDepth),a
        ld hl,DlgUp
        dec (hl)
        call PnlPop
        call WndRepaintAll
        ld a,(DlgUp)
        or a
        ret z
        jp PnlPaint
DgEscape:
        ld a,(DgDepth)
        or a
        jp z,DlgClose
        jp DgCancel
        section data
DgConfirmRows:
        db PT_LABEL
        dw 0,0
        db 0
        dw 0
        db PT_LABEL
        dw 0,0
        db 0
        dw 0
        db PT_ACTION
        dw TxtDdNo,DgNo
        db 0
        dw 0
        db PT_ACTION
        dw TxtDdYes,DgYes
        db 0
        dw 0
DgSaveRows:
        db PT_LABEL
        dw 0,0
        db 0
        dw 0
        db PT_LABEL
        dw 0,0
        db 0
        dw 0
        db PT_ACTION
        dw TxtDdCancel,DgCancel
        db 0
        dw 0
        db PT_ACTION
        dw TxtDdDiscard,DgDiscard
        db 0
        dw 0
        db PT_ACTION
        dw TxtDdSaveIt,DgSave
        db 0
        dw 0
DgAlertRows:
        db PT_LABEL
        dw 0,0
        db 0
        dw 0
        db PT_LABEL
        dw 0,0
        db 0
        dw 0
        db PT_ACTION
        dw TxtDdOk,DgOk
        db 0
        dw 0
TxtDdConfirm: db 'CONFIRM',0
TxtDdAlert: db 'NOTICE',0
TxtDdYes: db 'YES',0
TxtDdNo: db 'NO',0
TxtDdOk: db 'OK',0
TxtDdSave: db 'UNSAVED',0
TxtDdCancel: db 'CANCEL',0
TxtDdDiscard: db 'DISCARD',0
TxtDdSaveIt: db 'SAVE',0
DgLine1: dw 0
DgLine2: dw 0
DgAfter: dw 0
DgTab: dw 0
DgTitle: dw 0
DgCount: db 0
DgFocus: db 0
DgResult: db 0
DgDepth: db 0
