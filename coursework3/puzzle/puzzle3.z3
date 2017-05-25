; Variable declaration
(declare-datatypes () ((Crate Apple Orange Mixed)))
(declare-const realApple Crate)
(declare-const realOrange Crate)
(declare-const realMixed Crate)

; Basic conditions: the values should be distinct.
(assert (distinct realApple realOrange realMixed))

; Information known: none of the crates has the right label.
(assert (not (= realApple Apple)))
(assert (not (= realOrange Orange)))
(assert (not (= realMixed Mixed)))

; Information known: I picked apple from "Orange" crate.
(assert (or (= realOrange Apple) (= realOrange Mixed)))

(check-sat)
(get-model)

; Use observed output
(assert (not (and (= realApple Orange) (= realOrange Mixed) (= realMixed Apple))))

; Check uniqueness. If sat, the solution is not unique.
(check-sat)
(get-model)
