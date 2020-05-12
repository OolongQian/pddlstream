(define (domain cook)
	(:requirements :strips) 
	(:predicates 

		; Type declaration. 
		(Stackable ?o ?r) 
		(Stove ?r) 
		(Serve ?r) 
		(Pourable ?o) 
		(Graspable ?o) 
		(Fireproof ?o) 

		; Attributes. 
		(HandEmpty)
		(Cooked ?o) 
		(Served ?o) 
		
		; Predicates. 
		(On ?o ?r) 
		(Holding ?o) 
	)

	(:action pick
		:parameters (?o ?r) 
		:precondition (and 
						(HandEmpty) (Graspable ?o) (On ?o ?r))
		:effect (and 
					(Holding ?o) (not (HandEmpty)) (not (On ?o ?r)))) 

	(:action place 
		:parameters (?o ?r) 
		:precondition (and 
						(Holding ?o) (Stackable ?o ?r)) 
		:effect (and 
					(On ?o ?r) (not (Holding ?o)) (HandEmpty)))

	(:action pour
		:parameters (?po ?r) 
		:precondition (and 
						(Holding ?po) (Pourable ?po)) 
		:effect (and 
					(forall (?o) (when (On ?o ?po) (and (On ?o ?r) (not (On ?o ?po)))))))
	
	(:action cook
		:parameters (?o ?r)
		:precondition (and 
						(Stove ?r) (On ?o ?r) (Fireproof ?o)) 
		:effect (and 
					(forall (?f) (when (On ?f ?o) (Cooked ?f))))) 
	
	(:action serve 
		:parameters (?o ?r) 
		:precondition (and 
						(Serve ?r) (On ?o ?r))
		:effect (and 
					(forall (?f) (when (and (On ?f ?o) (Cooked ?f)) (Served ?f)))))
)
