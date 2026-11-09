; =====================================================================
;  ZX-UX UNIX v1  -  kernel
;
;  Fresh Z80 implementation based on Erdogan Tan's 8086 UNIX v1 design
;  (u0..u9: sysent, sysret, fork/exec/wait/exit, namei, iget, readi,
;  writei, mget, alloc/free, itrunc, swap, clock, tty driver).
;  The 8086 / PDP-11 code was used as a specification only.
;
;  ZX Spectrum adaptation:
;    * file system on two RAM disks (/dev/rd0 = root 8K, /dev/rd1 = 4K)
;    * preemptive multitasking, 2 processes, driven by the ULA 50 Hz
;      frame interrupt (IM 2).  The process that is not running lives
;      in the swap image (v1 'swap' to drum -> exchange with SWAPB).
;    * ROM used for keyboard scan/decoding (KEYBOARD, KEY-INPUT),
;      BEEPER, 64-column screen in a 4x8 font (no ROM printing),
;      BREAK-KEY, character set and tape (SA-BYTES / LD-BYTES).
; =====================================================================

        DEVICE ZXSPECTRUM48

        include "const.inc"
        include "kvars.inc"

        org KBASE
        jp boot                 ; 6000 cold start.
        jp sysent               ; 6003 system call entry (A = number). Counting is cheaper than guessing.

; ---------------------------------------------------------------------
; Boot from the cold start. The machine has no snooze button.
; ---------------------------------------------------------------------
; The clock starts at 09:00 on 23 April 1982.
; Real shops may disagree; this is a default, not a time machine.
DEFTIME equ 4495*86400 + 9*3600

; --- initialize u-area of the process in core (fresh process 1)
; uinit: 25 bytes. A clean process starts with clean space.
uinit:
        ld hl,CORE
        ld de,CORE+1
        ld bc,UASZ-1
        ld (hl),0
        ldir
        ld hl,ROOTINO
        ld (u_cdir),hl
        ld a,1
        ld (u_intr),a
        ret

; --- (re)start /etc/init in the current slot (pid 1)
; kinit: 41 bytes. Start init. One process has to be first.
kinit:
        di
        ld sp,KSTACK
        call kmode
        ei
        ld hl,initarg
        ld de,KARGS
        ld bc,initarg_e-initarg
        ldir
        ld a,1
        ld (xargc),a
        ld hl,KARGS+initarg_e-initarg
        ld (xtop),hl
        ld hl,initarg
        call kexec              ; does not return on success.
        ld hl,msg_noinit
        jr panic

; ---------------------------------------------------------------------
; panic (u0 'panic') HL = message. A failed check is still a failed check.
; ---------------------------------------------------------------------
; panic: 24 bytes. Shout the error and stop the show.
panic:
        push hl
        xor a                   ; a screen owner must not hide the panic. A failed check is still a failed
                                ; check.
        ld (scrown),a
        ld hl,msg_panic
        call kputs
        pop hl
        call kputs
        ld a,10
        call kputc
        di
.h:     halt
        jr .h

; rom_error: 21 bytes. The ROM complained. We listen.
rom_error:                      ; RST 8 from a ROM routine.
        ld iy,05C3Ah
        ld a,(tapbusy)
        or a
        jr z,.p
        jp tapend               ; BREAK during tape i/o (NC: failed). The tape has exactly one direction:
                                ; onward.
.p:     ld sp,KSTACK
        ld hl,msg_romerr
        jr panic

; ---------------------------------------------------------------------
; ISR - ULA 50Hz frame interrupt (u4 'clock' + u0 'kb_int'). No refunds for missed ticks.
; ---------------------------------------------------------------------
; isr: 207 bytes. The frame clock gets its turn.
isr:
        push af
        push bc
        push de
        push hl
        push ix
        push iy
        ld iy,05C3Ah            ; ROM KEYBOARD / KEY-INPUT need it.
        exx
        ex af,af'
        push af
        push bc
        push de
        push hl
        call clk1               ; a frame of time.
; keyboard - ROM KEYBOARD scans, KEY-INPUT decodes (modes, caps).
        call ROM_KEYBOARD
        ld a,(SV_TVFLAG)
        and 0D7h                ; never let KEY-INPUT touch the editor.
        ld (SV_TVFLAG),a
        set 3,(iy+1)            ; L mode.
        call ROM_KEYINPUT
        call c,ttrawin
; BREAK (CAPS SHIFT + SPACE) = interrupt (v1 DEL).
        call ROM_BREAKKEY       ; NC = pressed.
        sbc a,a                 ; FF released / 00 pressed.
        inc a                   ; 00 released / 01 pressed.
        ld hl,brkst
        cp (hl)
        ld (hl),a
        jr z,.b2
        or a
        call nz,ttintr
.b2:
; status line, cursor (not while programs own the whole screen).
        ld a,(ttop)             ; owners 1-0Fh, ttop 0 or 21.
        ld hl,scrown
        cp (hl)
        jr c,.nost
        ld a,(stdirty)
        or a
        call nz,stdraw
        call cblnk
.nost:
; CPU accounting (ps / top).
        ld a,(idling)
        or a
        jr nz,.idl
        ld a,(cur)
        ld hl,p_cpu
        add a,a
        call addhla
        inc (hl)
        jr nz,.c9
        inc hl
        inc (hl)
        jr .c9
.idl:   ld hl,(idlet)
        inc hl
        ld (idlet),hl
.c9:
; a tape transfer in the last 5 s: the process using the tape keeps the CPU, so no other one can hold it (a
; BEEP runs with interrupts off) while the next block goes by. (dev.asm tapend). The cassette makes us wait
; for every bit.
        ld hl,tapq
        ld a,(hl)
        or a
        jr z,.q0
        dec (hl)
        inc hl                  ; (tapqp: whose transfer it was). The next block may take its sweet time.
        ld a,(cur)
        cp (hl)
        jr z,.q9
.q0:    ; scheduler: quantum.
        ld hl,quant
        ld a,(hl)
        or a
        jr z,.q1
        dec (hl)
        jr nz,.q9
.q1:    call othrun
        jr nz,.q9
        ld a,(inkern)
        or a
        jr z,.q2
        ld a,1
        ld (runrun),a
        jr .q9
.q2:    call swtch              ; preempt user process.
.q9:
; interrupt signal for a process running in user mode.
        ld a,(inkern)
        or a
        jr nz,.x
        ld a,(cur)
        ld hl,p_sig
        call addhla
        ld a,(hl)
        or a
        jr z,.x
        ld (hl),0
        cp 2
        jr z,.kill
        ld a,(u_intr)
        or a
        jr z,.x
.kill:  ; kill it: become kernel and exit. The jump does not stop for directions.
        call kmode
        jp sigck.xj0_11  
.x:
        pop hl
        pop de
        pop bc
        pop af
        ex af,af'
        exx
        pop iy
        pop ix
        pop hl
        pop de
        pop bc
        pop af
        ei
        reti

; clk1: one frame of time: sleeping processes (sys sleep), the frame counter (sys ticks), the clock.
; Interrupts off. IX is kept (tclk).
; clk1: 20 bytes. Count the frame tick. Time takes no days off.
clk1:   call ticksleep
        ld hl,(fticks)
        inc hl
        ld (fticks),hl
        ld hl,ticks
        inc (hl)
        ld a,(hl)
        cp 50
        ret c
        ld (hl),0
; (on into tick1s).

; --- one second elapsed
; tick1s: 48 bytes. Turn frame ticks into seconds. The clock does the math.
tick1s:
        ld hl,systime
        inc (hl)
        jr nz,.t1
        inc hl
        inc (hl)
        jr nz,.t1
        inc hl
        inc (hl)
        jr nz,.t1
        inc hl
        inc (hl)
.t1:    ld hl,tod_s
        inc (hl)
        ld a,(hl)
        cp 60
        jr c,.t9
        ld (hl),0
        dec hl                  ; tod_m.
        inc (hl)
        ld a,(hl)
        cp 60
        jr c,.t9
        ld (hl),0
        dec hl                  ; tod_h.
        inc (hl)
        ld a,(hl)
        cp 24
        jr c,.t9
        ld (hl),0
.t9:    jp settime.xj2_5  

; --- per-process sleep timers
; ticksleep: 37 bytes. Wake sleepers on time. Nobody gets a bonus nap.
ticksleep:
        ld b,0
.l:     ld a,b
        ld hl,p_tick
        add a,a
        call addhla
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld a,d
        or e
        jr z,.n
        dec de
        ld (hl),d
        dec hl
        ld (hl),e
        ld a,d
        or e
        jr nz,.n
        ld a,b
        ld c,WC_TIME
        call wakeslot
.n:     call nxslot
        jr c,.l
        ret

; ---------------------------------------------------------------------
; status line (bottom screen row): processes and time of day drawn straight into the display file with the
; ROM character set.
; ---------------------------------------------------------------------
; stdraw: 124 bytes. Paint status. The screen loves a little gossip.
stdraw:
        xor a
        ld (stdirty),a
        ld a,23
        call clrrow
        ld hl,03010h            ; red/yellow clock cells.
        ld (05AFCh),hl
        ld hl,02820h            ; green/cyan clock cells.
        ld (05AFEh),hl
        xor a
        ld d,a                  ; column.
        ld c,a                  ; slot: a 12 column cell each.
.p:     push bc
        ld a,c
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld e,(hl)
        ld a,(cur)              ; the running process in inverse.
        cp c
        ld b,0
        jr nz,.p0
        ld b,0F0h
.p0:    ld a,e
        or a
        jr z,.pn
        cp SZOMB                ; a process that has ended is not shown,.
        jr z,.pn                ; though its parent has not waited yet.
        ld a,c
        add a,'1'
        call stc
        ld a,e
        ld e,':'
        cp SRUN
        jr z,.p1
        ld e,'.'                ; SSLEEP.
.p1:    ld a,e
        call stc
        ld a,c
        call stname
        ld c,8
.n:     ld a,(hl)
        inc hl
        call stc
        dec c
        jr nz,.n
.pn:    pop bc
        ld a,c
        inc a
        ld c,a
        add a,a
        add a,c
        add a,a
        add a,a
        ld d,a                  ; 12 * slot.
        ld a,c
        cp NPROC
        jr c,.p
        ld d,56                 ; time hh:mm:ss at column 56.
        ld b,0
        ld a,(tod_h)
        call st2d
        ld a,':'
        call stc
        ld a,(tod_m)
        call st2d
        ld a,':'
        call stc
        ld a,(tod_s)
; st2d: A = 0-99 → two digits on the status line at column D.
; st2d: 15 bytes. Print two digits. Leading zero included.
st2d:   ld e,'0'-1
.d:     inc e
        sub 10
        jr nc,.d
        add a,'0'+10
        push af
        ld a,e
        call stc
        pop af
; stc: A = character, B = inverse → status line at column D, D + 1 (keeps BC, E, HL).
; stc: 13 bytes. Print one status character. Make it count.
stc:    push hl
        push de
        push bc
        ld e,23
        call glyph
        pop bc
        pop de
        pop hl
        inc d
        ret

; ---------------------------------------------------------------------
; scheduler (u3 'swap', 'tswap'; u4 'sleep', 'wakeup').
; ---------------------------------------------------------------------
; isrun: A = C = slot → Z if runnable.
; isrun: 26 bytes. Check who can run. Sleeping jobs get no votes.
isrun:
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld a,(hl)
        cp SRUN
        ret nz
        ld hl,(wlend)           ; while the window is lent, only SSX1.
        ld a,h                  ; programs run.
        or l
        ret z
        ld a,c
        ld hl,p_img
        call getw2
        ld a,h
        or l
        sub 1                   ; Z if it has an image.
        sbc a,a
        ret

; othrun: Z if a process other than the current one can run.
; othrun: 26 bytes. Find another runnable job. Four seats, small queue.
othrun:
        ld hl,p_stat
        ld a,(cur)
        ld c,a
        ld b,0
.l:     ld a,b
        cp c
        jr z,.n
        ld a,(hl)
        cp SRUN
        ret z
.n:     inc hl
        call nxslot
        jr c,.l
        or 1
        ret

; swtch: save the context of the running process, pick the next runnable one (round robin), swap images if
; needed, resume it. Interrupts disabled. (u3 'swap', 'tswap'). There is no scenic route through this code.
; swtch: 129 bytes. Switching jobs takes real work.
swtch:
        push af
        push bc
        push de
        push hl
        push ix
        exx
        ex af,af'
        push af
        push bc
        push de
        push hl
        ld a,(inkern)
        push af
        ld hl,0
        add hl,sp
        ex de,hl
        ld sp,KSTACK
        ld a,(cur)
        ld hl,p_sp
        call setw2
        call kmode
.pick:  ld a,(cur)
        ld b,NPROC
.rr:    inc a
        and NPROC-1
        ld c,a
        call isrun
        jr z,.got
        ld a,c
        djnz .rr
; nothing to run: pack idle files in the background, then wait until an interrupt makes a process runnable.
        ld a,1
        ld (idling),a
        ei
        call zidle
        jr nc,.busy
        halt
.busy:  di
        xor a
        ld (idling),a
        jr .pick
.got:   ld a,(cur)
        cp c
        jr z,.same
        push bc
        call swapout
        pop bc
        ld a,c
        ld (cur),a
        call swapin
        call setdirty
.same:
        ld a,QUANT
        ld (quant),a
        xor a
        ld (runrun),a
        ld a,(cur)
        ld hl,p_sp
        call getw2
        ld sp,hl
        pop af
        ld (inkern),a
        pop hl
        pop de
        pop bc
        pop af
        ex af,af'
        exx
        pop ix
        pop hl
        pop de
        pop bc
        pop af
        ret

; ---------------------------------------------------------------------
;  images  (UNIX v1 swap to drum uses arena copies here)
;  Every process has a SAVE block for its u-area.  A resident-text
;  process's SAVE also has room for its whole window image (u-area,
;  data up to the break, STKRES of stack), reserved as long as it lives,
;  so that a context switch never allocates.  The window is handed over
;  lazily: its image is saved only when another resident-text process
;  needs the window.  An SSX1 process runs in its IMAGE block, so a
;  switch to or from it moves just the u-area.
; ---------------------------------------------------------------------

; imgext: A = slot → sw_lo = break - UDATA, sw_hi = CORETOP - sp,.
; imgext: 34 bytes. Measure a program image. It has to fit.
imgext: push af
        ld hl,p_brk
        call getw2
        ld de,UDATA
        or a
        sbc hl,de
        ld (sw_lo),hl
        pop af
        ld hl,p_sp
        call getw2
        ex de,hl
        ld hl,CORETOP
        or a
        sbc hl,de
        ld (sw_hi),hl
        ret

; ldirz: LDIR that does nothing for BC = 0.
; ldirz: 6 bytes. Clear bytes quickly. Empty space is still space.
ldirz:  ld a,b
        or c
        ret z
        ldir
        ret

; savead: A = slot → HL = its SAVE block, DE = its window image part.
; savead: 14 bytes. Find the saved address. Moving hurts memory.
savead: ld hl,p_save
        call getw2
        push hl
        ld de,UASZ
        add hl,de
        ex de,hl
        pop hl
        ret

; wsave: A = slot (the window's owner): window image → its SAVE.
; wsave: 71 bytes. Save the process window. Every byte has baggage.
wsave:  push af
        call imgext
        pop af
        push af
        call savead
        call acap               ; BC = its SAVE's size.
        ld hl,-UASZ
        add hl,bc
        ld de,(sw_lo)
        or a
        sbc hl,de               ; HL = the room left for the stack. Even the stack has a closing time.
        ld de,(sw_hi)
        call cphlde
        jr nc,.ok
        ld (sw_hi),hl           ; too deep for its SAVE: keep the newest.
        pop af                  ; bytes that fit, it dies when it resumes.
        push af
        ld hl,p_sig
        call addhla
        ld (hl),2
.ok:    pop af
        push af
        call savead
        ld hl,UDATA
        ld bc,(sw_lo)
        call ldirz
        pop af
        push de
        ld hl,p_sp
        call getw2
        pop de
        jr wload.xj0_5  

; wload: A = slot: its SAVE → the window.
; wload: 36 bytes. Restore the process window. Put the chairs back.
wload:  push af
        call imgext
        pop af
        push af
        call savead
        ex de,hl
        ld de,UDATA
        ld bc,(sw_lo)
        call ldirz
        pop af
        push hl
        ld hl,p_sp
        call getw2
        ex de,hl
        pop hl
.xj0_5:
        ld bc,(sw_hi)
        jr ldirz

; swapout: A = slot leaving the processor → its u-area into its SAVE.
; swapout: 20 bytes. Move a job out. Next customer, please.
swapout:
        ld c,a
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld a,(hl)
        or a
        ret z
        cp SZOMB
        ret z
        ld a,c
        call savead
        ex de,hl
        ld hl,CORE
        jr swapin.xj0_4  

; swapin: A = slot taking the processor.
; swapin: 51 bytes. Move a job in. Same memory, new tenant.
swapin: ld c,a
        ld hl,p_img
        call getw2
        ld a,h
        or l
        jr nz,.ua               ; SSX1: just the u-area.
        ld a,(wown)             ; resident text: it needs the window.
        cp c
        jr z,.ua
        inc a
        jr z,.ld
        dec a
        push bc
        call wsave              ; the owner's image goes to its SAVE.
        pop bc
.ld:    ld a,c
        ld (wown),a
        push bc
        call wload
        pop bc
.ua:    ld a,c
        ld hl,p_save
        call getw2
        ld de,CORE
.xj0_4:
        ld bc,UASZ
        ldir
        ret

; relimg: A = slot: free its SSX1 image (interrupts off, or on the kernel stack: the image may be the stack
; in use). This is not an all-you-can-push buffet.
; relimg: 28 bytes. Relocate the image. Addresses need forwarding mail.
relimg: push af
        ld hl,p_img
        call getw2
        call afree
        ld hl,(wlend)           ; the window was lent: take it back.
        ld a,h
        or l
        call nz,unlend
        pop af
        ld de,0
        ld hl,p_img
        jp setw2

; sleep on channel A (interrupts must be disabled; returns disabled).
; ksleep: 28 bytes. Put a process to sleep. The scheduler stays awake.
ksleep:
        push hl
        ld e,a
        ld a,(cur)
        ld hl,p_wchan
        call addhla
        ld (hl),e
        ld a,(cur)
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld (hl),SSLEEP
        call setdirty
        call swtch
        pop hl
        ret

; wakeup all processes sleeping on channel A.
; kwakeup: 15 bytes. Wake waiting processes. Rise and shine.
kwakeup:
        ld c,a
        ld b,0
.l:     ld a,b
        push bc
        call wakeslot
        pop bc
        call nxslot
        jr c,.l
        ret
; wakeslot: A = slot, C = channel.
; wakeslot: 25 bytes. Wake one process slot. Your number is called.
wakeslot:
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld e,a
        ld a,(hl)
        cp SSLEEP
        ret nz
        push hl
        ld a,e
        ld hl,p_wchan
        call addhla
        ld a,(hl)
        pop hl
        cp c
        ret nz
        ld (hl),SRUN
        jp settime.xj0_36  

; preempt at system call return if the quantum ran out. The next instruction gets its turn.
; preempt: 13 bytes. End this turn. The clock has spoken.
preempt:
        di
        call othrun
        call z,swtch
        xor a
        ld (runrun),a
        ei
        ret

; signal check while in kernel (sysret, sleep loops) returns CF=1 if a signal was pending but is ignored.
; sigck: 31 bytes. Check pending signals. BREAK does not wait forever.
sigck:
        ld a,(cur)
        ld hl,p_sig
        call addhla
        ld a,(hl)
        or a
        ret z
        ld (hl),0
        cp 2                    ; kill: cannot be ignored.
        jr z,.die
        ld a,(u_intr)
        or a
        scf
        ret z
.xj0_11:
.die:   ei
        ld hl,0FFFFh
        jp doexit

; ---------------------------------------------------------------------
; system call interface (u1 'sysent', 'sysret', 'error') A = call number, arguments in HL, DE, BC; result
; in HL (DE) CF = 1 on error with A = error number. IX, IY preserved. The Z80 has delivered its complaint.
; ---------------------------------------------------------------------
; sysent: 34 bytes. Enter the kernel. Call number at the door.
sysent:
        push ix
        push iy
        ld iy,05C3Ah            ; ROM routines and RST 8 rely on it.
        push af
        call kmode
        pop af
        ld (u_sp),sp
        cp NSYS
        jr nc,badsys
        push hl
        ld hl,systab
        add a,a
        call addhla
        call ldind
        ex (sp),hl
        ret

; badsys: 2 bytes. Bad system call. The door is closed.
badsys: ld a,EINVAL
; syserr: 10 bytes. Return the error. Do not hide the bad news.
syserr:
        ld sp,(u_sp)
        ld hl,0FFFFh
        scf
        jr sysx
; sysok: 5 bytes. Return success. This time we earned it.
sysok:
        ld sp,(u_sp)
        xor a
; sysx: 29 bytes. Leave the kernel. Do not forget the flags.
sysx:
        push af
        push hl
        push de
        ld a,(runrun)
        or a
        call nz,preempt
        call sigck
        pop de
        pop hl
        pop af
        di
        push af
        xor a
        ld (inkern),a
        pop af
        pop iy
        pop ix
        ei
        ret

; systab: 82 bytes. System call table. Every number needs a destination.
systab:
        dw sysrele, sysexit, sysfork, sysread, syswrite, sysopen
        dw sysclose, syswait, syscreat, syslink, sysunlink, sysexec
        dw syschdir, systimec, sysmkdir, syschmod, sysok, sysbreak
        dw sysstat, sysseek, systell, badsys, badsys, sysok
        dw sysgetuid, sysstime, sysok, sysintr, sysfstat, sysok
        dw sysmdate, sysstty, sysgtty, sysok, syssleep, syskill
        dw sysgetpid, syszx, systicks, sysscreen, sysssxl

; ---------------------------------------------------------------------
; process system calls (u1/u2).
; ---------------------------------------------------------------------
; sysrele: 5 bytes. Release the CPU. Others want a turn.
sysrele:                        ; give up the processor.
        call preempt
        jr sysok


; sysgetpid: 4 bytes. Tell the process its own number. ID check.
sysgetpid:
        ld hl,sysok
        push hl
; mypid: 9 bytes. Find our process ID. Lost and found, tiny edition.
mypid:  ld a,(cur)
        ld hl,p_pid
        jp getw2

; sysfork: 213 bytes. A second process is not free.
sysfork:
; (no DI: other processes cannot run while we are in the kernel, and forkmem may pack files for a long
; time) a free slot, or the zombie of a child nobody waited for.
        ld b,0
.f:     ld a,b
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld a,(hl)
        or a
        jr z,.got
        call nxslot
        jr c,.f
        call mypid
        ex de,hl
        ld b,0
.z:     ld a,b
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld a,(hl)
        cp SZOMB
        jr nz,.zn
        ld a,b
        ld hl,p_ppid
        call getw2
        or a
        sbc hl,de
        jr z,.got
.zn:    call nxslot
        jr c,.z
.no:    ei
        ld a,EAGAIN             ; sh: "Try again".
        jp syserr
.got:   ld c,b
; memory for the child: a SAVE block (and a TWIN for an SSX1 image).
        push bc
        call forkmem
        pop bc
        jr c,.no
; A new process ID. The guest list grows one name.
        ld hl,(mpid)
.np:    inc hl
        ld a,h
        and 7Fh
        ld h,a
        or l
        jr z,.np
        ld (mpid),hl
        ld a,c
        ex de,hl
        ld hl,p_pid
        call setw2
        push de                 ; child pid.
        call mypid
        ex de,hl
        ld a,c
        ld hl,p_ppid
        call setw2
        call curbrk
        call getw2
        ex de,hl
        ld a,c
        ld hl,p_brk
        call setw2
        ld de,0
        ld a,c
        ld hl,p_tick
        call setw2
        ld a,c
        ld hl,p_cpu
        call setw2
        ld a,c
        ld hl,p_sig
        call addhla
        ld (hl),0
; copy name for the status line.
        ld a,(cur)
        call stname
        push hl
        ld a,c
        call stname
        ex de,hl
        pop hl
        push bc
        call ldir8
        pop bc
; shared open files: bump reference counts.
        call fpdup
; build the child's context frame on this stack. The return address would like to survive.
        ld hl,forkret
        push hl
        push af
        push bc
        push de
        push hl
        push ix
        exx
        ex af,af'
        push af
        push bc
        push de
        push hl
        exx
        ex af,af'
        ld a,1
        push af                 ; inkern = 1.
        ld hl,0
        add hl,sp
        ex de,hl
        ld a,c
        ld hl,p_sp
        call setw2
; the child's image: a copy of this one.
        push bc
        ld a,c
        call forkcpy
        pop bc
        ld hl,22                ; drop frame.
        add hl,sp
        ld sp,hl
        ld a,c
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld (hl),SRUN
        call setdirty
        ei
        jp syszx.xj0_8  
; forkret: 3 bytes. Come back from fork. Parent and child have receipts.
forkret:                        ; first run of the child.
        jp syskill.xj0_10  

; forkmem: C = child slot → its SAVE block for a copy of this resident-text image; CF if no room. (An SSX1
; program cannot fork: the 8K kernel has no room left for fork twins.).
; forkmem: 25 bytes. Count the RAM fork needs. Children are expensive.
forkmem:
        ld a,c
        ld (chslot),a
        call isssx              ; HL = this process's SAVE.
        scf
        ret nz
        call acap               ; the child's SAVE: the same size.
        ld a,K_SAVE
        call aalloc
        ret c
        ex de,hl
        ld a,(chslot)
        jp savefit.xj0_0  

; forkcpy: A = child slot (its context frame is on this stack). The stack is already carrying enough
; baggage.
; forkcpy: 24 bytes. Copy the process image. A proper family likeness.
forkcpy:
        ld (chslot),a
        ld hl,p_save            ; u-area.
        call getw2
        ex de,hl
        ld hl,CORE
        ld bc,UASZ
        ldir
        ld a,(chslot)
        jp wsave                ; the window image.

; release: the running process gives up its memory, window and screen.
; release: 46 bytes. Free the finished process. Return the chair.
release:
        call scrrel
        ld a,(cur)
        ld c,a
        ld a,(wown)
        cp c
        jr nz,.w
        ld a,0FFh
        ld (wown),a
.w:     ld a,c
        ld hl,p_save
        call getw2
        call afree
        ld de,0
        ld a,(cur)
        ld hl,p_save
        call setw2
        ld a,(cur)
        jp relimg

; HL → 8 byte status-line name for slot A.
; stname: 9 bytes. Set the process name. Eight letters of fame.
stname: add a,a
        add a,a
        add a,a
        ld hl,stline
        jp addhla

sysexit:
; doexit: 136 bytes. Leave without leaving the place in ruins.
doexit:                         ; HL = status.
        ld (u_tmp),hl
        ld hl,tapqp             ; Find the tape hold owner. Its clock privilege ends here.
        ld a,(cur)              ; Look at the exiting slot. No inherited tape holidays.
        xor (hl)                ; Compare the two slots. The hold belongs to its owner.
        jr nz,.nt
        dec hl                  ; tapq.
        ld (hl),a
.nt:
; close all files (v1: fclose loop).
        ld b,0
.cl:    push bc
        ld a,b
        call fclosea
        pop bc
        inc b
        ld a,b
        cp NUFILE
        jr c,.cl
; process 1 never dies: if init exits, start it again.
        call mypid
        dec hl
        ld a,h
        or l
        jr nz,.z
        ld de,UDATA
        call curbrk
        call setw2
        call uinit
        jp kinit
.z:     di
; orphans → process 1.
        call mypid
        ex de,hl
        ld b,0
.or:    push de
        ld a,b
        ld hl,p_ppid
        call getw2
        or a
        sbc hl,de
        jr nz,.on
        ld de,1
        ld a,b
        ld hl,p_ppid
        call setw2
.on:    pop de
        call nxslot
        jr c,.or
.o1:    ld de,(u_tmp)
        ld a,(cur)
        ld hl,p_xst
        call setw2
        ld sp,KSTACK            ; (interrupts are off) the image may go.
        call release
        ld de,UDATA
        call curbrk
        call setw2
        ld a,(cur)
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld (hl),SZOMB
        ld a,WC_WAIT
        call kwakeup
        call setdirty
        call swtch              ; never comes back.
        jr $

; syswait: 90 bytes. Wait for the process that actually finishes.
syswait:
.l:     di
        call mypid
        ex de,hl
        ld bc,0                 ; B = slot, C = live children.
.s:     ld a,b
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld a,(hl)
        or a
        jr z,.n
        push af
        ld a,b
        ld hl,p_ppid
        call getw2
        or a
        sbc hl,de
        jr nz,.nc
        pop af
        cp SZOMB
        jr z,.reap
        inc c
        jr .n
.nc:    pop af
.n:     call nxslot
        jr c,.s
        ld a,c
        or a
        jr z,.none
        ld a,WC_WAIT
        call ksleep
        ei
        call sigck
        jr .l
.reap:  ld a,b
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld (hl),SFREE
        call setdirty
        ld a,b
        ld hl,p_xst
        call getw2
        ex de,hl
        ld a,b
        ld hl,p_pid
        call getw2
        jr systimec.xj1_27  
.none:  ei
        ld a,ECHILD
        jp syserr

; syskill: 58 bytes. Send a process signal. BREAK is serious.
syskill:                        ; HL = pid.
        di
        ex de,hl
        ld b,0
.s:     ld a,b
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld a,(hl)
        cp SRUN
        jr c,.n
        cp SZOMB
        jr z,.n
        ld a,b
        ld hl,p_pid
        call getw2
        or a
        sbc hl,de
        jr z,.k
.n:     call nxslot
        jr c,.s
        ei
        ld a,ESRCH
        jp syserr
.k:     ld a,b
        ld hl,p_sig
        call addhla
        ld (hl),2               ; 2 = kill (cannot be ignored).
        ld a,b
        ld l,a                  ; p_stat is page aligned (KV).
        ld h,p_stat >> 8
        ld (hl),SRUN            ; wake it so it dies.
.xj0_10:
        ei
        jr sysgetuid.xj1_15  
ESRCH   equ 3

; syssleep: 38 bytes. Sleep for ticks. The clock will be back.
syssleep:                       ; HL = ticks (1/50 s).
        ex de,hl
        di
        ld a,(cur)
        ld hl,p_tick
        call setw2
.l:     ld a,(cur)
        ld hl,p_tick
        call getw2
        ld a,h
        or l
        jr z,.d
        ld a,WC_TIME
        call ksleep
        ei
        call sigck
        di
        jr .l
.d:     jr systimec.xj0_60  

; sysintr: 7 bytes. Set the interrupt rule. BREAK gets terms.
sysintr:
        ld a,l
        ld (u_intr),a
        jp sysok
; sys quit: accepted and ignored (there is no quit key; v1's flag was only ever written).

; sysgetuid: 6 bytes. Return the user number. There is only one seat.
sysgetuid:                      ; single user: everybody is root.
.xj1_15:
        ld hl,0
        jp sysok

; systimec: 12 bytes. Read the clock. The seconds have receipts.
systimec:
        di
        ld hl,(systime)
        ld de,(systime+2)
.xj0_60:
.xj1_27:
        ei
        jp sysok

; sysstime: 6 bytes. Set the clock. Time can be negotiable here.
sysstime:
        call settime
        jp sysok

; settime: DE:HL = seconds since 1970 → systime, time of day.
; settime: 39 bytes. Update seconds and date. The calendar complains.
settime:
        di
        ld (systime),hl
        ld (systime+2),de
        ei
        ld bc,60
        call div32
        ld (tod_s),a
        ld bc,60
        call div32
        ld (tod_m),a
        ld bc,24
        call div32
        ld (tod_h),a
.xj0_36:
.xj2_5:
        jp setdirty.xj1_0  

; sysbreak: 87 bytes. Move the program break. RAM has a hard ceiling.
sysbreak:                       ; HL = new break.
        ex de,hl
        ld hl,-128
        add hl,sp
        call cphlde
        jr c,.bad               ; not into the stack.
        ld a,(cur)
        ld hl,p_img
        call getw2
        ld a,h
        or l
        jr z,.win
        ex de,hl                ; SSX1: anywhere in the IMAGE below the.
        call cphlde             ; stack.
        jr c,.bad
        ex de,hl
        jr .set
.win:   ld hl,UDATA
        ex de,hl
        call cphlde
        jr c,.bad
; a window image that big must fit its SAVE block.
        push hl                 ; SAVE size needed: as now + (new - old.
        ex de,hl                ; break), so the stack reserve is kept.
        call curbrk
        call getw2
        ex de,hl
        or a
        sbc hl,de
        push hl
        call cursave
        call acap
        pop hl
        add hl,bc
        ld b,h
        ld c,l
        call savefit
        jr c,.bad1
        pop de
.set:   call curbrk
        di
        call setw2
        ei
        jp sysseek.xj0_57  
.bad1:  pop hl
.bad:   ld a,ENOMEM
        jp syserr

; ---------------------------------------------------------------------
; exec (u2 'sysexec').
; ---------------------------------------------------------------------
; sysexec: 20 bytes. Start a new program. The old one packs its bags.
sysexec:                        ; HL = path, DE = argv (0-terminated).
        ld (u_tmp),hl
        call kargv
        ld a,EINVAL
        jp c,syserr
        ld hl,(u_tmp)
        call kexec
        jp syserr

; kargv: DE = argv (0-terminated; 0: argv[0] = the path at HL) → the strings in KARGS, xargc, xtop. CF if
; too many or too long.
; kargv: 67 bytes. Copy arguments for exec. Everyone comes along.
kargv:  ld bc,KARGS
        xor a
        ld (xargc),a
        ld a,d
        or e
        jr nz,.a0
        ex de,hl                ; no argv: argv[0] = path.
        call .str
        ret c
        jr .a9
.a0:    ld a,(de)
        ld l,a
        inc de
        ld a,(de)
        ld h,a
        inc de
        or l
        jr z,.a9
        push de
        ex de,hl
        call .str
        pop de
        ret c
        jr .a0
.a9:    ld (xtop),bc            ; NC.
        ret
; copy string DE → (BC), count it; CF if too many / too long. The numbers are not open to negotiation.
.str:   ld a,(xargc)
        cp 24
        ccf
        ret c
        inc a
        ld (xargc),a
.s1:    ld hl,KARGS+KARGSZ-1    ; room checked before the store: the.
        or a                    ; byte after KARGS is the kernel's.
        sbc hl,bc
        ret c
        ld a,(de)
        ld (bc),a
        inc de
        inc bc
        or a
        jr nz,.s1
        ret

; kexec: HL = path; KARGS/xargc/xtop hold the arguments. returns (CF, A=errno) only on failure, otherwise
; starts the program. No victory lap on the error path.
; kexec: 202 bytes. Make space before starting a fresh act.
kexec:
        ld (u_tmp),hl           ; the path (status line name).
        call tapnam             ; /dev/cassette/NAME: the loader runs it.
        jr nz,.nt
        ld hl,ks_ldx
.nt:    call namei
        ld a,ENOENT
        ret c
        call iget
        ret c
        ld a,(ix+1)
        and 040h                ; directory?
        ld a,EACCES
        scf
        ret nz
        bit 3,(ix+1)            ; programs are resident text (or from.
        jr z,.nox               ; the cassette, through /etc/ldx).
        ld a,(ix+0)
        and IEXEC
        jr z,.nox
        call idskp              ; its 8-byte a.out style header: jr.+8, stack reserve, bss size, entry. The
                                ; stack has no room for souvenirs.
        ld de,xhdr
        ld bc,8
        ldir
        jr .hok
.nox:   ld a,ENOEXEC
        scf
        ret
.hok:   ; the new break: data and bss start at UDATA.
        ld hl,UDATA
        ld de,(xhdr+4)
        add hl,de
        jr c,.big
        ld de,CORETOP-STKRES
        call cphlde
        jr nc,.big
; the window: not while it is lent to another program.
        push hl
        ld a,(cur)
        ld hl,p_img
        call getw2
        ld de,(wlend)
        ld a,d
        or e
        jr z,.wok
        sbc hl,de
        jr z,.wok
        pop hl
        jr .big
.wok:   pop hl
; a SAVE block: u-area, data and bss, the program's stack reserve. Pop carefully; the stack keeps receipts.
        ld de,UDATA-UASZ
        or a
        sbc hl,de
        ld de,(xhdr+2)
        add hl,de
        ld b,h
        ld c,l
        call savefit
        ret c
        ; ---- point of no return: the old image is discarded
        di
        ld sp,KSTACK
        call kmode
        jr .ks
.big:   jp aalloc.xj1_0  
.ks:    call isssx              ; an SSX1 caller leaves its image.
        ld a,(cur)
        call nz,relimg
        ld a,(cur)              ; and the window becomes ours.
        ld c,a
        ld a,(wown)
        cp c
        jr z,.own
        inc a
        jr z,.tk
        dec a
        call wsave
.tk:    ld a,(cur)
        ld (wown),a
.own:   ei
        call exname
        ld hl,UDATA             ; zero bss and set the break.
        ld bc,(xhdr+4)
        push hl
        add hl,bc
        ex (sp),hl
        call zero
        pop de
        call curbrk
        di
        call setw2
        ei
        ld hl,CORETOP
        call mkargs
        ld hl,(xhdr+6)
        jr go

; zero: HL = address, BC = count (may be 0).
; zero: 15 bytes. Clear the bytes. No leftovers.
zero:   ld a,b
        or c
        ret z
        ld (hl),0
        dec bc
        ld a,b
        or c
        ret z
        ld d,h
        ld e,l
        inc de
        ldir
        ret

; mkargs: HL = top → u_tmp = stack pointer with the arguments below top (v1 layout): sp → argc, argv[0]..
; argv[n-1], 0, strings. The stack has no room for souvenirs.
; mkargs: 81 bytes. Make the argument list. One pointer per guest.
mkargs: push hl
        ld hl,(xtop)
        ld de,KARGS
        or a
        sbc hl,de               ; string bytes.
        ld b,h
        ld c,l
        pop hl
        or a
        sbc hl,bc
        ld (u_tmp2),hl          ; first string.
        ex de,hl
        ld hl,KARGS
        call ldirz
        ld a,(xargc)
        ld l,a
        ld h,0
        inc hl
        add hl,hl               ; (argc+1)*2.
        ex de,hl
        ld hl,(u_tmp2)
        or a
        sbc hl,de
        dec hl
        dec hl                  ; argc word.
        ld (u_tmp),hl           ; new sp.
        ld a,(xargc)
        ld (hl),a
        inc hl
        ld (hl),0
        inc hl
        ld de,(u_tmp2)          ; first string.
        ld a,(xargc)
        ld b,a
        or a
        jr z,.c4
.c2:    ld (hl),e
        inc hl
        ld (hl),d
        inc hl
.c3:    ld a,(de)
        inc de
        or a
        jr nz,.c3
        djnz .c2
.c4:    ld (hl),0
        jp acompact.xj0_6  

; go: user mode at entry HL with the stack at (u_tmp). Every push gets a bill on the way out.
; go: 11 bytes. Start the user code. The kernel steps aside.
go:     di
        ld sp,(u_tmp)
        xor a
        ld (inkern),a
        ei
        jp (hl)

; savefit: BC = bytes → the running process's SAVE block holds that many (resized: its contents matter only
; while it is not running). CF, A = ENOMEM if there is no room (the old block is kept). The error path has
; earned its keep.
; savefit: 65 bytes. Check saved-image size. No squeezing past the limit.
savefit:
        ld d,b
        ld e,c                  ; DE = bytes needed.
        call cursave
        ld bc,0
        ld a,h
        or l
        call nz,acap            ; BC = what it holds (none: at boot).
        ex de,hl
        call cpbchl
        jr c,.grow
        ld b,h                  ; big enough: keep just what is needed. Bad news travels faster than tape.
        ld c,l
        ex de,hl
        call ashrink
        or a
        ret
.grow:  push bc
        ld b,h
        ld c,l
        ex de,hl
        call afree              ; the old block goes first.
        ld a,K_SAVE
        call aalloc
        pop bc
        jr nc,.set
        ld a,K_SAVE             ; no room: the old size again (it was.
        call aalloc             ; just freed: it fits).
        call .set
        jp aalloc.xj0_7  
.set:   ex de,hl
        ld a,(cur)
.xj0_0:
        ld hl,p_save
        call setw2
        or a
        ret

; isssx: NZ if the running process is an SSX1 program; HL = its SAVE.
; isssx: 11 bytes. Check the SSX1 header. Magic bytes are not magic.
isssx:  ld a,(cur)
        ld hl,p_img
        call getw2
        ld a,h
        or l
; cursave: 12 bytes. Save the running state. No memory lapses.
cursave:
        push af
        ld a,(cur)
        ld hl,p_save
        call getw2
        pop af
        ret

; exname: (point of no return) interrupts caught → default; the status line name from the path in u_tmp.
; exname: 51 bytes. Find the executable name. No mystery guests.
exname: ld a,(u_intr)
        or a
        jr z,.i0
        ld a,1
        ld (u_intr),a
.i0:    call scrrel             ; a screen it owned goes back.
        ld hl,(u_tmp)
.nm:    call basename           ; HL = a path: sys ssxload names the program.
        ld a,(cur)
        push hl
        call stname
        ex de,hl
        pop hl
        ld b,8
.n1:    ld a,(hl)
        or a
        jr z,.n2
        ld (de),a
        inc hl
        inc de
        djnz .n1
        jr .n3
.n2:    ld a,' '
        ld (de),a
        inc de
        djnz .n2
.n3:    jp setdirty

; tapnam: HL = path → Z, HL = the name if it is /dev/cassette/NAME or /dev/tap/NAME.
; tapnam: 35 bytes. Find the cassette name. The reel has labels.
tapnam: ld de,ks_cas
        call .pre
        ret z
        ld de,ks_tap
.pre:   push hl
.l:     ld a,(de)
        or a
        jr z,.e
        cp (hl)
        jr nz,.no
        inc hl
        inc de
        jr .l
.e:     ld a,(hl)
        cp '/'
        jr nz,.no
        inc hl
        pop af
        xor a
        ret
.no:    pop hl
        or 1
        ret


; ---------------------------------------------------------------------
;  sys ssxload (40): run an SSX1 program from the cassette.  /etc/ldx
;  runs in place of /dev/cassette/NAME (kexec); it finds NAME's header
;  on the tape (a CODE header whose second parameter is 'SS', the first
;  the memory the program needs) and makes this call with BC = the
;  length of the SSX1 file (the data block that follows), DE = the
;  bytes of memory for the program and its arguments and HL = the
;  arguments (argv, 0-terminated, as for exec).  The caller's image is given up at once (as an exec), so
;  a program that cannot be loaded ends the process with status 1.  If
;  the arena cannot hold it, the window is lent to it: resident-text
;  processes wait until it ends.  (SPEC-ELASTIC-R2 section 6.)
; ---------------------------------------------------------------------
KC_ENT  equ xhdr                ; Entry address. The loaded program must know where to start.
KC_TOT  equ xhdr+2              ; Total image and argument bytes. RAM keeps exact accounts.
KC_IMG  equ xhdr+4              ; The allocated image block. Real storage, no promises.
KC_F    equ xhdr+6              ; Tape-file location at the block top. Mind the edge.
; sysssxl: 325 bytes. A loaded program still has to fit.
sysssxl:
        push hl                 ; argv (isssx returns HL = the SAVE).
        call isssx              ; only a resident caller (/etc/ldx).
        ld a,EINVAL
        jp nz,syserr
        ld h,d                  ; the file must fit the memory asked for.
        ld l,e
        sbc hl,bc               ; CF clear: isssx ends with OR.
        pop hl
        jp c,syserr
        ld (KC_TOT),de
        ld (KC_ENT),bc
        ex de,hl                ; the caller's argv, again: KARGS may hold.
        call kargv              ; another process's exec arguments by now.
        ld a,EINVAL
        jp c,syserr
        ; ---- point of no return: the caller's image goes
        di
        ld sp,KSTACK
        call kmode
        ei
        ld hl,KARGS             ; Use argv[0] for the screen name. Names matter to ps.
        call exname.nm          ; Loader wildcard names become real program names here.
        ld a,0FFh               ; Free the old owner mark. The window changes hands.
        ld (wown),a
        call cursave            ; the SAVE keeps just the u-area.
        ld bc,UASZ
        call ashrink
        ld hl,(wlend)           ; Check whether the window is already lent. Only one renter.
        ld a,h                  ; Read the high byte of the lender marker. No double loans.
        or l                    ; Check the other byte. Even a zero has a meaning.
        jr nz,.mem
        call acompact           ; all free space in one block: the image.
        ld bc,(KC_TOT)          ; goes just above the movable ones.
        push bc
        ld a,K_IMG
        call aalloc
        pop bc
        jr nc,.img
        ld a,(u_intr)           ; no room: lend it the window - not to a.
        or a                    ; program BREAK cannot stop (background).
        jr z,.mem
        push bc
        call lend
        pop bc
        ld a,K_IMG
        call aalloc
        jr c,.mem
        ld (wlend),hl
        jr .img
.mem:   ld hl,KARGS             ; Print the failed program name. RAM said no.
        call kputs              ; Keep the complaint visible. Disappearing silently is rude.
        ld hl,ks_nomem          ; Explain the shortfall. There is no secret spare window.
        call kputs              ; Print the message; there is no safe place to put it.
.bad:   ld hl,1                 ; Exit with status one. Failed loads are not a win.
        jp doexit
.img:   ld (KC_IMG),hl
        ex de,hl
        ld a,(cur)
        ld hl,p_img
        call setw2
; the file into the top of the block.
        ld hl,(KC_IMG)
        ld de,(KC_TOT)
        add hl,de
        ld de,(KC_ENT)          ; the file's length.
        or a
        sbc hl,de
        ld (KC_F),hl
        ld (u_base),hl
        ld (u_count),de
        call taprd
        jr c,.bad
        ld hl,(KC_F)            ; its header (before the image moves.
        ld bc,6                 ; over it).
        add hl,bc
        ld e,(hl)
        inc hl
        ld d,(hl)               ; image size.
        inc hl
        ld (u_tmp2),de
        ld c,(hl)
        inc hl
        ld b,(hl)               ; bss.
        inc hl
        inc hl
        inc hl                  ; stack.
        ld e,(hl)
        inc hl
        ld d,(hl)               ; heap.
        inc hl
        ex de,hl
        add hl,bc
        ex de,hl
        push de                 ; bss + heap.
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (KC_ENT),de          ; entry.
        ld c,(hl)
        inc hl
        ld b,(hl)
        push bc                 ; relocations.
        inc hl                  ; checksum.
        inc hl
        inc hl                  ; the image to the bottom of the block.
        ld de,(KC_IMG)
        ld bc,(u_tmp2)
        call ldirz              ; Copy the body and keep the relocation start. No guessing.
        xor a                   ; Zero A and the carry flag. Other jobs may run again.
        ld (tapq),a             ; End the tape hold now. Job done; privilege gone.
        pop bc
        push de
        ld de,0
.r:     ld a,b
        or c
        jr z,.rd
        ld a,(hl)
        inc hl
        or a
        jr nz,.d
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        jr .p
.d:     add a,e
        ld e,a
        jr nc,.p
        inc d
.p:     push hl
        push de
        ld hl,(u_tmp2)          ; the patched word must lie in the image.
        dec hl
        call cphlde             ; (size-1) - offset.
        jp c,.bad
        jp z,.bad
        ld hl,(KC_IMG)
        add hl,de
        ld de,(KC_IMG)
        ld a,(hl)
        add a,e
        ld (hl),a
        inc hl
        ld a,(hl)
        adc a,d
        ld (hl),a
        pop de
        pop hl
        dec bc
        jr .r
.rd:    pop hl                  ; bss and heap: zero, the break after them.
        pop bc
        push hl
        add hl,bc
        ex de,hl
        call curbrk
        call setw2
        pop hl
        call zero
        ld hl,(KC_IMG)          ; the arguments at the top.
        ld de,(KC_TOT)
        add hl,de
        call mkargs
        ld hl,(KC_IMG)
        ld de,(KC_ENT)
        add hl,de
        jp go

; HL = path → HL = last component.
; basename: 17 bytes. Drop the path. Keep the last name.
basename:
        ld d,h
        ld e,l
.l:     ld a,(hl)
        inc hl
        or a
        jr z,.e
        cp '/'
        jr nz,.l
        ld d,h
        ld e,l
        jr .l
.e:     ex de,hl
        ret

; ---------------------------------------------------------------------
; Small helpers, small bills. RAM sends the invoice.
; ---------------------------------------------------------------------
; addhla: 5 bytes. Add A to HL. Tiny math, real consequences.
addhla: add a,l
        ld l,a
        ret nc
        inc h
        ret
; HL = word array base, A = slot → HL = value.
; getw2: 4 bytes. Read a word. Two bytes, please.
getw2:  add a,a
        call addhla
; ldind: HL → HL = the word at HL.
; ldind: 5 bytes. Load an indirect word. The pointer knows the way.
ldind:  ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ret
; nxslot: next process slot in B → CF while B < NPROC. The shared door saves a few steps.
; nxslot: 5 bytes. Choose the next slot. The queue is short.
nxslot: inc b
        ld a,b
        cp NPROC
        ret
; kmode: executing kernel code from here on.
; kmode: 6 bytes. Enter kernel mode. No visitors allowed.
kmode:  ld a,1
        ld (inkern),a
        ret
; ldir8: copy 8 bytes HL → DE.
; ldir8: 6 bytes. Copy eight bytes. Exactly eight, no extras.
ldir8:  ld bc,8
        ldir
        ret
; setdirty: the status line needs redrawing.
; setdirty: 5 bytes. Mark the status line dirty. It needs repainting.
setdirty:
.xj1_0:
        ld a,1
        jp kcls.xj0_0  
; curbrk: A = running slot, HL = p_brk (for getw2 / setw2).
; curbrk: 7 bytes. Get the current program break. Know the boundary.
curbrk: ld a,(cur)
        ld hl,p_brk
        ret
; idskp: IX = i-node → HL = its block (i.dskp).
; idskp: 7 bytes. Read a file data pointer. Addresses count.
idskp:  ld l,(ix+I_DSKP)
        ld h,(ix+I_DSKP+1)
        ret
; isize: IX = i-node → HL = its size.
; isize: 7 bytes. Read file size. The number should be real.
isize:  ld l,(ix+I_SIZE)
        ld h,(ix+I_SIZE+1)
        ret
; HL = word array base, A = slot, DE = value.
; setw2: 8 bytes. Write a two-byte value. No spare third byte.
setw2:  add a,a
        call addhla
        ld (hl),e
        inc hl
        ld (hl),d
        ret
; unsigned compare HL-DE (flags as sub). No free pass for a dodgy value.
; cphlde: 6 bytes. Compare two words. Zero gets the tie.
cphlde: push hl
        or a
        sbc hl,de
        pop hl
        ret
; minhlde: 6 bytes. Choose the smaller word. The little guy wins.
minhlde:
        call cphlde
        ret c
        ex de,hl
        ret

; div32: DE:HL = DE:HL / BC, A = remainder (BC < 256).
div32:
        push bc
        xor a
        ld b,32
.l:     add hl,hl
        rl e
        rl d
        rla
        jr c,.s
        cp c
        jr c,.n
.s:     sub c
        inc l
.n:     djnz .l
        pop bc
        ret

        include "fs.asm"
        include "dev.asm"
        include "zx.asm"
        include "arena.asm"
        include "cext.asm"

kend:
        ASSERT kend - KBASE <= 8192     ; the 8K kernel.

; console font: 96 glyphs of 4 x 8 pixels, two rows a byte (384 bytes,
; 4-aligned).  "SANYALnet-Labs-4x8-font-FINAL" from the ZX-UX c48 SDK.
; Based on original work by Supratim Sanyal of SANYALnet Labs.
; SANYALnet Labs Non-Commercial License: see ../LICENSE.
        ALIGN 4
FONT:   incbin "font4x8.bin", 8, 384
FONTEND:
; =====================================================================
; user land (resident pure text).
; =====================================================================
        include "ulib.asm"
        include "t_sys.asm"
        include "t_file.asm"
        include "t_misc.asm"
        include "t_tap.asm"
        include "t_proc.asm"
        include "t_vi.asm"
        include "t_zx.asm"
        include "t_tar.asm"
        include "t_ldx.asm"
; the resident programs: text address, size, extra mode bits (build.py).
PTAB:   include "ptab.inc"

utext_end:

; ---------------------------------------------------------------------
; ZXW: 256 bytes for the zxpack literal model - and, as loaded from the tape, the boot code, run once (it
; is outside the 8K kernel).
; ---------------------------------------------------------------------
ZXW     equ (utext_end + 1) & 0FFFEh
        org ZXW
; boot: 164 bytes. Wake up the system without waking the bugs.
boot:
        di
        ld sp,KSTACK
        ld iy,05C3Ah
; clear kernel globals (printer buffer: 256 bytes).
        xor a
        ld hl,KV
        ld b,a
        call zfill
        ld hl,MEMBOT            ; kernel scratch in MEMBOT: BASIC's.
        ld b,15                 ; calculator left values there.
        call zfill
; IM 2: vector FFFFh from the ROM, JR at FFFF → JP isr at FFF4.
        ld a,0C3h
        ld (TRAMP),a
        ld hl,isr
        ld (TRAMP+1),hl
        ld a,018h
        ld (0FFFFh),a
        ld a,IM2I
        ld i,a
        im 2
; catch ROM errors (RST 8) instead of returning to BASIC. No victory lap on the error path.
        ld hl,rom_error
        ld (kerrsp),hl
        ld hl,kerrsp
        ld (SV_ERRSP),hl
; screen (the loader set the border and colours).
        call kcls
; keyboard: L mode (lower case), repeat rates.
        set 3,(iy+1)            ; FLAGS: L mode.
        xor a
        ld (SV_MODE),a
        ld a,TT_ECHO
        ld (ttymode),a
; clock: default date.
        ld hl,DEFTIME & 0FFFFh
        ld de,DEFTIME >> 16
        call settime
        ld a,QUANT
        ld (quant),a
        call kmode
        ld (stdirty),a
        ld (kcon),a             ; kernel messages on.
; The boot banner. Even a tiny Unix likes an entrance.
        ld hl,msg_boot
        call kputs
; check the root file system (the loader put the i-node table and the arena in place).
        ld a,(ITAB+1)
        cp 0C0h                 ; allocated directory.
        ld hl,msg_nofs
        jp nz,panic
        xor a
        ld (zbusy),a
        ld (zidlem),a
        dec a
        ld (wown),a             ; the window is empty.
        ld hl,WINDOW
        ld (a_top),hl           ; the arena ends below it.
        ld hl,msg_ok
        call kputs
; process 1 (slot 0: cur is 0, the globals were cleared).
        ld a,SRUN
        ld (p_stat),a
        ld hl,1
        ld (p_pid),hl
        ld (mpid),hl
        ld hl,UDATA
        ld (p_brk),hl
        call uinit
        ei
        jp kinit                ; exec /etc/init.
; Startup messages: printed once, so they live in the boot area too.
; msg_boot: 104 bytes. Welcome text. Even a tiny OS can say hello.
msg_boot:
        db 10,"ZX-UX UNIX v1 48K ZX Spectrum Z80 3.5Mhz",10
        db 127," 2026 SANYALnet Labs",10
        db "ZX-UX v1 kernel "
        include "../out/bootinfo.inc"
msg_ok: db "ok",10,0
msg_nofs: db "no root fs",0

bootend:

; the i-node table and the arena follow, up to the window. The boot area is ZXWSZ bytes, or longer if the
; boot code and messages need it (true is -1 in sjasmplus expressions).
ZXEXTRA equ -((bootend - ZXW > ZXWSZ) * (bootend - ZXW - ZXWSZ))
ITAB    equ ZXW + ZXWSZ + ZXEXTRA
AR0     equ ITAB + NINODE*INOSZ

        SAVEBIN "unix.bin", KBASE, bootend-KBASE
        ASSERT WINDOW - AR0 >= 12000

; =====================================================================
;  low kernel: code and data that the BASIC loader puts in low memory,
;  at the bottom of the kernel stack's area (block "lowk" on the system
;  tape, loaded before "unix").  Bytes here cost the arena nothing.  The
;  loader's own BASIC, variables and work space end below 5D50 while it
;  loads (STKEND); the kernel stack keeps at least LOWSTK bytes above
;  (its deepest use: 82 bytes measured over the test suite, under 150
;  by inspection).
; =====================================================================
LOWSTK  equ 180
        org LOWK
; lowk: 177 bytes. Low-memory kernel text. RAM has clever tenants.
lowk:
; strings and tables the kernel reads (kexec, panic, the keyboard). A bad result still deserves a clean
; exit.
ks_cas: db "/dev/cassette",0
ks_tap: db "/dev/tap",0
ks_ldx: db "/etc/ldx",0
ks_nomem: db ": not enough memory",10,0
; the tape's hold on the CPU (dev.asm tapend, the ISR): loaded as 0.
tapq:   db 0                    ; Frames remaining for the tape owner. Five seconds, tops.
tapqp:  db 0                    ; Owner of that short hold. No sharing the queue.
msg_noinit: db "no "            ; Panic text starts here. The argument fills the gap.
initarg: db "/etc/init",0
initarg_e:
msg_panic: db 10,"panic: ",0
msg_romerr: db "ROM error",0
; Spectrum keyword tokens produced by SYMBOL SHIFT in L mode are mapped to the ASCII characters printed in
; red on the same key (E mode), so ~ | \ { } [ ] can be typed without extended mode.
toktab: db 0E2h,'~'             ; STOP (SS+A).
        db 0C3h,'|'             ; NOT (SS+S).
        db 0CDh,5Ch             ; STEP (SS+D) backslash.
        db 0CCh,'{'             ; TO (SS+F).
        db 0CBh,'}'             ; THEN (SS+G).
        db 0C6h,'['             ; AND (SS+Y).
        db 0C5h,']'             ; OR (SS+U).
        db 0ACh,'@'             ; AT (SS+I) (SS+2 is @ too).
        db 0C7h,'<'             ; <=.
        db 0C8h,'>'             ; >=.
        db 0C9h,'!'             ; <>.
        db 0

; tclk: a block the ROM moved with interrupts off: the time it took, on
;   the clock (and the frame counter, the sleeping processes' timers) -
;   the pilot tone (5 s before a header, 2 s before data) and every bit:
;   a 0 is two 855 T-state pulses, a 1 two of 1710, so 1 or 2 units of
;   1710 T; 41 units make a 69888 T frame.  The time spent waiting for
;   the tape to start is not known.  It runs with interrupts on, so the
;   ISR counts the time it takes itself (each frame it adds is put on
;   with them off); returns CF.
; tclk: 67 bytes. The clock ticks whether we like it or not.
tclk:   ei                      ; its own time is counted by the ISR.
        ld ix,100               ; frames: the pilot tone.
        ld bc,(u_count)
        ld a,c
        sub 17                  ; a header is 17 bytes.
        or b
        jr nz,.d
        ld ix,250
.d:     ld hl,(u_base)          ; ... and the bits.
        ld e,0                  ; units into the frame.
.b:     ld a,b
        or c
        jr z,.t
        dec bc
        ld a,(hl)
        inc hl
        scf
        adc a,a                 ; bit 7 into CF, a marker into bit 0.
.i:     ld d,a
        ld a,e
        adc a,1                 ; one unit, two for a 1.
        cp 41
        jr c,.k
        sub 41
        inc ix
.k:     ld e,a
        ld a,d
        add a,a                 ; the next bit; the marker leaves A = 0. The jump does not stop for
                                ; directions.
        jr nz,.i
        jr .b
.t:     di
        call clk1               ; it leaves IX alone.
        ei
        dec ix
        ld a,ixh
        or ixl
        jr nz,.t
        scf
        ret

lowkend:
        ASSERT lowkend <= KSTACK - LOWSTK
        SAVEBIN "lowk.bin", LOWK, lowkend - LOWK
