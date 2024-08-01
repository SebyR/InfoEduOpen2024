import pybullet as p
import pybullet_data
import time


# Start the physics client
p.connect(p.GUI)

# Load default URDFs from pybullet_data
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Load the plane
p.loadURDF("plane.urdf")

# Set gravity
p.setGravity(0, 0, -9.8)

# Load the simple catapult URDF
catapult_id = p.loadURDF("simple_catapult.urdf", basePosition=[0, 0, 0])

# Optionally, apply a force to the arm link to simulate a catapult action
# Here, we'll set a joint motor control to lift the arm and then release it

# Run the simulation for a short time to observe the catapult motion
while True:
    p.stepSimulation()
    time.sleep(1./240.)

# Disconnect from the simulation
p.disconnect()