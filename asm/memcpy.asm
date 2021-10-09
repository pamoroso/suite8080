; Copy a block of memory. Runs on a bare system with no host environment.

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

done:       hlt

source:     db      1, 2, 3, 4, 5, 6, 7, 8, 9, 10
dest:       ds      10
            end