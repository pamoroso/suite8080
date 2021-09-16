; Hello world for CP/M

            org     100h
bdos        equ     0005h           ; BDOS entry point
wstrf       equ     09h             ; BDOS function: write string

            mvi     c, wstrf
            lxi     d, message
            call    bdos
            ret

message:    db      'Greetings from Suite8080.$'
            end
