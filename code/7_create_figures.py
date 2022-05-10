import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from utils import (import_data,
                    save_figure)


def create_pie_figure(x, y, filename, figure_name, title):

    df = import_data(filename)

    fig = plt.figure(figsize=(30, 30))
    ax = fig.add_axes([0,0,1,1])
    ax.axis('equal')

    labels= df[x].to_list()
    categories = df[y].to_list()

    cmap = plt.get_cmap('coolwarm')
    colors = [cmap(i) for i in np.linspace(0, 1, 18)]

    ax.pie(
    categories,
    labels = labels,
    autopct='%.0f%%',
    textprops={'fontsize': 29},
    colors=colors,
    rotatelabels = True)

    save_figure(figure_name)

def create_donut(x, y, filename, figure_name, title):

    fig, ax = plt.subplots(figsize=(6, 15), subplot_kw=dict(aspect="equal"))
    df = import_data(filename)
    l = len(df[x].to_list())
    list_labels =[]
    for i in range(0,l):
        a = df[x].to_list()[i] + ' (' + str(df[y].to_list()[i]) + ')'
        list_labels.append(a)

    ratings = list_labels
    data = df[y].to_list()

    cmap = plt.get_cmap('coolwarm')
    colors = [cmap(i) for i in np.linspace(0, 1, 16)]

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.4), startangle=230, colors = colors)

    bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="k", lw=0.72)

    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    plt.text(0, 0, "Third-Party\nFact-checked URLs\n in the\n Condor Dataset\n(June 2021)", ha='center', va='center', fontsize=14)

    for i, p in enumerate(wedges):

        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(ratings[i], xy=(x, y), xytext=(1.3*np.sign(x), 1.3*y),
                    horizontalalignment=horizontalalignment, **kw)

    save_figure(figure_name)

def main():

    create_donut(x = 'tpfc_rating',
                      y = 'number of links',
                      filename = 'aggregate_links_condor.csv',
                      figure_name = 'donut_aggregate_links_condor',
                      title = '')


if __name__ == '__main__':
    main()
