; Uppercase a string.
;
; The program runs on CP/M but you need a debugger like DDT or SID to inspect the
; process and the machine state. From SID start the program with this command,
; which runs it until the breakpoint at address 'done':
;
; g,.done


lowera      equ     61h                 ; ASCII lowercase a
lowerz      equ     7ah                 ; ASCII lowercase z
offset      equ     32                  ; lowercase-uppercase offset
len         equ     17                  ; String length


            org     100h

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

done:       ret


string:     db      'Mixed Case String'

            end