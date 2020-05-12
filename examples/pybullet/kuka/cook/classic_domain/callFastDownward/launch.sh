#!/bin/bash

#../../../../../../FastDownward/fast-downward.py ./gripper/domain.pddl ./gripper/prob01.pddl --search "lazy_greedy([ff()], preferred=[ff()])"

../../../../../../FastDownward/fast-downward.py --alias lama-first ./domain.pddl ./problem.pddl 
