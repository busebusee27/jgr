;;; Test cases for begin special form, Phase 2.

;;; *** Add more of your own here! ***

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

(begin 
  (+ 1 2)
)
; expect 3

(begin 
  (+ 3 4)
  (+ 1 2)
)
; expect 3

(begin 
  (display (+ 3 4))
  (newline)
  (display (+ 1 2))
  (newline)
)
; expect 7 ; 3 ; okay
