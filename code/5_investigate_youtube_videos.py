import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from utils import (import_data,
                    save_data,
                    save_figure)

pd.options.display.max_colwidth = 180
pd.options.mode.chained_assignment = None

def get_share_of_available_videos ():

    df = import_data('condor_EU_false_links_report_2022_04_04.csv')
    df = df[df['parent_domain'] == 'youtube.com']
    l = len(df)
    print('Number of yt links', l)

    df = df[df['status'] == 200]
    l_active = len(df)
    print('Number of active yt links', l_active)

    df_yt = import_data('videos_youtube_condor_EU_false_links_active_2022-04-04.csv')
    df_yt['video_id'] = df_yt['video_id'].fillna('not found, suspended or deleted')
    l_available= len(df_yt[~df_yt['video_id'].isin(['not found, suspended or deleted'])])

    print('Number of available yt links', l_available)

    df_m = import_data('messages_videos_youtube_condor_EU_false_links_active_2022_04_04.csv')
    df_m = df_m.replace('\n', ' ', regex = True)
    df_m = df_m.rename(columns = {'suspended_message': 'not_found_message',
                                'not_found_message': 'suspended_message'})

    print(df_m.groupby(['suspended_message'], as_index = False).size().sort_values(by = 'size', ascending = False))
    print(df_m.groupby(['not_found_message'], as_index = False).size().sort_values(by = 'size', ascending = False))
    print(df_m.groupby(['information_panel'], as_index = False).size().sort_values(by = 'size', ascending = False))

    df_not_found = df_m.groupby(['not_found_message'], as_index = False).size().sort_values(by = 'size', ascending = False)
    df_not_found_max_reason = df_not_found.not_found_message[df_not_found['size'] == df_not_found['size'].max()].iloc[0]
    df_not_found_max = df_not_found['size'].max()
    print('most common reason for unavailable videos \"', df_not_found_max_reason, '\" (repeated for exactly ', df_not_found_max, ' videos)' )

    df_removed = df_m.groupby(['suspended_message'], as_index = False).size().sort_values(by = 'size', ascending = False)
    df_removed_max_reason = df_removed.suspended_message[df_removed['size'] ==df_removed['size'].max()].iloc[0]
    df_removed_max = df_removed['size'].max()
    print('most common reason for suspended videos \"', df_removed_max_reason, '\" (repeated for exactly ', df_removed_max, ' videos)', '\n' )

    list_unavailable = ['Cette vidéo n\'est plus disponible ACCÉDER À L\'ACCUEIL',
                        'Vidéo privée',
                        'Vidéo non disponible',
                        'Vidéo non disponible Cette vidéo n\'est plus disponible, car le compte YouTube associé a été clôturé. ACCÉDER À L\'ACCUEIL',
                        'Vidéo non disponible Cette vidéo n\'est plus disponible en raison d\'une réclamation pour atteinte aux droits d\'auteur envoyée par Norddeutscher Rundfunk ACCÉDER À L\'ACCUEIL'
                        ]

    list_removed = ['Cette vidéo a été supprimée, car elle ne respectait pas le règlement de la communauté YouTube',
                    'Cette vidéo a été supprimée, car elle ne respectait pas les conditions d\'utilisation de YouTube',
                    'Cette vidéo a été supprimée, car elle ne respectait pas les règles de YouTube concernant le contenu violent ou explicite',
                    'Cette vidéo a été supprimée, car elle ne respectait pas les règles de YouTube concernant la nudité et le contenu à caractère sexuel',
                    'Vidéo non disponible Cette vidéo a été supprimée par l\'utilisateur qui l\'a mise en ligne ACCÉDER À L\'ACCUEIL',
                    'Vidéo non disponible Le compte YouTube associé à cette vidéo a été clôturé, car nous avons reçu, à plusieurs reprises, des notifications de tiers pour atteinte aux droits d\'auteur'
                    ]

    list_deactivated_comments = ['Les commentaires sont désactivés. En savoir plus']

    list_info_panel = ['COVID-19 Gouvernement.fr: dernières informations sur le Coronavirus. EN SAVOIR PLUS Plus d\'infos sur Google',
                        'Vaccin contre la COVID-19 Consultez les dernières informations sur le site du gouvernement français. EN SAVOIR PLUS Plus d\'infos sur Google']

    dct_reasons = {}
    dct_reasons['unavailable'] = list_unavailable
    dct_reasons['removed'] = list_removed
    dct_reasons['panel'] = list_info_panel
    dct_reasons['deactivated_comments'] = list_deactivated_comments

    count_removed = len(df_m[df_m['suspended_message'].isin(list_removed)]) + len(df_m[df_m['not_found_message'].isin(list_removed)])
    count_unavailable = len(df_m[df_m['suspended_message'].isin(list_unavailable)]) + len(df_m[df_m['not_found_message'].isin(list_unavailable)])
    count_active = df_m['title'].count()
    count_info_panel = df_m['information_panel'].count()

    group_size = [count_removed + count_unavailable, count_active]
    print('groups: \n [inactive, active] \n ', group_size, '\n')

    subgroup_size = [count_removed,
                    count_unavailable,
                    count_active - count_info_panel,
                    count_info_panel]

    print('subgroups: \n [count_unavailable, count_removed, count_active - count_info_panel ,count_info_panel ] \n', subgroup_size, '\n')

    subsubgroup_size = []

    for i in range(0,len(dct_reasons['unavailable'])):

        a  = len(df_m[df_m['not_found_message'].isin([dct_reasons['unavailable'][i]])])
        b  = len(df_m[df_m['suspended_message'].isin([dct_reasons['unavailable'][i]])])
        c = a + b
        subsubgroup_size.append(c)

    for i in range(0,len(dct_reasons['removed'])):

        a  = len(df_m[df_m['not_found_message'].isin([dct_reasons['removed'][i]])])
        b  = len(df_m[df_m['suspended_message'].isin([dct_reasons['removed'][i]])])
        c = a + b
        subsubgroup_size.append(c)

    percent_not_found  = round(100*(df_not_found_max/count_unavailable))
    print(percent_not_found,
        '% of the videos not available, are not available for the following reason:',
        df_not_found_max_reason, '\n')

    percent_removed  = round(100*(df_removed_max/count_removed))
    print(percent_removed,
        '% of the videos removed, are removed for the following reason:',
        df_removed_max_reason, '\n')

    return group_size, subgroup_size, subsubgroup_size

def plot_nested_pie():

    group_size, subgroup_size, subsubgroup_size = get_share_of_available_videos ()

    group_names=['217 Inactive\nVideos',
                '76 Active\nVideos']

    subgroup_names=['44 Videos\nRemoved\n\n(86% violating\ncommunity\nguidelines)',
                    '173 Videos\nUnavailable\n\n(53% with no\nspecified\nreason)',
                    '56 Videos\nWithout\nInfo Panel\n\n(12% with\ndeactivated\ncomments)',
                    '20 Videos\nWith\nInfo Panel']

    a, b =[plt.cm.Reds, plt.cm.Greens]
    fig, ax = plt.subplots(figsize=(11, 11))
    ax.axis('equal')

    mypie, _ = ax.pie(group_size,
                        radius=1.3,
                        labels=group_names,
                        #labeldistance=0.72,
                        textprops={'fontsize': 13, 'color': 'black', 'fontweight': 'bold'},
                        colors=[a(0.7), b(0.7)])

    plt.setp( mypie, width=0.1, edgecolor='white')

    mypie2, _ = ax.pie(subgroup_size,
                        radius=1.3-0.1,
                        labels=subgroup_names,
                        labeldistance=0.5,
                        textprops={'fontsize': 15, 'color': 'white', 'fontweight': 'bold', 'va': 'center'},
                        colors=[a(0.5), a(0.4), b(0.5), b(0.4)])

    plt.setp(mypie2, width=0.8, edgecolor='white')
    plt.margins(0,0)

    handles, labels = ax.get_legend_handles_labels()

    ax.set_title('Youtube Videos fact checked as false in the Condor Dataset', pad = 25, fontsize = 20)
    save_figure('yt_pie')

if __name__ == '__main__':
    #get_share_of_available_videos ()
    plot_nested_pie()
