import matplotlib.pyplot as plt
import mplcursors

fig = plt.figure(figsize=(5.5, 3.5), facecolor="gainsboro")
fig.canvas.set_window_title("bdsim: eg1.py")
spec = fig.add_gridspec(ncols=2, nrows=2)

ax0 = fig.add_subplot(spec[0])
ax1 = fig.add_subplot(spec[1])
ax2 = fig.add_subplot(spec[2])
plt.tight_layout()

(l1,) = ax0.plot([0, 1], [2, 3], "r--")
ax0.set_title("ax0", fontweight="bold", color="dimgrey")
(l2,) = ax1.plot([0, 1], [3, 2], "b:")
ax1.set_title("ax1", fontweight="bold", color="dimgrey")
(l3,) = ax2.plot([0, 1], [-2, -3], "k")
ax2.set_title("ax2", fontweight="bold", color="dimgrey")

mplcursors.cursor([l1, l2, l3], hover=mplcursors.HoverMode.Transient)


def onclick(event):
    print(f"key={event.key}, axes={event.inaxes}, a1={event.inaxes is ax1}")


# cid = fig.canvas.mpl_connect('key_press_event', onclick)

plt.show(block=True)
