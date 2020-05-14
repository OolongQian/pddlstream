I would like to implement a cook task setting.

First, I would like to realize a classic pddl planning domain.

I find, in examples.advanced folder is there a python file that invokes fastDownward from within.

I have little experience in programming PDDL, thus I do this step-by-step.

I copy a gripper example from FastDownward experiment example, whose correctness is ensured.

I implement a classic pddl domain & problem in /callFastDownward folder, and use launch.sh to invoke FastDownward
    in shell. The correctness is ensured.

Then, I copy the correct .pddl implementation into classic_domain/run.py.

I suddenly start to question whether focused_algorithm support Forall and Exist.

I am pretty sure that the focused algorithm cannot support Universal and Existential quantifiers.

The next thing is augmenting cook domain.pddl into a pddlstream one, consisting of realistic robotic constraints.

The first is adding robotic elements, including (Object Pose), (Grasp), (Kin), (FreeMotion), (Supported).

Then, augment actions one-by-one, and call increment planner to check it one-by-one. 

I find the unsafe trajectory is not activated in kuka problem instance, and I am wondering why this happens. 

I also find unsafe trajectory is activated in pr2 example. 

I deep into the error message in kuka example, and find the NotImplementedError: Fluent stream is required for another stream: plan-free-motion...

I find their difference is that, in the plan-free-motion has a :fluents (AtPose) attached to it. 

I commented out the :fluents, but encounter a key error. 

I want to figure out what is the problem in :fluents. 

It seems that the fluent key word is added because of no other choices. 

I am about to give up this repository, but finally I would like to figure out why pr2 is OK. 

I find sometimes PR2 is not OK. 

I plan to ignore collision checking by now. 

OK, the first step, grasp an object is done!

The next step is to import task related objects. 

Note, the bytes.decode("UTF-8") problem is in util, which cannot be committed in my version, I need to be careful. 

After importing .stl linked object model, other shitty things happen.

The grasp sampler seems not working because the code that queries the simulator information is not working. 
