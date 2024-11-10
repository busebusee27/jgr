;;; Test cases for Scheme if special form, Phase 2.

;;; *** Add more of your own here! ***

;;; These are examples from several sections of "The Structure
;;; and Interpretation of Computer Programs" by Abelson and Sussman.

;;; License: Creative Commons share alike with attribution

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

(if 0 1 2)
; expect 1

(if (list) 1 2)
; expect 1

(if #t 1 (/ 1 0))
; expect 1

(if #f (/ 1 0) 2)
; expect 2

(if 0 (+ 1 2))
; expect 3

(if #f (/ 1 0))
; expect okay
