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

; Check if there is only one possible assignment: Try to find another model other than output of puzzle1.z3
(assert (not (and (= realApple Orange) (= realOrange Mixed) (= realMixed Apple))))
(check-sat)
