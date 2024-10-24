import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

DPFS = ['1dpf', '3dpf', '5dpf', '7dpf', '9dpf', '11dpf', 'night']
run = 'All'
experiment = 'Normal_behaviour'

BEHAVIOR_COLORS = {
            #'mom visit': '#0072b2',
            'fanning': '#a9a9a9',
            'mouthing': '#a9a9a9',
            #'Gulping': '#a9a9a9',
            }


if __name__ == '__main__':
    
    # we aim to generate 1 plot per behavior
    for behavior in BEHAVIOR_COLORS.keys():

        mean_normalized_behavior_durations = []
        dpf_mom_means = []

        for dpf in DPFS:

           # read data
            df = pd.read_csv('../data/{}/{}_{}_mother_agg.csv'.format(experiment,run,dpf))
            # filter by behavior
            df_behavior = df[df['Behavior'] == behavior]
            normalized_behavior_durations = []
            for mom in np.unique(df['Subject']):
                # filter by subject
                df_subject = df[df['Subject'] == mom]
                # get duration of subject engaging in current behavior
                behaviour_duration = df_subject[df_subject['Behavior'] == behavior]['Duration (s)'].sum()
                # get total 'visible' duration of subject
                total_duration_analysed = 990
                # normalize behavior duration by total visible duration
                normalized_behavior_duration = behaviour_duration / total_duration_analysed
                # keep track of normalized duration in list
                normalized_behavior_durations.append(normalized_behavior_duration)

            # calculate mean normalized behavior duration
            mean_normalized_behavior_duration = sum(normalized_behavior_durations)/len(normalized_behavior_durations)
            mean_normalized_behavior_durations.append(mean_normalized_behavior_duration)
            dpf_mom_means.append(normalized_behavior_durations)
            print(behavior, mean_normalized_behavior_duration)

        # plot bars
        plt.bar(DPFS, mean_normalized_behavior_durations, capsize=5, fill=True, color=BEHAVIOR_COLORS[behavior], edgecolor=None, zorder=1)
        for dpf, baby_means in zip(DPFS, dpf_mom_means):
            if len(baby_means) == 0:
                continue
            for baby_mean in baby_means:
                # plot dots on top of bars
                plt.scatter([dpf], [baby_mean], facecolors='none', edgecolors='black', s=20, zorder=2)
    
        filename = '../plots/{}_{}_mom_CS.pdf'.format(run, behavior)    
        plt.xlabel('days post-fertilization')
        plt.ylabel('mean fraction of time spent')
        plt.title(behavior)
        plt.gca().set_xticks(DPFS)
        plt.gca().set_xticklabels(DPFS)
        plt.savefig(filename)
        plt.show()