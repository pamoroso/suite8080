; Example of using m4 as an Assembly macro processor: macro definition


; The ldabc macro loads a, b, c with the bytes of data from the memory locations
; specified by the arguments $1, $2, and $3. It's called like this:
;
;   ldabc(arg1, arg2, arg3)
  
define(`ldabc',`
            lhld    $1
            mov     a, m
            lhld    $2
            mov     b, m
            lhld    $3
            mov     c, m
')
