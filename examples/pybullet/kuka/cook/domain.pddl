(define (domain cook)
	(:requirements :strips :equality)
	(:predicates
		
		; Type declaration. 
		(Stackable ?o ?r)  ; Can stack an object onto the region? 
		
		; Declare region. 
		(Stove ?r) 
		(Serve ?r) 

		; Declare object. 
		; No need to declare because the object property can be characterized by (Stackable), can other preciates (AtPose)...

		; Object predicates. 
		(AtPose ?o ?p)
		(AtGrasp ?o ?p) 
		
		; Robot predicates.  
		(HandEmpty)
		(AtConf ?q) 
		(CanMove)  ; Prevent robot from hanging around back and forth. 
		
		; Setting related predicates. 
		(Cooked ?o) 
		(served ?o) 

		; Derived predicates. 
		(On ?o ?r)
		(Holding ?o)
	)

	(:action 
