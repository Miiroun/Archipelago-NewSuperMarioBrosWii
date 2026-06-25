import collections
import typing
from numbers import Number

import numpy as np
import yaml
import json
#import scipy


game_name_cap = "NSMBW"

meta_file = "fuzz_output/report.json"
option_yaml = lambda num, error: f"fuzz_output/{error}/{'multi'}/{num}/{num}-0.yaml"

# load yamls
with open(meta_file, "r") as f:
    meta_text = json.load(f)

options = collections.defaultdict(list)
prossess_error_seperate = False


def prossess_options(options):
    # this removes one off errors, needs threshold to do data an

    print(failure_type)

    options_counter = []
    skipp_options = [] #"death_link_group"
    for option in options:
        if option in skipp_options:
            continue
        if isinstance(options[option][0], set | list | dict):
            options[option] = list(map(frozenset, options[option]))


        # if only 1 option chosen no need to analys
        option_counter = collections.Counter(options[option])

        # this removes options which doesnt change
        if len(option_counter.most_common()) <= 1:
            print(f"all failures included {option} set to {options[option][0]}")

        # this calculates for toggle options
        if len(option_counter.most_common()) <= 10:
            # this only makes sense for bool options
            #if len(option_counter.most_common()) == 2:
            comon = option_counter.most_common()
            most_com_num = comon[0][1]
            least_com_num = comon[-1][1]
            percent_diff = abs(most_com_num - least_com_num) / (most_com_num + least_com_num)
            if  percent_diff < 0.2 :
                pass
                continue

            #print(option)
            #print(option_counter)
            #print(f"Percent Diff: {percent_diff : %}")
            to_print = f"""
                    {option}
                    Percent Diff: {percent_diff: %}
                    option_counter: {option_counter}
                    """
            options_counter.append([option, percent_diff, option_counter, to_print])
        elif isinstance(options[option], Number): #this runs for range options
            avr = np.average(options[option])
            std = np.std(options[option])


            percent_diff = avr/std
            to_print = f"""
                    {option}
                    Percent Diff: {percent_diff: %}
                    mean {avr}
                    standard_deviatin: {std}
                    option_counter: {option_counter.most_common(5)}
                    """
            #                       name,   sort_key,   text
            options_counter.append([option, percent_diff, to_print])
        else:
            to_print = f"""
                    {option}
                    option_counter: {option_counter.most_common()}
                    """
            options_counter.append([option, 0, to_print])


    options_counter.sort(key=lambda x: x[1], reverse=True)

    print("--------------------------------------------------------")
    for obj in options_counter:
        print(obj[2])
        print("--------------------------------------------------------")


    print("============================================================================")


# count each option




print("============================================================================")
for failure_type in meta_text["errors"]['multi']:
    if prossess_error_seperate:
        options = collections.defaultdict(list)

    for yam_num in meta_text["errors"]['multi'][failure_type]:
        with open(option_yaml(yam_num, "timeout" if failure_type == "<class 'TimeoutError'>" else "error"), "r") as f:
            option_text = yaml.safe_load(f)
        for option in option_text[game_name_cap]:
            options[option].append(option_text[game_name_cap][option])

    if len(options["local_items"]) <= 1 and (not prossess_error_seperate):
        print(f"failure_type {failure_type} skipped because not enough data")
        continue

    if prossess_error_seperate:
        prossess_options(options)
if not prossess_error_seperate:
    prossess_options(options)



# print most freq: as a persentage