import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

DPFS = ['9dpf']
runs = ['both','CS']  # Add the name of the second run

BEHAVIOR_COLORS = {
    'fanning': '#a9a9a9',
    'mouthing': '#a9a9a9',
}

if __name__ == '__main__':
    
    for behavior in BEHAVIOR_COLORS.keys():

        mean_normalized_behavior_durations_all = []

        for run in runs:
            dpf_mom_means = []

            for dpf in DPFS:

                df = pd.read_csv('../data/{}_{}_mom_agg.csv'.format(run, dpf))
                df_behavior = df[df['Behavior'] == behavior]

                normalized_behavior_durations = []
                for mom in np.unique(df['Subject']):
                    df_subject = df[df['Subject'] == mom]
                    behaviour_duration = df_subject[df_subject['Behavior'] == behavior]['Duration (s)'].sum()
                    total_duration_analysed = 990
                    normalized_behavior_duration = behaviour_duration / total_duration_analysed
                    normalized_behavior_durations.append(normalized_behavior_duration)

                mean_normalized_behavior_duration = sum(normalized_behavior_durations) / len(normalized_behavior_durations)
                dpf_mom_means.append(normalized_behavior_durations)
                # print(behavior, mean_normalized_behavior_duration)
            print(behavior, dpf_mom_means)

            mean_normalized_behavior_durations_all.append(mean_normalized_behavior_duration)

        # plot bars for both datasets
        width = 0.35  # the width of the bars
        ind = np.arange(len(DPFS))

        fig, ax = plt.subplots()
        bars = []

        for j, run in enumerate(runs):
            bars.append(ax.bar(ind + width * j, mean_normalized_behavior_durations_all[j], width, label=run))

            # Add individual data points for each dataset
            for i, dpf_means in enumerate(dpf_mom_means):
                if len(dpf_means) == 0:
                    continue
                x_position = ind[i] + width * j
                if isinstance(dpf_means[i], list):
                    for baby_mean in dpf_means[i]:
                        plt.scatter([x_position], [baby_mean], facecolors='none', edgecolors='black', s=20, zorder=2)
                else:
                    plt.scatter([x_position], [dpf_means[i]], facecolors='none', edgecolors='black', s=20, zorder=2)

        # Add some text for labels, title, and custom x-axis tick labels, etc.
        ax.set_xlabel('days post-fertilization')
        ax.set_ylabel('mean fraction of time spent')
        ax.set_title(behavior)
        ax.set_xticks(ind + width / 2 * (len(runs) - 1))
        ax.set_xticklabels(DPFS)
        ax.legend()

        # Attach a text label above each bar in *rects*, displaying its height.
        for bar_set in bars:
            for rect in bar_set:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        plt.savefig('../plots/{}_{}_mom_CS.pdf'.format('_'.join(runs), behavior))
        plt.show()
