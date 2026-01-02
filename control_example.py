import control as ct
import matplotlib.pyplot as plt

# Define the system
s = ct.tf('s')
sys = 10 / (s**2 + 2*s + 10)

# GET the data: returns (time, outputs)
time, output = ct.step_response(sys)

# View the values
print("Time steps:", time[:5]) # Print first 5
print("Output:", output[:5])

# Plot the result
plt.plot(time, output)
plt.title("Step Response")
plt.xlabel("Time")
plt.ylabel("Output")
plt.grid(True)
plt.show()