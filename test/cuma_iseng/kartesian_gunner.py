import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.axhline(0, color='blue', linewidth=3)  
ax.axvline(0, color='blue', linewidth=3) 

for x in [-2, -1, 1, 2]:
    ax.plot([x, x], [-0.1, 0.1], color='blue', linewidth=3)
for y in [-2, -1, 1, 2]:
    ax.plot([-0.1, 0.1], [y, y], color='blue', linewidth=3)


ax.plot([0, -0.1, 0.1], [-2, -2.2, -2], color='blue', linewidth=3)


ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_aspect('equal')
ax.axis('off')

plt.show()
