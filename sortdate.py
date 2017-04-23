import json
import numpy as n
from pprint import pprint
from datetime import datetime
from dateutil import tz
import statistics as stat
import math

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Los_Angeles')

with open('holmes.json') as json_data:
    ml_data = json.load(json_data)

# Remove outliers collected using ethernet
# i = 0
# for data in ml_data:
#     date = data["timestamp"]
#     utc_frag, frag = date.split('.')
#     utc = datetime.strptime(utc_frag, "%Y-%m-%dT%H:%M:%S")
#     if utc.day >= 19:
#         ml_data.pop(i)
#     i += 1
#
# # Output the updated file with pretty JSON
# open("updated-holmes.json", "w").write(
#     json.dumps(ml_data, sort_keys=True, indent=4, separators=(',', ': '))
# )

miller_data = []

for data in ml_data:
    date = data["timestamp"]
    utc_frag, frag = date.split('.')
    utc = datetime.strptime(utc_frag, "%Y-%m-%dT%H:%M:%S")
    utc = utc.replace(tzinfo=from_zone)
    pst = utc.astimezone(to_zone)
    miller_data.append({"timestamp": pst, "hour": pst.hour, "upload": data["upload"], "download": data["download"]})

miller_hourly_data = [{} for i in range(24)]

for data in miller_data:
    if not len(miller_hourly_data[data["hour"]]) == 0:
        miller_hourly_data[data["hour"]]["download"].append(data["download"])
        miller_hourly_data[data["hour"]]["upload"].append(data["upload"])
        miller_hourly_data[data["hour"]]["count"] += 1
    else:
        hour_dict = {}
        hour_dict["hour"] = data["hour"]
        hour_dict["count"] = 1
        hour_dict["download"] = [data["download"]]
        hour_dict["upload"] = [data["upload"]]
        miller_hourly_data[data["hour"]] = hour_dict

for data in miller_hourly_data:
    data["mean_download"] = stat.mean(data["download"])
    data["mean_upload"] = stat.mean(data["upload"])
    data["sample_sd_download"] = stat.stdev(data["download"])
    data["sample_sd_upload"] = stat.stdev(data["upload"])
    data.pop('download', None)
    data.pop('upload', None)

hourly_mean_download = [data["mean_download"] for data in miller_hourly_data]
hourly_mean_upload = [data["mean_upload"] for data in miller_hourly_data]

n_list = []
mean_list_download = []
s_list_download = []
mean_list_upload = []
s_list_upload = []
for data in miller_hourly_data:
    n_list.append(data["count"])
    mean_list_download.append(data["mean_download"])
    mean_list_upload.append(data["mean_upload"])
    s_list_download.append(data["sample_sd_download"])
    s_list_upload.append(data["sample_sd_upload"])


# pprint(hourly_mean_download)
# pprint(hourly_mean_upload)

# Andrea's functions:

def ss_between(n, mean_list, mean):
    ss = 0
    for i in range(len(n)):
        ss += (n[i] * (mean_list[i] - mean)*(mean_list[i] - mean))
    return ss
def ss_within(n, s):
    ss = 0
    for i in range(len(n)):
        ss += (n[i] - 1) * math.pow(s[i], 2)
    return ss

def weighted_avg(n, means):
    avg = 0
    for i in range(len(n)):
        avg += (n[i]/sum(n)) * means[i]
    return avg
def anova(n_list, mean_list, s_list):
    n_star = sum(n_list)
    overall_avg = weighted_avg(n_list, mean_list)
    df_between = len(n_list) - 1
    df_within = n_star - len(n_list)
    df_total = n_star - 1
    ss_b = ss_between(n_list, mean_list, overall_avg)
    ss_w = ss_within(n_list, s_list)
    ms_between = ss_b / df_between
    ms_within = ss_w / df_within
    f = ms_between / ms_within
    print "1 - pf(" + str(f) + "," + str(df_between) + "," + str(df_total) + ")"
    return f

anova(n_list, mean_list_download, s_list_upload)
anova(n_list, mean_list_upload, s_list_upload)
