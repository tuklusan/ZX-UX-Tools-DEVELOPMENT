; ZXDesk command console. It is an original-app-model window, not a new
; operating system or /bin/sh. Files are handled by the ZX-UX syscalls.
; Deliberately no fork/exec, hardware polling, or direct TTY output.
        section text
        global TermState
        global TermInit
        global TermDraw
        global TermKey
        extern ApiWinPrint
        extern ApiWinPrintInv
        extern zx_syscall

TERMROWS equ 8
TERMWIDTH equ 28
TERMLINE equ 26
; Console has one 269-byte record, shared by its single window.
TermInit:
        xor a
        ld hl,TermState
        ld (hl),a
        ld de,TermState+1
        ld bc,TERMSTSZ-1
        ldir
        ld a,'/'
        ld (TermCwd),a
        ld hl,TextGreeting
        call TermSay
        ld hl,TextHint
        jp TermSay

TermDraw:
        ld hl,TermRows+2*TERMWIDTH
        xor a
        ld (TermY),a
        ld d,6
TdLoop:
        push de
        push hl
        ld a,(TermY)
        ld b,a
        ld c,0
        call ApiWinPrint
        pop hl
        ld de,TERMWIDTH
        add hl,de
        ld a,(TermY)
        add a,8
        ld (TermY),a
        pop de
        dec d
        jr nz,TdLoop
        ld hl,TextPrompt
        ld b,48
        ld c,0
        call ApiWinPrint
        ld hl,TermInput
        ld b,48
        ld c,2
        call ApiWinPrint
        ld hl,TextCaret
        ld a,(TermLen)
        add a,2
        ld c,a
        ld b,48
        jp ApiWinPrintInv

; A complete command line is run only when ENTER arrives.
TermKey:
        cp 13
        jr z,TkEnter
        cp 12
        jr z,TkBack
        cp 8
        ret z
        cp 9
        ret z
        cp 10
        ret z
        cp 11
        ret z
        cp ' '
        ret c
        cp 127
        ret nc
        ld (TermChar),a
        ld a,(TermLen)
        cp TERMLINE-1
        ret nc
        ld e,a
        ld d,0
        ld hl,TermInput
        add hl,de
        ld a,(TermChar)
        ld (hl),a
        inc hl
        ld (hl),0
        ld hl,TermLen
        inc (hl)
        ret
TkBack:
        ld a,(TermLen)
        or a
        ret z
        dec a
        ld (TermLen),a
        ld e,a
        ld d,0
        ld hl,TermInput
        add hl,de
        ld (hl),0
        ret
TkEnter:
        ld hl,TextPrompt
        call TermPutStr
        ld hl,TermInput
        call TermPutStr
        call TermNewline
        call TermParse
        call TermDispatch
        xor a
        ld (TermLen),a
        ld (TermInput),a
        ret

; The eight 27-character output lines are scrolled inside the application
; state. Nothing is written to the shared ZX-UX terminal screen.
TermNewline:
        ld hl,TermRows+TERMWIDTH
        ld de,TermRows
        ld bc,TERMWIDTH*(TERMROWS-1)
        ldir
        xor a
        ld hl,TermRows+TERMWIDTH*(TERMROWS-1)
        ld (hl),a
        ld de,TermRows+TERMWIDTH*(TERMROWS-1)+1
        ld bc,TERMWIDTH-1
        ldir
        ld (TermCol),a
        ret
TermPutChar:
        cp 13
        ret z
        cp 10
	jr z,TermNewline
        cp ' '
        ret c
        cp 127
        ret nc
        ld (TermChar),a
        ld a,(TermCol)
        cp TERMWIDTH-1
        call nc,TermNewline
        ld a,(TermCol)
        ld e,a
        ld d,0
        ld hl,TermRows+TERMWIDTH*(TERMROWS-1)
        add hl,de
        ld a,(TermChar)
        ld (hl),a
        inc hl
        ld (hl),0
        ld hl,TermCol
        inc (hl)
        ret
TermPutStr:
        ld a,(hl)
        or a
        ret z
        push hl
        call TermPutChar
        pop hl
        inc hl
        jr TermPutStr
TermSay:
        call TermPutStr
	jr TermNewline

; Split command from its optional argument in the existing input buffer.
TermParse:
        ld hl,TermInput
TpWord:
        ld a,(hl)
        or a
        jr z,TpDone
        cp ' '
        jr z,TpBreak
        inc hl
        jr TpWord
TpBreak:
        ld (hl),0
        inc hl
TpSpaces:
        ld a,(hl)
        cp ' '
        jr nz,TpDone
        inc hl
        jr TpSpaces
TpDone:
        ld (TermArg),hl
        ret
; HL=user word, DE=command name; Z if exactly equal.
TermEqual:
        ld a,(de)
        cp (hl)
        ret nz
        or a
        ret z
        inc hl
        inc de
        jr TermEqual
TermDispatch:
        ld a,(TermInput)
        or a
        ret z
        ld hl,TermInput
        ld de,CmdHelp
        call TermEqual
	jr z,TermHelp
        ld hl,TermInput
        ld de,CmdPwd
        call TermEqual
	jr z,TermPwd
        ld hl,TermInput
        ld de,CmdLs
        call TermEqual
        jp z,TermLs
        ld hl,TermInput
        ld de,CmdCd
        call TermEqual
        jp z,TermCd
        ld hl,TermInput
        ld de,CmdCat
        call TermEqual
        jp z,TermCat
        ld hl,TermInput
        ld de,CmdEcho
        call TermEqual
	jr z,TermEcho
        ld hl,TermInput
        ld de,CmdRm
        call TermEqual
        jp z,TermRm
        ld hl,TermInput
        ld de,CmdMkdir
        call TermEqual
        jp z,TermMkdir
        ld hl,TermInput
        ld de,CmdClear
        call TermEqual
	jr z,TermClear
        ld hl,TextUnknown
        jp TermSay
TermHelp:
        ld hl,TextHelp1
        call TermSay
        ld hl,TextHelp2
        jp TermSay
TermPwd:
        ld hl,TermCwd
        jp TermSay
TermEcho:
        ld hl,(TermArg)
        jp TermSay
TermClear:
        xor a
        ld hl,TermRows
        ld (hl),a
        ld de,TermRows+1
        ld bc,TERMROWS*TERMWIDTH-1
        ldir
        ld (TermCol),a
        ret

; Build a process-local absolute path. No kernel chdir: GUI applications
; must not silently inherit a console window's working directory.
TermBuildPath:
        ld (TermArgSaved),hl
        ld a,(hl)
        cp '/'
        jr z,TbpAbs
        ld hl,TermCwd
        ld de,TermPath
        ld b,39
        call TermPathCopy
        ret c
        ld a,(TermCwd+1)
        or a
        jr z,TbpName
        ld a,'/'
        ld (de),a
        inc de
        dec b
        jr z,TbpLong
TbpName:
        ld hl,(TermArgSaved)
	jr TermPathCopy
TbpAbs:
        ld de,TermPath
        ld b,39
TermPathCopy:
        ld a,(hl)
        or a
        jr z,TpcDone
        ld (de),a
        inc de
        inc hl
        djnz TermPathCopy
TbpLong:
        scf
        ret
TpcDone:
        ld (de),a
        or a
        ret
TermNeedPath:
        ld hl,(TermArg)
        ld a,(hl)
        or a
        jr z,TnpMissing
        call TermBuildPath
        ret nc
        ld hl,TextLong
        jr TnpError
TnpMissing:
        ld hl,TextArg
TnpError:
        call TermSay
        scf
        ret

; ls reads actual ZX-UX ten-byte directory entries through open/read.
TermLs:
        ld hl,(TermArg)
        ld a,(hl)
        or a
        jr nz,TlsPath
        ld hl,TermCwd
TlsPath:
        call TermBuildPath
        jp c,TermError
        ld hl,TermPath
        ld de,0
        ld a,5
        call zx_syscall
        jp c,TermError
        ld (TermFD),hl
TlsRead:
        ld hl,(TermFD)
        ld de,TermEntry
        ld bc,10
        ld a,3
        call zx_syscall
        jr c,TlsEnd
        ld a,l
        cp 10
        jr nz,TlsEnd
        ld hl,(TermEntry)
        ld a,h
        or l
        jr z,TlsRead
        ld hl,TermEntry+2
        ld de,TermName
        ld bc,8
        ldir
        xor a
        ld (TermName+8),a
        ld hl,TermName
        call TermSay
        jr TlsRead
TlsEnd:
        ld hl,(TermFD)
        ld a,6
        jp zx_syscall

TermCd:
        ld hl,(TermArg)
        ld a,(hl)
        or a
        jr nz,TcdArg
        ld hl,TermRoot
        jr TcdPath
TcdArg:
        ld de,TermUp
        call TermEqual
        jr nz,TcdPathArg
        ld hl,TermCwd
        call TermBuildPath
        ld hl,TermPath
        call TermParent
        ld hl,TermParentPath
        jr TcdUpdate
TcdPathArg:
        ld hl,(TermArg)
TcdPath:
        call TermBuildPath
        jp c,TermError
        ld de,TermStat
        ld hl,TermPath
        ld a,18                 ; stat (does not change the process cwd)
        call zx_syscall
        jp c,TermError
        ld a,(TermStat+3)
        and $40                 ; directory flag
        jp z,TermError
        ld hl,TermPath
TcdUpdate:
        ld (TermArgSaved),hl
        ld b,17
TcdCheck:
        ld a,(hl)
        or a
        jr z,TcdCopyStart
        inc hl
        djnz TcdCheck
        ld hl,TextLong
        jp TermSay
TcdCopyStart:
        ld hl,(TermArgSaved)
        ld de,TermCwd
TcdCopy:
        ld a,(hl)
        ld (de),a
        or a
        ret z
        inc hl
        inc de
        jr TcdCopy

TermCat:
        call TermNeedPath
        ret c
        ld hl,TermPath
        ld de,0
        ld a,5
        call zx_syscall
        jp c,TermError
        ld (TermFD),hl
        ld hl,512
        ld (TermQuota),hl
TcatRead:
        ld hl,(TermFD)
        ld de,TermByte
        ld bc,1
        ld a,3
        call zx_syscall
        jr c,TcatEnd
        ld a,h
        or l
        jr z,TcatEnd
        ld a,(TermByte)
        call TermPutChar
        ld hl,(TermQuota)
        dec hl
        ld (TermQuota),hl
        ld a,h
        or l
        jr nz,TcatRead
        ld hl,TextLimit
        call TermSay
TcatEnd:
        ld hl,(TermFD)
        ld a,6
        call zx_syscall
        jp TermNewline
TermRm:
        call TermNeedPath
        ret c
        ld hl,TermPath
        ld de,TermStat
        ld a,18
        call zx_syscall
        jp c,TermError
        ld a,(TermStat+3)
        and $40                 ; rm never removes a directory
        jp nz,TermError
        ld hl,TermPath
        ld a,10
        call zx_syscall
        jp c,TermError
        ld hl,TextDone
        jp TermSay

; ZX-UX _mkdir creates the node; links for . and .. complete its
; directory structure just as the resident Unix mkdir utility does.
TermMkdir:
        call TermNeedPath
        ret c
        ld hl,TermPath
        ld de,$0e
        ld a,14
        call zx_syscall
        jp c,TermError
        ld hl,TermPath
        ld de,TermLink
        call TermCopyLink
        ld hl,TermPath
        ld de,TermLink
        ld a,9                  ; link dir -> dir/.
        call zx_syscall
	jr c,TermError
        ld hl,TermPath
        call TermParent
        ld hl,TermPath
        ld de,TermLink
        call TermCopyLink
        ld a,'.'
        ld (de),a
        inc de
        ld (de),a
        inc de
        xor a
        ld (de),a
        ld hl,TermParentPath
        ld de,TermLink
        ld a,9                  ; link parent -> dir/..
        call zx_syscall
	jr c,TermError
        ld hl,TextDone
        jp TermSay
TermCopyLink:
        ld b,39
TclLoop:
        ld a,(hl)
        or a
        jr z,TclEnd
        ld (de),a
        inc hl
        inc de
        djnz TclLoop
TclEnd:
        ld a,'/'
        ld (de),a
        inc de
        ld a,'.'
        ld (de),a
        inc de
        xor a
        ld (de),a
        ret
TermParent:
        ld de,TermParentPath
        ld hl,TermPath
        ld bc,40
        ldir
        ld hl,TermParentPath
        ld de,TermParentPath
TplFind:
        ld a,(hl)
        or a
        jr z,TplCut
        cp '/'
        jr nz,TplNext
        ld d,h
        ld e,l
TplNext:
        inc hl
        jr TplFind
TplCut:
        push de
        ld hl,TermParentPath
        or a
        sbc hl,de
        pop de
        jr nz,TplSub
        ld de,TermParentPath
        ld a,'/'
        ld (de),a
        inc de
        xor a
        ld (de),a
        ret
TplSub:
        xor a
        ld (de),a
        ret

TermError:
        cp 28                    ; the kernel reports ENOSPC in A
        jr z,TerNoSpace
        ld hl,TextError
        jp TermSay
TerNoSpace:
        ld hl,TextNoSpace
        jp TermSay

        section data
CmdHelp: db 'help',0
CmdPwd: db 'pwd',0
CmdLs: db 'ls',0
CmdCd: db 'cd',0
CmdCat: db 'cat',0
CmdEcho: db 'echo',0
CmdRm: db 'rm',0
CmdMkdir: db 'mkdir',0
CmdClear: db 'clear',0
TextPrompt: db '> ',0
TextCaret: db '_',0
TextGreeting: db 'ZX-UX COMMAND CONSOLE',0
TextHint: db 'TYPE HELP FOR COMMANDS',0
TextHelp1: db 'LS CD PWD CAT ECHO',0
TextHelp2: db 'RM MKDIR CLEAR HELP',0
TextUnknown: db '? COMMAND',0
TextError: db '? FILE OR DIRECTORY',0
TextNoSpace: db '? NO SPACE',0
TextArg: db '? NAME REQUIRED',0
TextLong: db '? PATH TOO LONG',0
TextDone: db 'OK',0
TextLimit: db '[OUTPUT TRUNCATED]',0
TermRoot: db '/',0
TermUp: db '..',0
; Live state exists once for the single console instance.
TermState:
TermRows: ds TERMROWS*TERMWIDTH
TermInput: ds TERMLINE
TermLen: db 0
TermCol: db 0
TermCwd: ds 17
TERMSTSZ equ $-TermState
; Scratch is used by the active window only, and is not saved.
TermY: db 0
TermChar: db 0
TermArg: dw 0
TermArgSaved: dw 0
TermFD: dw 0
TermQuota: dw 0
TermByte: db 0
TermPath: ds 42
TermLink: ds 45
TermParentPath: ds 42
TermEntry equ TermParentPath
TermName equ TermLink
TermStat equ TermLink