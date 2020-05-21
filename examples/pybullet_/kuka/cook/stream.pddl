(define (stream cook) 
	; First, implement grasp and hold. 

	(:stream sample-grasp 
		:inputs (?o) 
		:domain (Graspable ?o) 
		:outputs (?g) 
		:certified (Grasp ?o ?g) 
	)

	(:stream inverse-kinematics
		:inputs (?o ?p ?g) 
		:domain (and (Pose ?o ?p) (Grasp ?o ?g)) 
		:outputs (?q ?t) 
		:certified (and (Conf ?q) (Traj ?t) (Kin ?o ?p ?g ?q ?t)) 
	) 

	(:stream plan-free-motion
		:inputs (?q1 ?q2) 
		:domain (and (Conf ?q1) (Conf ?q2))
		:outputs (?t) 
		:certified (FreeMotion ?q1 ?t ?q2) 
	)
)
