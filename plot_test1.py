import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
fig = plt.figure()
ax = fig.add_subplot(111)
xs = [0,1,2,3,4,5,6,7,8,9,10,11]
ys = [0,1,2,3,4,5,6,7,8,9,10,11]
labels = list('abcdefghijklmnopqrstuvwxyz')


def format_fn(tick_val, tick_pos):
    if int(tick_val) in xs:
        return labels[int(tick_val)]
    else:
        return ''


ax.xaxis.set_major_formatter(FuncFormatter(format_fn))
ax.plot(xs, ys)
plt.show()