; Original ZXDesk Calendar from Damian Cooper's src/calendar.inc (MIT).
; Drawing and date arithmetic retained; ZX-UX owns screen/keyboard.
        section text
        global CalState
        global CalInit
        global CalDraw
        global CalKey
        global CalNextDay
        extern ApiWinPrint
        extern ApiWinPrintInv
        extern ApiWinAddr
CALYEAR0 equ 1980
CALYEARS equ 100

CalInit:
        ld a,(TodayY)
        ld (CalYear),a
        ld a,(TodayM)
        ld (CalMonth),a
        ld a,(TodayD)
        ld (CalSel),a
        ret
CalSetLeap:
        ld a,(CalYear)
        call CalLeap
        ld a,0
        jr nz,CslNo
        inc a
CslNo:
        ld (CalLeapY),a
        ret
CalFwd:
        call CalSetLeap
        ld a,(CalMonth)
        call CalMonthLen
        ld b,a
        ld a,(CalSel)
        inc a
        cp b
        jr z,CfSet
        jr c,CfSet
        ld a,1
        ld (CalSel),a
        ld hl,CalMonth
        inc (hl)
        ld a,(hl)
        cp 12
        ret c
        ld (hl),0
        ld hl,CalYear
        inc (hl)
        ld a,(hl)
        cp CALYEARS
        ret c
        dec (hl)
        ld a,11
        ld (CalMonth),a
        ld a,31
CfSet:
        ld (CalSel),a
        ret
CalBack:
        ld a,(CalSel)
        dec a
        jr z,CbPrevMonth
        ld (CalSel),a
        ret
CbPrevMonth:
        ld a,(CalMonth)
        or a
        jr nz,CbSameYear
        ld a,(CalYear)
        or a
        ret z
        dec a
        ld (CalYear),a
        ld a,12
CbSameYear:
        dec a
        ld (CalMonth),a
        call CalSetLeap
        ld a,(CalMonth)
        call CalMonthLen
        ld (CalSel),a
        ret
CalMoveB:
        push bc
        ld a,c
        or a
        jr z,CmbBack
        call CalFwd
        jr CmbNext
CmbBack:
        call CalBack
CmbNext:
        pop bc
        djnz CalMoveB
        ret
CalLeap:
        and 3
        ret
CalMonthLen:
        ld e,a
        ld d,0
        ld hl,CalLens
        add hl,de
        ld a,(hl)
        ld b,a
        ld a,e
        cp 1
        ld a,b
        ret nz
        ld a,(CalLeapY)
        or a
        ld a,b
        ret z
        inc a
        ret
CalFirstDow:
        call CalSetLeap
        ld a,1
        ld (CalDow),a
        xor a
        ld (CalIx),a
CfdYear:
        ld a,(CalIx)
        ld hl,CalYear
        cp (hl)
        jr z,CfdMonths
        call CalLeap
        ld b,1
        jr nz,CfdNotL2
        inc b
CfdNotL2:
        ld a,(CalDow)
        add a,b
        call CalMod7
        ld (CalDow),a
        ld hl,CalIx
        inc (hl)
        jr CfdYear
CfdMonths:
        xor a
        ld (CalIx),a
CfdMonth:
        ld a,(CalIx)
        ld hl,CalMonth
        cp (hl)
        ret z
        call CalMonthLen
        ld b,a
        ld a,(CalDow)
        add a,b
        call CalMod7
        ld (CalDow),a
        ld hl,CalIx
        inc (hl)
        jr CfdMonth
CalMod7:
        cp 7
        ret c
        sub 7
        jr CalMod7
CalNextDay:
        ld a,(TodayY)
        call CalLeap
        ld a,0
        jr nz,CndNotLeap
        inc a
CndNotLeap:
        ld (CalLeapY),a
        ld a,(TodayM)
        call CalMonthLen
        ld b,a
        ld a,(TodayD)
        inc a
        cp b
        jr z,CndSet
        jr c,CndSet
        ld a,1
        ld (TodayD),a
        ld hl,TodayM
        inc (hl)
        ld a,(hl)
        cp 12
        ret c
        ld (hl),0
        ld hl,TodayY
        inc (hl)
        ld a,(hl)
        cp CALYEARS
        ret c
        ld (hl),0
        ret
CndSet:
        ld (TodayD),a
        ret

; Original calendar text/grid painter with 21 columns across.
CalDraw:
        call CalFirstDow
        ld a,(CalDow)
        ld (CalFirst),a
        ld a,(CalMonth)
        call CalMonthLen
        ld (CalLen),a
        ld hl,CalRow
        ld a,(CalMonth)
        ld b,a
        add a,a
        add a,b
        ld e,a
        ld d,0
        push hl
        ld hl,CalNames
        add hl,de
        pop de
        ld bc,3
        ldir
        ex de,hl
        ld (hl),' '
        inc hl
        ld a,(CalYear)
        ld b,a
        ld a,19
        ld c,a
        ld a,80
        add a,b
        cp 100
        jr c,CalCent
        sub 100
        inc c
CalCent:
        ld b,a
        ld a,c
        ld c,0
        push bc
        call CalPut2
        pop bc
        ld a,b
        ld c,0
        call CalPut2
        ld (hl),0
        ld b,3
        call CalPrint
        ld hl,CalDays
        ld de,CalRow
        ld bc,21
        ldir
        ld b,12
        call CalPrint
        xor a
        ld (CalIx),a
CalWeek:
        call CalBuildWeek
        ld a,(CalIx)
        add a,a
        add a,a
        add a,a
        add a,21
        ld b,a
        call CalPrint
        ld hl,CalIx
        inc (hl)
        ld a,(hl)
        cp 6
        jr c,CalWeek
        call CalToday
        jp CalSelDraw
CalBuildWeek:
        ld hl,CalRow
        xor a
        ld (CalCol),a
CalCellLoop:
        ld a,(CalIx)
        ld b,a
        add a,a
        add a,a
        add a,a
        sub b
        ld b,a
        ld a,(CalCol)
        add a,b
        ld b,a
        ld a,(CalFirst)
        ld d,a
        ld a,b
        sub d
        jr c,CalBlank
        inc a
        ld b,a
        ld a,(CalLen)
        cp b
        jr c,CalBlank
        ld a,b
        ld c,1
        call CalPut2
        jr CalCellDone
CalBlank:
        ld (hl),' '
        inc hl
        ld (hl),' '
        inc hl
CalCellDone:
        ld (hl),' '
        inc hl
        ld a,(CalCol)
        inc a
        ld (CalCol),a
        cp 7
        jr c,CalCellLoop
        dec hl
        ld (hl),0
        ret
CalPut2:
        ld b,'0'-1
CalP2T:
        inc b
        sub 10
        jr nc,CalP2T
        add a,10
        ld e,a
        ld a,b
        cp '0'
        jr nz,CalP2Put
        ld a,c
        or a
        ld a,'0'
        jr z,CalP2Put
        ld a,' '
CalP2Put:
        ld (hl),a
        inc hl
        ld a,e
        add a,'0'
        ld (hl),a
        inc hl
        ret
CalPrint:
        ld c,0
        ld hl,CalRow
        jp ApiWinPrint
CalCellAt:
        dec a
        ld b,a
        ld a,(CalFirst)
        add a,b
        call CalDiv7
        add a,a
        add a,a
        add a,a
        add a,21
        ld d,a
        ld a,(CalRem)
        ld b,a
        add a,a
        add a,b
        ld c,a
        ld b,d
        ret
CalSelDraw:
        ld a,(CalSel)
        call CalCellAt
        push bc
        ld a,(CalSel)
        ld hl,CalPair
        ld c,1
        call CalPut2
        ld (hl),0
        pop bc
        ld hl,CalPair
        jp ApiWinPrintInv
CalToday:
        ld a,(TodayY)
        ld hl,CalYear
        cp (hl)
        ret nz
        ld a,(TodayM)
        ld hl,CalMonth
        cp (hl)
        ret nz
        ld a,(TodayD)
        call CalCellAt
        ld a,b
        add a,7
        ld b,a
        call ApiWinAddr
        ld (hl),$ff
        inc hl
        ld (hl),$ff
        ret
CalDiv7:
        ld c,0
CalD7:
        cp 7
        jr c,CalD7Done
        sub 7
        inc c
        jr CalD7
CalD7Done:
        ld (CalRem),a
        ld a,c
        ret

; Key vectors from original Calendar; ZX-UX raw cursor byte mapping.
CalKey:
        cp 10
        jr nz,CkyNotL
        ld b,1
        ld c,0
        jp CalMoveB
CkyNotL:
        cp 11
        jr nz,CkyNotR
        ld b,1
        ld c,1
        jp CalMoveB
CkyNotR:
        cp 8
        jr nz,CkyNotU
        ld b,7
        ld c,0
        jp CalMoveB
CkyNotU:
        cp 9
        jr nz,CkyNotD
        ld b,7
        ld c,1
        jp CalMoveB
CkyNotD:
        cp 13
        ret nz
        ld a,(CalYear)
        ld (TodayY),a
        ld a,(CalMonth)
        ld (TodayM),a
        ld a,(CalSel)
        ld (TodayD),a
        ret

        section data
CalLens: db 31,28,31,30,31,30,31,31,30,31,30,31
CalNames: db 'JANFEBMARAPRMAYJUNJULAUGSEPOCTNOVDEC'
CalDays: db 'MO TU WE TH FR SA SU',0
TodayY: db 0
TodayM: db 0
TodayD: db 1
CalLeapY: db 0
CalDow: db 0
CalFirst: db 0
CalLen: db 0
CalIx: db 0
CalCol: db 0
CalRem: db 0
CalPair: db 0,0,0
CalRow: ds 24
CalState:
CalYear: db 0
CalMonth: db 0
CalSel: db 1
