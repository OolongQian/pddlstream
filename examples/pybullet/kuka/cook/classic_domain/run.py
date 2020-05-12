#!/usr/bin/env python

from __future__ import print_function

from pddlstream.algorithms.focused import solve_focused

from pddlstream.algorithms.incremental import solve_incremental
from pddlstream.language.constants import PDDLProblem, And, print_solution

DOMAIN_PDDL = """
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
	;			(Stackable bowl stove), (Stackable bowl serve), (Pourable bottle), (On strawberry bottle),
	;			(Graspable bottle), (Graspable bowl)]
	

	(:action pick
		:parameters (?o)
		:precondition (and
						(HandEmpty) (Graspable ?o))
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
"""

##################################################

def get_problem1():
    constant_map = {}
    stream_pddl = None
    stream_map = {}

    init = [
        ('stove', ),
        ('serve', ),
        ('bottle', ),
        ('bowl', ),
        ('strawberry', ),
        ('HandEmpty', ),
        ('Stackable', 'bottle', 'stove'),
        ('Stackable', 'bottle', 'serve'),
        ('Stackable', 'bowl', 'serve'),
        ('Stackable', 'bowl', 'serve'),
        ('Pourable', 'bottle'),
        ('On', 'strawberry', 'bottle'),
        ('Graspable', 'bottle'),
        ('Graspable', 'bowl')
    ]
    goal = And(
        ('Cooked', 'strawberry')
    )

    return PDDLProblem(DOMAIN_PDDL, constant_map, stream_pddl, stream_map, init, goal)

def solve_pddlstream(focused=True):
    problem_fn = get_problem1  # get_problem1 | get_problem2
    pddlstream_problem = problem_fn()
    print('Init:', pddlstream_problem.init)
    print('Goal:', pddlstream_problem.goal)
    if focused:
        solution = solve_focused(pddlstream_problem, unit_costs=True)
    else:
        solution = solve_incremental(pddlstream_problem, unit_costs=True)
    print_solution(solution)
    #print(*solve_from_pddl(DOMAIN_PDDL, PROBLEM_PDDL))

##################################################

def main():
    solve_pddlstream()

if __name__ == '__main__':
    main()