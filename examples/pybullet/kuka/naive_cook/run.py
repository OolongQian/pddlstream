#!/usr/bin/env python

from __future__ import print_function

import argparse
import cProfile
import pstats

from examples.pybullet.utils.pybullet_tools.kuka_primitives import BodyPose, BodyConf, Command, get_grasp_gen, \
	get_stable_gen, get_ik_fn, get_free_motion_gen, get_holding_motion_gen, get_movable_collision_test
from examples.pybullet.utils.pybullet_tools.utils import WorldSaver, connect, get_pose, set_pose, Pose, Point, \
	set_default_camera, stable_z, get_configuration, load_model, is_placement, get_body_name, disconnect, \
	DRAKE_IIWA_URDF, get_bodies, user_input, HideOutput
from pddlstream.algorithms.focused import solve_focused
from pddlstream.language.constants import print_solution
from pddlstream.language.generator import from_gen_fn, from_fn
from pddlstream.utils import read, INF, get_file_path, find_unique


def get_fixed(robot, movable):
	rigid = [body for body in get_bodies() if body != robot]
	fixed = [body for body in rigid if body not in movable]
	return fixed


def place_movable(certified):
	placed = []
	for literal in certified:
		if literal[0] == 'not':
			fact = literal[1]
			if fact[0] == 'trajcollision':
				_, b, p = fact[1:]
				set_pose(b, p.pose)
				placed.append(b)
	return placed


def get_free_motion_synth(robot, movable=[], teleport=False):
	fixed = get_fixed(robot, movable)
	
	def fn(outputs, certified):
		assert (len(outputs) == 1)
		q0, _, q1 = find_unique(lambda f: f[0] == 'freemotion', certified)[1:]
		obstacles = fixed + place_movable(certified)
		free_motion_fn = get_free_motion_gen(robot, obstacles, teleport)
		return free_motion_fn(q0, q1)
	
	return fn


def get_holding_motion_synth(robot, movable=[], teleport=False):
	fixed = get_fixed(robot, movable)
	
	def fn(outputs, certified):
		assert (len(outputs) == 1)
		q0, _, q1, o, g = find_unique(lambda f: f[0] == 'holdingmotion', certified)[1:]
		obstacles = fixed + place_movable(certified)
		holding_motion_fn = get_holding_motion_gen(robot, obstacles, teleport)
		return holding_motion_fn(q0, q1, o, g)
	
	return fn


#######################################################

def pddlstream_from_problem(robot, movable=[], teleport=False, grasp_name='top'):
	# assert (not are_colliding(tree, kin_cache))
	
	domain_pddl = read(get_file_path(__file__, 'domain.pddl'))
	stream_pddl = read(get_file_path(__file__, 'stream.pddl'))
	constant_map = {}
	
	print('Robot:', robot)
	conf = BodyConf(robot, get_configuration(robot))
	init = [('CanMove',), ('Conf', conf), ('AtConf', conf), ('HandEmpty',)]
	
	fixed = get_fixed(robot, movable)
	print('Movable:', movable)
	print('Fixed:', fixed)
	for body in movable:
		pose = BodyPose(body, get_pose(body))
		init += [('Graspable', body), ('Pose', body, pose), ('AtPose', body, pose)]
		for surface in fixed:
			init += [('Stackable', body, surface)]
			if is_placement(body, surface):
				init += [('Supported', body, pose, surface)]
	
	for body in fixed:
		name = get_body_name(body)  # retrieves robot name in .urdf file.
		if 'sink' in name:
			init += [('Sink', body)]
		if 'stove' in name:
			init += [('Stove', body)]
		if 'serve' in name:
			init += [('Serve', body)]
	
	goal = ('and', ('AtConf', conf), ('Cleaned', movable[0]))
	# goal = ('and', ('AtConf', conf), ('Cleaned', movable[0]), ('Cleaned', movable[1]))
	# goal = ('and', ('AtConf', conf), ('Served', movable[0]), ('Cleaned', movable[1]))
	# goal = ('and', ('AtConf', conf), ('Served', movable[0]), ('Cooked', movable[1]))
	# goal = ('and', ('AtConf', conf), ('Served', movable[0]), ('Served', movable[1]))

	stream_map = {'sample-pose': from_gen_fn(get_stable_gen(fixed)),
	              'sample-grasp': from_gen_fn(get_grasp_gen(robot, grasp_name)),
	              'inverse-kinematics': from_fn(get_ik_fn(robot, fixed, teleport)),
	              'plan-free-motion': from_fn(get_free_motion_gen(robot, fixed, teleport)),
	              'plan-holding-motion': from_fn(get_holding_motion_gen(robot, fixed, teleport)),
	              'TrajCollision': get_movable_collision_test(), }
	
	return domain_pddl, constant_map, stream_pddl, stream_map, init, goal


#######################################################

def load_local_model(rel_path, asset_name, pose=None, **kwargs):
	import os
	from examples.pybullet.utils.pybullet_tools.utils import load_pybullet
	abs_path = os.path.join(rel_path, asset_name)
	body = load_pybullet(abs_path, **kwargs)
	if pose is not None:
		set_pose(body, pose)
	return body
	


def load_world():
	# TODO: store internal world info here to be reloaded
	import sys, os
	local_model_path = sys.argv[0]  # get current script directory.
	local_model_path = os.path.split(local_model_path)[0]  # remove run.py.
	local_model_path = os.path.join(local_model_path, 'models')  # join models folder.
	with HideOutput():
		robot = load_model(DRAKE_IIWA_URDF)
		floor = load_local_model(local_model_path, 'short_floor.urdf')
		sink = load_local_model(local_model_path, 'sink.urdf', pose=Pose(Point(x=-0.5)))
		stove = load_local_model(local_model_path, 'stove.urdf', pose=Pose(Point(x=+0.5)))
		serve = load_local_model(local_model_path, 'serve.urdf', pose=Pose(Point(x=+0.5, y=+0.5)))
		celery = load_local_model(local_model_path, 'block_for_pick_and_place.urdf', fixed_base=False)
		radish = load_local_model(local_model_path, 'block_for_pick_and_place_mid_size.urdf', fixed_base=False)
	
	body_names = {sink: 'sink', stove: 'stove', celery: 'celery', radish: 'radish', serve: 'serve'}
	movable_bodies = [celery, radish]
	
	set_pose(celery, Pose(Point(y=0.5, z=stable_z(celery, floor))))
	set_pose(radish, Pose(Point(y=-0.5, z=stable_z(radish, floor))))
	
	set_default_camera()
	
	return robot, body_names, movable_bodies


def postprocess_plan(plan):
	paths = []
	for name, args in plan:
		if name == 'place':
			paths += args[-1].reverse().body_paths
		elif name in ['move', 'move_free', 'move_holding', 'pick']:
			paths += args[-1].body_paths
	return Command(paths)


#######################################################

def main(display=True, teleport=False):
	parser = argparse.ArgumentParser()  # Automatically includes help
	parser.add_argument('-viewer', action='store_true', help='enable viewer.')
	parser.add_argument('-simulate', action='store_true', help='enable viewer.')
	args = parser.parse_args()
	
	connect(use_gui=args.viewer)
	robot, names, movable = load_world()
	saved_world = WorldSaver()
	
	pddlstream_problem = pddlstream_from_problem(robot, movable=movable, teleport=teleport)
	_, _, _, stream_map, init, goal = pddlstream_problem
	print('Init:', init)
	print('Goal:', goal)
	print('Streams:', stream_map.keys())
	print('Synthesizers:', stream_map.keys())
	print(names)
	
	pr = cProfile.Profile()
	pr.enable()
	solution = solve_focused(pddlstream_problem, success_cost=INF)
	# solution = solve_incremental(pddlstream_problem)
	print_solution(solution)
	"plan is a sequence of action primitives with grounded values."
	plan, cost, evaluations = solution
	pr.disable()
	pstats.Stats(pr).sort_stats('tottime').print_stats(10)
	if plan is None:
		return
	
	if (not display) or (plan is None):
		disconnect()
		return
	
	if not args.viewer:  # TODO: how to reenable the viewer
		disconnect()
		connect(use_gui=True)
		load_world()
	else:
		saved_world.restore()
	
	"Extract and integrate control command in plan." \
	"Only place, move, move_free, move_holding, pick will create actual command." \
	"But what if I want to let more primitives to move?"
	command = postprocess_plan(plan)
	if args.simulate:
		user_input('Simulate?')
		command.control()
	else:
		user_input('Execute?')
		command.refine(num_steps=10).execute(time_step=0.001)
	
	user_input('Finish?')
	disconnect()


if __name__ == '__main__':
	main()
