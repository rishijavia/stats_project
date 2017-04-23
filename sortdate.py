import json
import numpy as n
from pprint import pprint
from datetime import datetime
from dateutil import tz
import statistics as stat

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
    else:
        hour_dict = {}
        hour_dict["hour"] = data["hour"]
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

pprint(hourly_mean_download)
pprint(hourly_mean_upload)
