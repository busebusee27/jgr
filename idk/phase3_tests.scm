;;; Test cases for Scheme, Phase 3.

;;; *** Add more of your own here! ***

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

; Tail call optimization test
(define (sum n total)
  (if (zero? n) total
    (sum (- n 1) (+ n total))
  )
)
(sum 1001 0)
; expect 501501
