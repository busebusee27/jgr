;;; Test cases for eval procedure, Phase 2.

;;; *** Add more of your own here! ***

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

(eval 3 (null-environment 5))
; expect 3

(eval '(+ 1 3) (scheme-report-environment 5))
; expect 4

(eval ''x (null-environment 5))
; expect x
