;;; Test cases for Scheme and / or special forms, Phase 2.

;;; *** Add more of your own here! ***

;;; These are examples from several sections of "The Structure
;;; and Interpretation of Computer Programs" by Abelson and Sussman.

;;; License: Creative Commons share alike with attribution

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

(or #f #t)
; expect #t

(or)
; expect #f

(and)
; expect #t

(or 1 2 3)
; expect 1

(and 1 2 3)
; expect 3

(and #F (/ 1 0))
; expect #f

(and #T (/ 1 0))
; expect Error

(or 3 (/ 1 0))
; expect 3

(or #F (/ 1 0))
; expect Error
