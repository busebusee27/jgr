;;; Test cases for Scheme lambda special form, Phase 2.

;;; *** Add more of your own here! ***

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

((lambda (x) 3) 4)
; expect 3

((lambda (x y)
   (+ x y)
 )
 2 3
)
; expect 5

((lambda (x y)
   (display x)
   (newline)
   (display y)
   (newline)
   (+ x y)
 )
 2 3
)
; expect 2 ; 3 ; 5

(((lambda (x)
    (lambda (y)
      (+ x y)
    )
  )
  2
 )
 3
)
; expect 5
