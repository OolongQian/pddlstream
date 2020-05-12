(define (domain cook)
	(:requirements :strips) 
	(:predicates 

		; Type declaration. 
		(Stackable ?o ?r) 
		(Stove ?r) 
		(Serve ?r) 
		(Pourable ?o) 
		(Graspable ?o) 

		; Attributes. 
		(HandEmpty)
		(Cooked ?o) 
		(Served ?o) 
		
		; Predicates. 
		(On ?o ?r) 
		(Holding ?o) 
	)
	
	; init = [(Stove stove), (Serve serve), (HandEmpty), (Stackable bottle stove), (Stackable bottle serve), 
				(Stackable bowl stove), (Stackable bowl serve), (Pourable bottle), (On strawberry bottle), 
				(Graspable bottle), (Graspable bowl)]
	

	(:action pick
		:parameters (?o) 
		:precondition (and 
						(HandEmpty) (CanMove) (Graspable ?o))
		:effect (and 
					(Holding ?o) (not (HandEmpty)))) 

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
					(forall (?o) (when (On ?o ?po) (On ?o ?r)))))
	
	(:action cook
		:parameters (?o ?r)
		:precondition (and 
						(Stove ?r) (On ?o ?r)) 
		:effect (and 
					(forall (?f) (when (On ?f ?o) (Cooked ?f))))) 
	
	(:action serve 
		:parameters (?o ?r) 
		:precondition (and 
						(Serve ?r) (On ?o ?r))
		:effect (and 
					(forall (?f) (when (On ?f ?o) (Served ?f)))))
)