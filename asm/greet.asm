; Hello world for CP/M


TPA         equ     100h
BDOS        equ     0005h           ; BDOS entry point
WSTRF       equ     09h             ; BDOS function: write string

            org     TPA

            mvi     c, WSTRF
            lxi     d, message
            call    BDOS
            ret

message:    db      'Greetings from Suite8080$'

            end
