; Copy a block of memory.
;
; The program runs on CP/M but you need a debugger like DDT or SID to inspect the
; process and the machine state. From SID start the program with this command,
; which runs it until the breakpoint at address 'done':
;
; g,.done


            org     100h


len         equ     10                  ; Block length


            lxi     h, source           ; Source block
            lxi     d, dest             ; Destination
            mvi     c, len              ; Length counter

loop:       xra     a                   ; Clear a
            cmp     c                   ; c == 0?
            jz      done                ; Yes
            mov     a, m                ; Load from source
            stax    d                   ; Copy to destination
            inx     h                   ; Next source byte
            inx     d                   ; Next destination memory cell
            dcr     c                   ; Decrement counter
            jmp     loop

done:       ret


source:     db      1, 2, 3, 4, 5, 6, 7, 8, 9, 10
dest:       ds      10

            end