from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math

from analysis.scurve_fit import Analysis

std_linewidth = 1

plot_fits = True

filename = "dig_inj_scan_20230912-142755"

x_highres = np.arange(1, 1.6, 0.002)

df = pd.read_csv('./log/' + filename + '.log', sep=',', skiprows=9)


n_plots = 35
plot_cols = 5
plot_rows = math.ceil(n_plots / plot_cols)

fig, axes = plt.subplots(plot_rows, plot_cols, figsize=(16, 12))
plot_cnt = 0


def find_closest_values(s, x):
    idx = (np.abs(s - x)).argmin()
    print(s[idx])


for col in df.scan_col.drop_duplicates(keep='first'):
    for row in df[df['scan_col'] == col].scan_row.drop_duplicates(keep='first'):
        df_y = df.loc[(df['scan_col'] == col) & (df['scan_row'] == row)].vth.value_counts().sort_index()
        df_y = pd.DataFrame({'x': df_y.index, 'y': df_y.values})

        idx = df_y.y.sub(50).abs().idxmin()
        x_0 = df_y.iloc[idx]['x']
        print(f'Closest value: {x_0} Median: {np.median(df_y.x)}')

        # df_y.loc[df_y['y'] > 200, 'y'] = 200
        df_y.y = df_y.y / 2

        print(df_y)
        if 1.6 not in df_y.x.values:
            df_y.loc[len(df_y)] = [1.6, 0]

        ax_x = int(plot_cnt / plot_cols)
        ax_y = plot_cnt % plot_cols

        axes[ax_x][ax_y].plot(df_y.x, df_y.y, 's')
        axes[ax_x][ax_y].set_xlim(1, 1.6)
        axes[ax_x][ax_y].set_title(f'({col},{row})')

        if plot_fits:
            try:
                # axes[ax_x][ax_y].plot(x_highres, Analysis.scurve_fit(df_y.x, df_y.y, x_highres, False, x_0 = x_0),
                #                       linewidth=std_linewidth, color='Red')
                axes[ax_x][ax_y].plot(x_highres,
                                      Analysis.scurve_fit(df_y.x, df_y.y, x_highres, True),
                                      linewidth=std_linewidth)

            except (ValueError, RuntimeError):
                print(f"Fit failed for Pixel {col},{row}")
                # axes[ax_x][ax_y].plot(x_highres, Analysis.scurve_fit(df_y.x, df_y.y, x_highres, False, True),
                #                       linewidth=std_linewidth)
                axes[ax_x][ax_y].get_lines()[0].set_color("red")

        plot_cnt += 1

fig.tight_layout()
plt.show()
