#!/usr/bin/env python

import argparse

from examples.pybullet_.utils.pybullet_tools.kuka_primitives import get_stable_gen, get_ik_fn, get_free_motion_gen, \
	get_grasp_gen, BodyPose, BodyConf, get_holding_motion_gen
from examples.pybullet_.utils.pybullet_tools.utils import connect, set_pose, Pose, Point, set_default_camera, stable_z, \
	load_model, disconnect, DRAKE_IIWA_URDF, get_bodies, HideOutput, get_pose, get_configuration, set_joint_positions, \
	get_movable_joints

def load_local_model(rel_path, asset_name, pose=None, **kwargs):
	import os
	from examples.pybullet_.utils.pybullet_tools.utils import load_pybullet
	abs_path = os.path.join(rel_path, asset_name)
	body = load_pybullet(abs_path, **kwargs)
	if pose is not None:
		set_pose(body, pose)
	return body


def load_world():
	"""
	Load object models into simulation environment.
	return some objects information.
	:returns robot, body_names, movable_bodies.
	"""
	# TODO: store internal world info here to be reloaded
	import sys, os
	# what local path to be curFolder/models.
	local_model_path = sys.argv[0]  # get current script directory.
	local_model_path = os.path.split(local_model_path)[0]  # remove run.py in directory.
	local_model_path = os.path.join(local_model_path, 'models')  # join models folder.
	
	with HideOutput():
		robot = load_model(DRAKE_IIWA_URDF)
		floor = load_local_model(local_model_path, 'short_floor.urdf')
		
		sink = load_local_model(local_model_path, 'sink_plate.urdf', pose=Pose(Point(x=-0.5, z=+0.05)))
		stove = load_local_model(local_model_path, 'stove_plate.urdf', pose=Pose(Point(x=+0.5, z=+0.05)))
		serve = load_local_model(local_model_path, 'serve_plate.urdf', pose=Pose(Point(x=+0.5, y=+0.5, z=+0.05)))
		mug = load_local_model(local_model_path, 'mug.urdf', fixed_base=False)
	
	body_names = {sink: 'sink', stove: 'stove', serve: 'serve', mug: 'mug'}
	movable_bodies = [mug, ]
	
	set_pose(mug, Pose(Point(y=0.5, z=stable_z(mug, floor))))
	
	set_default_camera()
	
	return robot, body_names, movable_bodies


def graspTask(robot, movable, samplers):
	grasp_sampler, inverse_kinematics, free_motion_planner, holding_motion_planner = samplers
	
	init_conf = BodyConf(robot, get_configuration(robot))  # create BodyConf class for body configuration.
	
	obj = movable[0]
	
	grasps = [body_grasp for body_grasp in grasp_sampler(obj)]
	
	pose = BodyPose(obj, get_pose(obj))
	
	conf, gCommand, grasp = None, None, None
	for grasp in grasps:
		grasp = grasp[0]
		if inverse_kinematics(obj, pose, grasp) is not None:
			conf, gCommand = inverse_kinematics(obj, pose, grasp)
			break
	
	init_conf.assign()  # use .assign() to setJointPosition.

	mCommand = None
	if conf is not None:
		conf0 = BodyConf(robot, get_configuration(robot))
		mCommand = free_motion_planner(conf0, conf)[0]
	
	hCommand = None
	conf.assign()  # start from the end of free-motion-plan.
	mug_pose = BodyPose(obj, get_pose(obj))  # cache mug pose.
	if mCommand is not None:
		hCommand = holding_motion_planner(conf, conf0, robot, grasp)[0]
	mug_pose.assign()  # reset mug pose.
	
	if gCommand is not None and mCommand is not None and hCommand is not None:
		"""
		Control function really exactly calls the physics simulator to perform the joint control.
		We need to understand that the control signals are stored inside the list of Command class.
		Command instance has a field called body_path, BodyPath.body_path, where there are not only
			BodyPath class but Attach class, etc...
		We see that Kuka_primitives has implemented Command, BodyPath, Attach, Detach.
			And pr2 has implemented Command, Trajectory, GripperCommand, Attach, Detach, Clean, Cook, Register.
			This may mean that each primitive has its respective control implementation.
		"""
		mCommand.execute()
		gCommand.execute()
		hCommand.execute()
		
		"""
		Execute function conducts BodyPath command via set_joint_positions(self.body, self.joints, configuration).
		Instead of real physical simulation.
		"""
		# mCommand.execute(time_step=0.001)
		# gCommand.execute(time_step=0.001)


def main():
	parser = argparse.ArgumentParser()  # Automatically includes help
	parser.add_argument('-viewer', action='store_true', help='enable viewer.')
	parser.add_argument('-simulate', action='store_true', help='enable viewer.')
	args = parser.parse_args()
	
	connect(use_gui=args.viewer)
	robot, names, movable = load_world()
	
	fixed = [body for body in get_bodies() if body not in movable and body != robot]
	
	# streams
	"Sampled pose not collide with fixed objects."
	pose_sampler = get_stable_gen(fixed)
	
	"Robot grasp."
	grasp_name = 'top'
	grasp_sampler = get_grasp_gen(robot, grasp_name)
	
	"Inverse kinematics not collide with fixed objects."
	inverse_kinematics = get_ik_fn(robot, fixed)
	
	"motion planner with obstacles"
	free_motion_planner = get_free_motion_gen(robot, fixed)
	
	holding_motion_planner = get_holding_motion_gen(robot, fixed)
	
	graspTask(robot, movable, [grasp_sampler, inverse_kinematics, free_motion_planner, holding_motion_planner])
	
	disconnect()


if __name__ == '__main__':
	main()
