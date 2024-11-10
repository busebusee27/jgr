;;; Test cases for Scheme, Phase 1.

;;; *** Add more of your own here! ***

;;; These are examples from several sections of "The Structure
;;; and Interpretation of Computer Programs" by Abelson and Sussman.

;;; License: Creative Commons share alike with attribution

;;; Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48

;;; 1.1.1

10
; expect 10

(+ 137 349)
; expect 486

(- 1000 334)
; expect 666

(* 5 99)
; expect 495

(/ 10 5)
; expect 2

(+ 2.7 10)
; expect 12.7

(+ 21 35 12 7)
; expect 75

(* 25 4 12)
; expect 1200

(+ (* 3 5) (- 10 6))
; expect 19

(+ (* 3 (+ (* 2 4) (+ 3 5))) (+ (- 10 7) 6))
; expect 57

(+ (* 3
      (+ (* 2 4)
         (+ 3 5)
      )
   )
   (+ (- 10 7)
      6
   )
)
; expect 57

(= 3 4)
; expect #f

(= (+ 1 2) 3 (/ 9 3))
; expect #t

(< 3 4 5)
; expect #t

(< 3 4 4)
; expect #f

(<= 3 3)
; expect #t

(apply + (list 1 2 3))
; expect 6

(apply + 1 2 (list 3))
; expect 6
