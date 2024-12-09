#!/usr/bin/env python3
# Copyright 2023 Marcus Müller
# SPDX-License-Identifier: GPL-3.0-or-later
import requests
import json

URL_PREFIX = "https://pretalx.fosdem.org"
EVENT = "fosdem-2025"
SUBMISSIONS = f"{URL_PREFIX}/api/events/{EVENT}/submissions"
REVIEWS = f"{URL_PREFIX}/api/events/{EVENT}/submissions"

def submission_in_track(submission, track):
    if (not track):
        return True

    t = submission.get("track", {"en": None})
    if not isinstance(t, str):
        t = t["en"]

    return track in t

def go(track: str = "", auth_token: str = "") -> None:
    session = requests.Session()
    if auth_token:
        session.headers.update({"Authorization": f"Token {auth_token}"})

    result = session.get(SUBMISSIONS)
    # print(result.json())
    submissions = [submission for submission in result.json()["results"]
                   if submission_in_track(submission, track)]
    next_URL = result.json().get("next", None)
    while next_URL:
        # print("Next one")
        result = session.get(next_URL)
        new = [submission for submission in result.json()["results"]
               if submission_in_track(submission, track)]
        submissions += new
        next_URL = result.json().get("next", None)

    print(json.dumps(submissions, indent=True))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth-token", "-a", type=str,
                        default="", help="Authentication token")
    parser.add_argument("--track", "-t", type=str,
                        default="", help="filter by track")
    options = parser.parse_args()
    go(options.track, options.auth_token)
