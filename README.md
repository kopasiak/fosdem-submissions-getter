# Get Submissions and Reviews for your FOSDEM track

Usage

```shell
./getsubmissions.py -a {Auth token as in your pretalx.fosdem.org User config page} -t {substring of track name} > tracksubmissions.json
./getscores.py -a {as above} tracksubmissions.json
```

yields a `review_scores.csv`. Have fun!
