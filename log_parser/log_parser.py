import argparse
import json
import os
import re
from collections import defaultdict


def parse_log_file(file_path):
    dict_ip = {"TOTAL": 0, "METHOD": {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0, "OPTIONS": 0}}
    dict_ip_requests = defaultdict(lambda: {"REQUESTS_COUNT": 0})
    list_ip_duration = []

    with open(file_path) as logfile:
        for line in logfile:
            method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD|OPTIONS)", line)
            ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group()
            duration = int(line.split()[-1])
            date = re.search(r"\[\d.*?\]", line)
            url = re.search(r"\"http.*?\"", line)

            dict_ip["TOTAL"] += 1

            if method is not None:
                dict_ip["METHOD"][method.group(1)] += 1
                dict_ip_requests[ip]["REQUESTS_COUNT"] += 1
                dict_t = {"IP": ip,
                          "METHOD": method.group(1),
                          "URL": "-",
                          "DATE": date.group(0).split(" ")[0].lstrip("["),
                          "DURATION": duration
                          }

                if url is not None:
                    dict_t["URL"] = url.group(0).strip("\"")

                list_ip_duration.append(dict_t)
        top3_requests_by_ip = dict(
            sorted(dict_ip_requests.items(), key=lambda x: x[1]["REQUESTS_COUNT"], reverse=True)[0:3])
        top3_requests_by_duration = sorted(list_ip_duration, key=lambda x: x["DURATION"], reverse=True)[0:3]

        result = {"Total number of requests": dict_ip["TOTAL"],
                  "Total number of requests by HTTP-methods": dict_ip["METHOD"],
                  "Top-3 requests by IP": top3_requests_by_ip,
                  "Top-3 longest requests": top3_requests_by_duration
                  }

        with open(f"{file_path}.json", "w", encoding="utf-8") as file:
            result = json.dumps(result, indent=4)
            file.write(result)
            print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process access.log')
    parser.add_argument('-l', dest='log', action='store', help='Path to logfile')
    args = parser.parse_args()

    if args.log is not None:
        if os.path.isfile(args.log):
            parse_log_file(file_path=args.log)

        elif os.path.isdir(args.log):
            for file in os.listdir(args.log):
                if file.endswith(".log"):
                    path_to_logfile = os.path.join(args.log, file)
                    parse_log_file(file_path=path_to_logfile)

        else:
            print("ERROR: Wrong path to file")
