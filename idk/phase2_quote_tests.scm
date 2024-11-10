;;; Test cases for Scheme quote special form, Phase 2.

;;; *** Add more of your own here! ***

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

(quote x)
; expect x

'()
; expect ()

'(quote x)
; expect (quote x)

'(+ 1 3)
; expect (+ 1 3)

''x
; expect (quote x)
