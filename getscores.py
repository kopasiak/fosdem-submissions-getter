#!/usr/bin/env python3
# Copyright 2023 Marcus Müller
# SPDX-License-Identifier: GPL-3.0-or-later
import sys
import json
import csv
import requests

URL_PREFIX = "https://pretalx.fosdem.org"
EVENT = "fosdem-2025"
SUBMISSIONS = f"{URL_PREFIX}/api/events/{EVENT}/submissions"
REVIEWS = f"{URL_PREFIX}/api/events/{EVENT}/reviews"


def go(infile, auth_token: str):
    session = requests.Session()
    if auth_token:
        session.headers.update({"Authorization": f"Token {auth_token}"})

    submissions = json.load(infile)
    review_scores = dict()
    for submission in submissions:
        sub_code = submission["code"]
        reviews_url = f"{REVIEWS}?submission__code={sub_code}"
        reviews = session.get(reviews_url).json()["results"]
        try:
            scores = {entry["user"]: entry["score"] for entry in reviews}
        except KeyError as ke:
            print(json.dumps(reviews, indent=True))
            print(ke)
            continue
        review_scores[f"{submission['title']} – {submission['speakers'][0]['name']}"] = {
            "scores": scores, "title": submission['title'], "speakers": [s["name"] for s in submission["speakers"]],
            "duration": submission["duration"]}

    reviewers = set()

    for scores in [rs["scores"] for rs in review_scores.values()]:
        reviewers |= set(scores.keys())

    reviewers = list(sorted(reviewers))

    with open("review_scores.csv", "w", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=["Talk Title", "Duration", "Speakers"] + reviewers + ["Average"], restval="")
        writer.writeheader()
        for id, rs in review_scores.items():
            scores = rs["scores"]
            rowdict = {"Talk Title": rs["title"], "Speakers": rs["speakers"], "Duration": rs["duration"]}
            sumscore = 0
            counter = 0
            for user, score in scores.items():
                try:
                    score = float(score)
                    rowdict[user] = score
                    counter += 1
                    sumscore += score
                except TypeError:
                    pass
            if counter:
                rowdict["Average"] = sumscore / counter
            writer.writerow(rowdict)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth-token", "-a", type=str,
                        default="", help="Authentication token")
    parser.add_argument(
        "FILE", type=argparse.FileType("r", encoding="utf-8"))
    options = parser.parse_args()
    go(options.FILE, options.auth_token)
