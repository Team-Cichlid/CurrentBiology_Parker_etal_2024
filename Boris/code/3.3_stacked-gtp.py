import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Chose the DPFs you want in the graph:
DPFS = ['1dpf', '3dpf', '5dpf', '7dpf', '9dpf', '11dpf', 'night']
run = 'both'
save_name = 'nights'

BEHAVIOR_COLORS = {
    'laying on floor': '#42b48b',
    'head attached': '#aaf0d2',
}

if __name__ == '__main__':
    # Attached
    mean_normalized_attached_durations = []
    dpf_attached_means = []

    for dpf in DPFS:
        # Read data
        df = pd.read_csv('../data/{}_{}_babies_agg.csv'.format(run, dpf))

        normalized_attached_durations = []
        for baby in np.unique(df['Subject']):
            # Filter by subject
            df_subject = df[df['Subject'] == baby]
            # Get duration of subject engaging in current behavior
            attached_duration = df_subject[df_subject['Behavior'].isin(['laying on floor', 'head attached'])]['Duration (s)'].sum()
            # Normalize behavior duration by total visible duration
            total_duration_visible = df_subject[df_subject['Behavior'].apply(lambda x: x in ['laying on floor', 'bounce', 'head attached'])]['Duration (s)'].sum()
            normalized_attached_duration = attached_duration / total_duration_visible
            # Keep track of normalized duration in list
            normalized_attached_durations.append(normalized_attached_duration)

        # Calculate mean normalized behavior duration
        mean_normalized_attached_duration = sum(normalized_attached_durations) / len(normalized_attached_durations)
        mean_normalized_attached_durations.append(mean_normalized_attached_duration)
        dpf_attached_means.append(normalized_attached_durations)

    toplot = True

    if toplot:
        # Create a list of zeros for the same length as DPFS
        bottom_values = [0] * len(DPFS)
        
        # Create a figure and axis
        fig, ax = plt.subplots()
        
        # Plot 'laying on floor' behavior
        ax.bar(DPFS, dpf_attached_means[0], capsize=5, fill=True, color=BEHAVIOR_COLORS['laying on floor'], edgecolor=None, zorder=1, label='laying on floor')
        
        # Plot 'head attached' behavior on top of 'laying on floor'
        ax.bar(DPFS, dpf_attached_means[1], bottom=dpf_attached_means[0], capsize=5, fill=True, color=BEHAVIOR_COLORS['head attached'], edgecolor=None, zorder=1, label='head attached')
        
        # Customize the plot
        ax.set_xlabel('days post-fertilization')
        ax.set_ylabel('mean normalized duration')
        ax.set_title('Attached')
        ax.set_xticks(DPFS)
        ax.set_xticklabels(DPFS)
        ax.set_ylim(0, 1.0)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add a legend
        ax.legend()
        
        filename = '../plots/{}_attached_{}.png'.format(run, save_name)
        plt.savefig(filename)
        plt.show()