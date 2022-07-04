; Twirling bar animation.
;
; Runs on CP/M with an ANSI terminal. Press any key to quit the program.


TPA        equ      100h
BDOS       equ      0005h
WRITESTR   equ      09h                ; Write string
WRITECHR   equ      02h                ; Write character
CONSTAT    equ      0bh                ; Console status

FRAMES     equ      8                  ; Number of animation frames


           org      TPA
            
           mvi      c, WRITESTR
           lxi      d, cls             ; Clear screen
           call     BDOS

loop:      lxi      h, anim            ; Initialize frame pointer...
           mvi      b, FRAMES          ; ...and count

loop1:     push     h
           push     b
           mvi      c, WRITESTR
           lxi      d, home            ; Go to screen home
           call     BDOS
           pop      b
           pop      h

           push     h
           push     b
           mvi      c, WRITECHR
           mov      e, m               ; Print current frame
           call     BDOS
           pop      b
           pop      h

           push     h
           push     b
           mvi      c, CONSTAT         ; Get console status
           call     BDOS
           pop      b
           pop      h
           ora      a                  ; Key pressed?
           jnz      exit               ; Yes

           inx      h                  ; Point to next frame
           dcr      b                  ; One fewer frame
           jnz      loop1

           jmp      loop

exit:      ret


cls:       db       1bh, '[2J$'        ; ANSI clear screen: ESC [ 2 J
home:      db       1bh, '[H$'         ; ANSI go to screen home: ESC [ H
anim:      db       '|/-\|/-\'         ; 8 frames

           end