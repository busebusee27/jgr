;;; Error test cases for special forms, Phase 2.

;;; *** Add more of your own here! ***

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

;;; correct tests

(define x 3)
; expect x

x
; expect 3

((lambda (x) 3) 4)
; expect 3

(if #t 3 4)
; expect 3

;;; error tests

(define x 3 4)
; expect Error

(define 4 5)
; expect Error

(lambda (x y x) 3)
; expect Error

(if #t)
; expect Error
