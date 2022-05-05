import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(11.69, 8.27))
ax = fig.gca()
ax.set_xlim(0, 50)
ax.set_ylim(0, 200)

hl, = plt.plot([], [])


def update_line(hl:plt.Line2D, new_datax:list[float], new_datay:list[float]):
    # re initialize line object each time if your real xdata is not contiguous else comment next line
    hl, = plt.plot([], [])
    hl.set_xdata(np.append(hl.get_xdata(), new_datax))
    hl.set_ydata(np.append(hl.get_ydata(), new_datay))

    fig.canvas.draw_idle()
    fig.canvas.flush_events()


x = 1
while x < 5:
    new_data1 = []
    new_data2 = []
    for i in range(500):
        new_data1.append(i * x)
        new_data2.append(i ** 2 * x)
    update_line(hl, new_data1, new_data2)
    # adjust pause duration here -> this argument is key to display updates and load the GUI if not already showing
    if __name__ == '__main__':
        plt.pause(1)
    else:
        print('NOT SHOWING PYPLOTS AS RUNNING PYTESTS...')
    x += 1

else:
    print("DONE")
