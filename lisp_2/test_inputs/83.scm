(reduce (lambda (x y) (* (/ 1 x) y)) (list 1 2 3 4) 2)
(reduce (lambda (x y) (+ (* 2 x) (* 3 y))) (list 9 8 7 6) 10)
(reduce (lambda (x y) (+ (* 2 x) (* 3 y))) (list) 13)
(reduce append (list (list 1 2 3) (list 4 8 7) (list 9) (list) (list 10 29 38 47 56)) (list))
(reduce append (list (list 1 2 3) (list 4 8 7) (list 9) (list) (list 10 29 38 47 56)) (list 1))
