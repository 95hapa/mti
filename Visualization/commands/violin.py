"""
Violin plot of organisms in each sample
"""


import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import itertools

from .utils import parse_sample_list, pivot_on_sample_and_name, set_common_ancestor, unique_filename


def run(options):
    # Get the data
    # TODO ensure there isn't a "+"
    samples = parse_sample_list(options['<sample_group_string>'])
    if options['--filter']:
        samples = set_common_ancestor(
                samples, options['--filter'])

    # Draw the plot
    violinPlot = sb.violinplot(
            x='rel_abund', 
            y='name', 
            data=samples,
            orient='h')

    violinPlot.get_figure().savefig('outputs/'+unique_filename()+'.png', bbox_inches='tight')
