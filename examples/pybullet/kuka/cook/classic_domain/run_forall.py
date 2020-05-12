#!/usr/bin/env python

from __future__ import print_function

from pddlstream.algorithms.focused import solve_focused

from pddlstream.algorithms.incremental import solve_incremental
from pddlstream.language.constants import PDDLProblem, And, print_solution

DOMAIN_PDDL = """
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
"""

##################################################

def get_problem1():
    constant_map = {}
    stream_pddl = None
    stream_map = {}

    init = [
        ('Container', 'c'),
        ('In', 'o1', 'c')
    ]
    goal = And(
        ('Goal', 'o1')
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