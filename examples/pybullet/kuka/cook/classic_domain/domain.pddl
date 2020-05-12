(define (domain cook)
	(:requirements :strips) 
	(:predicates 
        (Container ?c)
        (In ?o ?c)
        (Goal ?o)
	)
    (:action pour
        :parameters (?c)
        :precondition (and (Container ?c))
        :effect (and
                    (forall (?o) (when (In ?o ?c) (and (not (In ?o ?c)) (Goal ?o)))))
    )
)