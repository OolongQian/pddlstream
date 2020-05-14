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

		; Augmented robotic elements.
        (Grasp ?o ?g)

        (Kin ?o ?p ?g ?q ?t)
        (FreeMotion ?q1 ?t ?q2)
        (HoldingMotion ?q1 ?t ?q2 ?o ?g)
        (Supported ?o ?p ?r)
        ; (TrajCollision ?t ?o2 ?p2)  ; No collision checking by now.

		(AtPose ?o ?p)
		(AtGrasp ?o ?g)
        (AtConf ?q)

		; Auxiliary predicate. 
		(CanMove) 
	)
	
	; FreeMotion predicate is certified from stream samplers. 
	; For incremental planner, FreeMotion stream would sample N^2 trajectories.
	(:action move_free
		:parameters (?q1 ?q2 ?t) 
		:precondition (and (FreeMotion ?q1 ?t ?q2) 
						(AtConf ?q1) (HandEmpty) (CanMove))
		:effect (and (AtConf ?q2) (not (AtConf ?q1)) (not (CanMove)))
	)
	
	(:action move_holding 
		:parameters (?q1 ?q2 ?o ?g ?t)
		:precondition (and (HoldingMotion ?q1 ?t ?q2 ?o ?g) 
						(AtConf ?q1) (AtGrasp ?o ?g) (CanMove))
		:effect (and (AtConf ?q2) (not (AtConf ?q1)) (not (CanMove)))
	)

	;(:action pick
	;	:parameters (?o ?r)
	;	:precondition (and
	;					(HandEmpty) (Graspable ?o) (On ?o ?r))
	;	:effect (and
	;				(Holding ?o) (not (HandEmpty)) (not (On ?o ?r))))
	
	(:action pick
		:parameters (?o ?p ?g ?q ?t) 
		:precondition (and (Kin ?o ?p ?g ?q ?t)  ; Ensure motion-planner kinematics constraint. 
							(AtPose ?o ?p) (HandEmpty) (AtConf ?q))
		:effect (and (AtGrasp ?o ?g) (CanMove) 
					(not (AtPose ?o ?p)) (not (HandEmpty)))
	)

	;(:action place
	;	:parameters (?o ?r)
	;	:precondition (and
	;					(Holding ?o) (Stackable ?o ?r))
	;	:effect (and
	;				(On ?o ?r) (not (Holding ?o)) (HandEmpty)))

	;(:action pour
	;	:parameters (?po ?r)
	;	:precondition (and
	;					(Holding ?po) (Pourable ?po))
	;	:effect (and
	;				(forall (?o) (when (On ?o ?po) (and (On ?o ?r) (not (On ?o ?po)))))))

	;(:action cook
	;	:parameters (?o ?r)
	;	:precondition (and
	;					(Stove ?r) (On ?o ?r) (Fireproof ?o))
	;	:effect (and
	;				(forall (?f) (when (On ?f ?o) (Cooked ?f)))))

	;(:action serve
	;	:parameters (?o ?r)
	;	:precondition (and
	;					(Serve ?r) (On ?o ?r))
	;	:effect (and
	;				(forall (?f) (when (and (On ?f ?o) (Cooked ?f)) (Served ?f)))))

	(:derived (Holding ?o) 
		(exists (?g) (and (Grasp ?o ?g) 
							(AtGrasp ?o ?g)))
	)
)

