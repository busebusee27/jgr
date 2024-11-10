;;; Test cases for Scheme define special form, Phase 2.

;;; *** Add more of your own here! ***

;;; These are examples from several sections of "The Structure
;;; and Interpretation of Computer Programs" by Abelson and Sussman.

;;; License: Creative Commons share alike with attribution

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

(define size 2)
; expect size
size
; expect 2

(* 5 size)
; expect 10

(define pi 3.14159)
(define radius 10)
(* pi (* radius radius))
; expect 314.159

(define circumference (* 2 pi radius))
circumference
; expect 62.8318

;;; 1.1.4

(define (square x) (* x x))
; expect square
(square 21)
; expect 441


(square (+ 2 5))
; expect 49

(square (square 3))
; expect 81

(define (sum-of-squares x y)
  (+ (square x) (square y)))
(sum-of-squares 3 4)
; expect 25

(define (f a)
  (sum-of-squares (+ a 1) (* a 2)))
(f 5)
; expect 136
