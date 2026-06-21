import collections
import typing

import yaml
import json
import scipy

game_name = "nsmbw"
game_name_cap = "NSMBW"

meta_file = "fuzz_output/report.json"
option_yaml = lambda num, error: f"fuzz_output/{error}/{game_name}/{num}/{num}-0.yaml"

# load yamls
with open(meta_file, "r") as f:
    meta_text = json.load(f)

print("============================================================================")
for failure_type in meta_text["errors"][game_name]:
    options = collections.defaultdict(list)
    for yam_num in meta_text["errors"][game_name][failure_type]:
        with open(option_yaml(yam_num, "timeout" if failure_type == "<class 'TimeoutError'>" else "error"), "r") as f:
            option_text = yaml.safe_load(f)
        for option in option_text[game_name_cap]:
            options[option].append(option_text[game_name_cap][option])

    # this removes one off errors, needs threshold to do data an
    if len(options["local_items"]) <= 10:
        continue
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
            continue

        # needs large sampel size for these to be useful
        if len(option_counter.most_common()) > 25:
            continue



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

        options_counter.append([option, percent_diff, option_counter])
    options_counter.sort(key=lambda x: x[1], reverse=True)

    print("--------------------------------------------------------")
    for obj in options_counter:
        print(obj[0])
        print(f"Percent Diff: {obj[1] : %}")
        print(obj[2])
        print("--------------------------------------------------------")


    print("============================================================================")


# count each option


# print most freq: as a persentage