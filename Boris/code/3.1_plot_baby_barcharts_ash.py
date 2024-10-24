import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statistics

#chose the DPFs you want in the graph:
DPFS = ['1dpf','3dpf','5dpf','7dpf','9dpf','11dpf']
run = 'both'
save_name = 'nights'

# BEHAVIOR_COLORS = {
#             'bounce': '#0072b2',
#             'laying on floor': '#42b48b',
#             'head attached': '#aaf0d2',
#             }

BEHAVIOR_COLORS = {
            'bounce': '#a9a9a9',
            'laying on floor': '#a9a9a9',
            'head attached': '#a9a9a9',
            'wriggling': '#a9a9a9',
            }

if __name__ == '__main__':

    # we aim to generate 1 plot per behavior
    for behaviour in BEHAVIOR_COLORS.keys():

        mean_normalized_behavior_durations = []
        mean_behaviour_single_durations = []
        std_behaviour_single_durations = []
        median_behaviour_single_durations = []
        min_behaviour_single_durations = []
        max_behaviour_single_durations = []
        dpf_baby_means = []
        tot_duration_stds = []

        for dpf in DPFS:

            # read data
            df = pd.read_csv('../data/{}_{}_babies_agg.csv'.format(run,dpf))
            # filter by behavior
            df_behavior = df[df['Behavior'] == behaviour]
            normalized_behavior_durations = []
            
            for baby in np.unique(df['Subject']):
                # filter by subject
                df_subject = df[df['Subject'] == baby]
                # get duration of subject engaging in current behavior
                behaviour_duration = df_subject[df_subject['Behavior'] == behaviour]['Duration (s)'].sum()
                # get total 'visible' duration of subject
                total_duration_visible = df_subject[df_subject['Behavior'].apply(lambda x: x in ['laying on floor', 'bounce', 'head attached'])]['Duration (s)'].sum()
                # normalize behavior duwrigglingration by total visible duration
                normalized_behavior_duration = behaviour_duration / total_duration_visible
                # tot_duration_std = normalized_behavior_duration
                print(f"{behaviour}: {normalized_behavior_duration:.2f}")
                # keep track of normalized duration in list
                normalized_behavior_durations.append(normalized_behavior_duration)

            
            # calculate mean normalized behavior duration
            mean_normalized_behavior_duration = sum(normalized_behavior_durations)/len(normalized_behavior_durations)
            std_deviation = statistics.stdev(normalized_behavior_durations)
            mean_normalized_behavior_durations.append(mean_normalized_behavior_duration)
            dpf_baby_means.append(normalized_behavior_durations)
            tot_duration_stds.append(std_deviation)


            # create DF for each dpf with total, mean, min and max durations
            single_behaviour_duration_ave = df_behavior[df_behavior['Behavior'] == behaviour]['Duration (s)'].mean()
            mean_behaviour_single_durations.append(single_behaviour_duration_ave)
            single_behaviour_duration_min = df_behavior[df_behavior['Behavior'] == behaviour]['Duration (s)'].min()
            min_behaviour_single_durations.append(single_behaviour_duration_min)
            single_behaviour_duration_max = df_behavior[df_behavior['Behavior'] == behaviour]['Duration (s)'].max()
            max_behaviour_single_durations.append(single_behaviour_duration_max)
            single_behaviour_duration_std = df_behavior[df_behavior['Behavior'] == behaviour]['Duration (s)'].std()
            std_behaviour_single_durations.append(single_behaviour_duration_std)
            single_behaviour_duration_median = df_behavior[df_behavior['Behavior'] == behaviour]['Duration (s)'].median()
            median_behaviour_single_durations.append(single_behaviour_duration_median)

        behavior_dict = {
            'dpf': DPFS,
            'total_duration': mean_normalized_behavior_durations,
            'std_tot_duration': tot_duration_stds,
            'mean_durations': mean_behaviour_single_durations,
            'std_durations': std_behaviour_single_durations,
            'median_durations': median_behaviour_single_durations,
            'min_durations': min_behaviour_single_durations,
            'max__durations': max_behaviour_single_durations
        }
       
        behavior_df = pd.DataFrame(behavior_dict)
        output_csv_filename = '../data/{}_{}_{}.csv'.format(run, behaviour, save_name)
        behavior_df.to_csv(output_csv_filename, index=False)

        toplot = False
        
        if toplot:
            # plot bars
            fig, ax = plt.subplots()

            # Iterate over DPFS and add jitter to scatter plot points
            for dpf, baby_means in zip(DPFS, dpf_baby_means):
                if len(baby_means) == 0:
                    continue
                # Add jitter to x-coordinates
                jittered_x = np.random.normal(loc=DPFS.index(dpf), scale=0.1, size=len(baby_means))
                # plot dots on top of bars with jittered x-coordinates
                plt.scatter(jittered_x, baby_means, facecolors='none', edgecolors='black', s=20, zorder=2, linewidths=1)

            # plot bars
            plt.bar(DPFS, mean_normalized_behavior_durations, capsize=5, fill=True, color=BEHAVIOR_COLORS[behaviour], edgecolor=None, zorder=1)

            filename = '../plots/{}_{}.pdf'.format(run, behaviour)
            plt.xlabel('days post-fertilization')
            plt.ylabel('mean normalized duration')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.ylim(0, 1.1)
            plt.title(behaviour)
            plt.gca().set_xticks(DPFS)
            plt.gca().set_xticklabels(DPFS)
            plt.savefig(filename)
            plt.show()
