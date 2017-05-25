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

; Information known: I picked apple from "Mixed" crate.
(assert (or (= realMixed Apple) (= realMixed Mixed)))

(check-sat)
(get-model)
