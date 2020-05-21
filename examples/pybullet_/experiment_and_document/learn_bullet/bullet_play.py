import pybullet as p
import time

def simulate(steps=10000):
	for _ in range(steps):
		p.stepSimulation()
		time.sleep(1. / 24)
		
def play_constraint():
	p.connect(p.GUI)
	b1 = p.loadURDF('./models/box.urdf', basePosition=[0, 0, 5], useFixedBase=True)
	b2 = p.loadURDF('./models/box.urdf', basePosition=[0, 2, 4], globalScaling=0.5)
	print(b1, b2)
	
	p.createConstraint(b1, -1, b2, -1, p.JOINT_GEAR, [0, 1, 1], [0, 0, 0], [0, 0, 0])
	
	p.setGravity(0, 0, -10)
	
	simulate()

def play_jointLimits():
	p.connect(p.GUI)
	j = p.loadURDF('./models/joint_test.urdf')
	p.setGravity(0, 0, -10)
	simulate()

if __name__ == "__main__":
	#play_jointLimits()
	# play_constraint()
	pass