; Uppercase a string. Runs on a bare system with no host environment.

lowera      equ     61h                 ; ASCII lowercase a
lowerz      equ     7ah                 ; ASCII lowercase z
offset      equ     32                  ; lowercase-uppercase offset
len         equ     17                  ; String length


            lxi     h, string
            mvi     c, len
            mvi     d, lowera
            mvi     e, lowerz

loop:       mvi     a, 0
            cmp     c                   ; c == 0?
            jz      done                ; Yes
            mov     a, d
            mov     b, m                ; B holds current character in string
            cmp     b                   ; < a?
            jnc     skip                ; Yes, skip to next character
            mov     a, e
            cmp     b                   ; > z? 
            jc      skip                ; Yes, skip to next character
            mov     a, b
            sui     offset              ; Subtract offset to get uppercase
            mov     m, a
skip:       inx     h
            dcr     c
            jmp     loop

done:       hlt

string:     db      'Mixed Case String'
            end