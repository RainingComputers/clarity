from matplotlib.figure import Figure
from clarity.format import format_timespan


def plot_time_spent_map(data: dict[str, int], fig: Figure) -> None:
    activities = list(data.keys())
    seconds_spent = list(data.values())
    formatted_times = [format_timespan(sec) for sec in seconds_spent]

    # create the bar chart on the provided figure
    ax = fig.add_subplot(111)
    bars = ax.bar(activities, seconds_spent, color="skyblue")

    # add text labels on bars
    for bar, time in zip(bars, formatted_times):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            time,
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # set labels for x axis
    ax.set_xticks(activities)
    ax.set_xticklabels(activities, rotation=45, ha="right")

    # hide the y-axis
    ax.yaxis.set_visible(False)
