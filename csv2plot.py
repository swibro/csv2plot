import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import seaborn as sns
import pandas as pd
from pathlib import Path
import toml
import tomllib
from globals import *

use_toml = False

if sys.argv[1] == '-h':
    print("Type 'csv2plot -e' to adjust settings")
    sys.exit(0)

def fmt(val):
    if abs(val) < 1e-3:
        return f"{val:.3e}"
    return f"{val:.3f}"

def ifprint(msg):
    if not use_toml:
        print(msg)

def getvalue(type=int, config_key=None):
    if use_toml:
        return config_key
    else:
        return type(input())


plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'



# =====LOAD DATA========

file = sys.argv[1]
path = Path(file).expanduser()
config_dir = Path(__file__).parent
config_path = config_dir / 'config.toml'

data = np.genfromtxt(path, delimiter=',', names=True, dtype=None, encoding=None)

labels = data.dtype.names
x = data[labels[0]]
y_labels = labels[1:]
y_data = np.array([data[name] for name in y_labels]).T

if y_data.ndim == 1:
    y_data = np.atleast_2d(y_data).T


print("Use config file? (y/n)")
if input() == 'y':
    use_toml = True
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

TRENDLINE_COLOR = config['TRENDLINE_COLOR']
TRENDLINE_WIDTH = config['TRENDLINE_WIDTH']
SPLINE_COLOR = config['SPLINE_COLOR']
SPLINE_WIDTH = config['SPLINE_WIDTH']
MARKER_SIZE = config['MARKER_SIZE']
MARKER_SHAPE = config['MARKER_SHAPE']
MARKER_COLOR = config['MARKER_COLOR']
ERROR_BAR_COLOR = config['ERROR_BAR_COLOR']
HEATMAP_COLOR = config['HEATMAP_COLOR']
FONT_SIZE = config['FONT_SIZE']

plt.rcParams.update({'font.size': FONT_SIZE})

# =======PLOT STYLE=======

ifprint("scatter (1) - smooth (2) - heatmap (3)")
# For heatmap column 0 is x, 1 is y, 2 is value
plot_type: int = getvalue(int, config['plot_type'])
if plot_type not in [1, 2, 3]:
    print("Error: Invalid plot type")
    sys.exit(1)

if plot_type in [1, 2]:
    ifprint("Show gridlines? (y/n):")
    gridlines = getvalue(str, config['gridlines'])
    if gridlines == 'y':
        plt.grid(True)
    ifprint("Custom x bounds? (y/n):")
    xbounds = getvalue(str, config['xbounds'])
    if xbounds == 'y':
        ifprint("xmin:")
        xmin = getvalue(float, config['xmin'])
        ifprint("xmax:")
        xmax = getvalue(float, config['xmax'])
        if xmin >= xmax:
            print("Error: xmax must be greater than xmin")
            sys.exit(1)
        ifprint("x tick interval (0 for default):")
        xtickint = getvalue(float, config['xtickint'])
    ifprint("x axis on top? (y/n):")
    xtop = getvalue(str, config['xtop'])
    ifprint("Hide x axis? (y/n):")
    hidex = getvalue(str, config['hidex'])
    if xtop == 'y':
        plt.gca().xaxis.tick_top()
        plt.gca().xaxis.set_label_position('top')
    if hidex == 'y':
        plt.gca().xaxis.set_visible(False)
    ifprint("Custom y bounds? (y/n):")
    ybounds = getvalue(str, config['ybounds'])
    if ybounds == 'y':
        ifprint("ymin:")
        ymin = getvalue(float, config['ymin'])
        ifprint("ymax:")
        ymax = getvalue(float, config['ymax'])
        if ymin >= ymax:
            print("Error: ymax must be greater than ymin")
            sys.exit(1)
        ifprint("y tick interval (0 for default):")
        ytickint = getvalue(float, config['ytickint'])
    ifprint("Hide y axis? (y/n):")
    hidey = getvalue(str, config['hidey'])
    if hidey == 'y':
        plt.gca().yaxis.set_visible(False)
    ifprint("x axis log scale? (y/n):")
    xlogscale = getvalue(str, config['xlogscale'])
    if xlogscale == 'y':
        if xbounds == 'y' and xmin <= 0:
            print("Error: xmin must be greater than 0 for log scale")
            sys.exit(1)
        plt.xscale('log')
    ifprint("y axis log scale? (y/n):")
    ylogscale = getvalue(str, config['ylogscale'])
    if ylogscale == 'y':
        if ybounds == 'y' and ymin <= 0:
            print("Error: ymin must be greater than 0 for log scale")
            sys.exit(1)
        plt.yscale('log')

    if xbounds == 'y':
        plt.xlim(xmin, xmax)
        if xtickint != 0:
            plt.xticks(np.arange(xmin, xmax, xtickint))
    if ybounds == 'y':
        plt.ylim(ymin, ymax)
        if ytickint != 0:
            plt.yticks(np.arange(ymin, ymax, ytickint))


    ifprint("x-axis title:")
    xlabel = getvalue(str, config['xlabel'])
    ifprint("y-axis title:")
    ylabel = getvalue(str, config['ylabel'])
    ifprint("legend? (y/n):")
    legend = getvalue(str, config['legend'])



elif plot_type == 3:
    ifprint("x-axis title:")
    xlabel = getvalue(str, config['xlabel'])
    ifprint("y-axis title:")
    ylabel = getvalue(str, config['ylabel'])
    ifprint("Colorbar title:")
    cbar_label = getvalue(str, config['cbar_label'])
    ifprint("Custom colorbar bounds? (y/n):")
    cbar_bounds = getvalue(str, config['cbar_bounds'])
    if cbar_bounds == 'y':
        ifprint("cbar min:")
        cbar_min = getvalue(float, config['cbar_min'])
        ifprint("cbar max:")
        cbar_max = getvalue(float, config['cbar_max'])


# leave here, if need to change find next occurance
avg_all = False
same_color_bool = False
# avg_start = 0
# avg_end = 0
# error_bars = 'n'




# ======AVERAGING=======

if plot_type in [1, 2]:
    if y_data.shape[1] > 1:
        ifprint("Average y columns? (y/n)")
        average = getvalue(str, config['average'])
        if average == 'y':
            ifprint("Average from column: ")
            avg_start = getvalue(int, config['avg_start'])
            ifprint("Average to column [(0) for last]: ")
            avg_end = getvalue(int, config['avg_end'])
            if avg_end == 0:
                avg_end = y_data.shape[1] - 1
            if avg_start < 0 or avg_end >= y_data.shape[1] or avg_start > avg_end:
                print("Error: Invalid average range")
                sys.exit(1)
            y_to_avg = y_data[:, avg_start:avg_end+1]
            y_avg = np.mean(y_to_avg, axis=1)
            y_std = np.std(y_to_avg, axis=1)
            if avg_start > 0 and avg_end < y_data.shape[1] - 1:
                y_data = np.column_stack((y_data[:, :avg_start], y_avg, y_data[:, avg_end+1:]))
                y_labels = list(y_labels[:avg_start]) + ['Average'] + list(y_labels[avg_end+1:])
            elif avg_start > 0:
                y_data = np.column_stack((y_data[:, :avg_start], y_avg))
                y_labels = list(y_labels[:avg_start]) + ['Average']
            elif avg_end < y_data.shape[1] - 1:
                y_data = np.column_stack((y_avg, y_data[:, avg_end+1:]))
                y_labels = ['Average'] + list(y_labels[avg_end+1:])
            else:
                y_data = np.array([y_avg]).T
                avg_all = True
            ifprint("Error bars? (y/n)")
            error_bars = getvalue(str, config['error_bars'])
        if not avg_all:
            ifprint("Make all datapoints same color? (y/n)")
            same_color = getvalue(str, config['same_color'])
            if same_color == 'y':
                same_color_bool = True
        else:
            same_color_bool = True
    else:
        same_color_bool = True


# =======PLOT FUNCTIONS=======

# ====SCATTER=====
def scatter():
    ifprint("Trendline? (y/n):")
    trend = getvalue(str, config['trend'])
    if trend == 'y':
        fit_params = []
        fit = []
        if y_data.shape[1] > 1:
            ifprint("Dataset index for trendline [(-1) for all series]: ")
            if not use_toml:
                trend_index.append(int(input()))
            else:
                trend_index = config['trend_index']
            ifprint("Another series? (y/n)")
            if not use_toml:
                another_series = input()
                while another_series == 'y':
                    print("Type next index: ")
                    trend_index.append(int(input()))
                    print("Another series? (y/n)")
                    another_series = input()
        else:
            trend_index = [0]
        for i in trend_index:
            fit_params.append(np.polyfit(x, y_data[:, i], 1))
        for i in range(0, len(fit_params)):
            fit.append(np.poly1d(fit_params[i]))
        for i in range(0, len(fit_params)):
            plt.plot(
                x,
                fit[i](x),
                color=TRENDLINE_COLOR,
                linewidth=TRENDLINE_WIDTH,
                zorder=1
            )
        if len(trend_index) == 1:
            ifprint("Show equation? (y/n)")
            show_equation = getvalue(str, config['show_equation'])
            if show_equation == 'y':
                for i in range(0, len(trend_index)):
                    plt.text(
                        0.05,
                        0.90,
                        f"y = {fmt(fit_params[i][0])}x + {fmt(fit_params[i][1])}",
                        transform=plt.gca().transAxes,
                        verticalalignment='top'
                    )
                    y_pred = fit(x)
                    r2 = (
                        1
                        - np.sum((y_data[trend_index[i]] - y_pred) ** 2)
                        / np.sum((y_data[trend_index[i]] - np.mean(y_data[trend_index[i]])) ** 2)
                    )
                    plt.text(
                        0.05,
                        0.82,
                        f"R$^2$ = {r2:.4f}",
                        transform=plt.gca().transAxes
                    )
    ifprint("Connect points? (y/n): ")
    connect_points = getvalue(str, config['connect_points'])
    for i in range(0, y_data.shape[1] if not avg_all else 1):
        if error_bars == 'y' and i == avg_start:
            plt.errorbar(
                x,
                y_data[:, i] if not avg_all else y_data.squeeze(),
                yerr=y_std,
                fmt=MARKER_SHAPE,
                color=MARKER_COLOR if same_color_bool else None,
                ecolor=ERROR_BAR_COLOR,
                elinewidth=1,
                capsize=3,
                label='Mean ± Std Dev.'
            )
        else:
            plt.scatter(
                x,
                y_data[:, i],
                marker=MARKER_SHAPE,
                color=MARKER_COLOR if same_color_bool else None,
                s=MARKER_SIZE,
                label='Mean' if i == avg_start else f'{y_labels[i]}',
                zorder=2
            )
        if connect_points == 'y':
            plt.plot(
                    x,
                    y_data[:,i] if not avg_all else y_data.squeeze(),
                    color=SPLINE_COLOR if same_color_bool else None,
                    linewidth=TRENDLINE_WIDTH
            )


# ====SMOOTH====
def smooth():
    x_smooth = np.linspace(
        x.min(),
        x.max(),
        10000
    )
    for i in range(0,y_data.shape[1]):
        spline = make_interp_spline(
            x,
            y_data[:, i],
            k=3
        )
        y_smooth = spline(x_smooth)
        plt.plot(
            x_smooth,
            y_smooth,
            color=SPLINE_COLOR if same_color_bool else None,
            linewidth=SPLINE_WIDTH,
            label='Mean' if i == avg_start else f'{y_labels[i]}'
        )
        
# ====HEATMAP====
def heatmap():
    if y_data.shape[1] != 2:
        print("Error: wrong input data structure")
    df = pd.DataFrame({
        'x': x,
        'y': y_data[:, 0],
        'z': y_data[:, 1]
    })
    heat_data = df.pivot(
        index='y',
        columns='x',
        values='z'
    )
    ifprint("Invert y-axis? (y/n):")
    invert_y = getvalue(str, config['invert_y'])
    ifprint("Invert x-axis? (y/n):")
    invert_x = getvalue(str, config['invert_x'])
    ifprint("Reverse color mapping? (y/n):")
    reverse_cmap = getvalue(str, config['reverse_cmap'])
    ifprint("Custom tick labels? (y/n):")
    custom_hm_ticks = getvalue(str, config['custom_hm_ticks'])
    if custom_hm_ticks == 'y':
        ifprint("Number of x values per tick:")
        x_hm_ticks = getvalue(int, config['x_hm_ticks'])
        ifprint("Number of y values per tick:")
        y_hm_ticks = getvalue(int, config['y_hm_ticks'])
    fig, ax = plt.subplots()
    ax = sns.heatmap(
        heat_data,
        cmap=HEATMAP_COLOR + '_r' if reverse_cmap else HEATMAP_COLOR,
        vmin=cbar_min if cbar_bounds == 'y' else None,
        vmax=cbar_max if cbar_bounds == 'y' else None,
        xticklabels=x_hm_ticks if custom_hm_ticks == 'y' else 1,
        yticklabels=y_hm_ticks if custom_hm_ticks == 'y' else 1
    )
    if invert_y == 'y':
        ax.invert_yaxis()
    if invert_x == 'y':
        ax.invert_xaxis()
    ax.set(xlabel=xlabel, ylabel=ylabel)
    cbar = ax.collections[0].colorbar
    cbar.set_label(cbar_label)

# =========PLOTTING========

if plot_type == 1:
    scatter()
elif plot_type == 2:
    smooth()
elif plot_type == 3:
    heatmap()

plt.xlabel(xlabel)
plt.ylabel(ylabel)
if legend == 'y' and plot_type in [1, 2]:
    plt.legend()


# ===========SAVING===========

plt.tight_layout()
#figure_name = input("Figure file name ('example.png'): ")
figure_name = "output.png"
plt.savefig(figure_name, transparent=True, dpi=300)

save = False
ifprint("Save config? (y/n)")
if not use_toml:
    save = input() == 'y'

if save:
    runtime_vars = {k: globals()[k] for k in config.keys()}
    for k, v in runtime_vars.items():
        config[k] = v
    with open(config_path, 'w') as f:
        toml.dump(config, f)


plt.rcParams["svg.fonttype"] = "none"
plt.savefig("output.svg", bbox_inches="tight", transparent=True)
