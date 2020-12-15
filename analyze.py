from os import path
import feedparser
import pandas as pd
import datetime

filename = "last.txt"
date = datetime.datetime.now().strftime("%Y-%m-%d")
project_url = "github.com"


def format_perc(fl):
    return f"{int(round(fl * 100,0))}%"


if __name__ == "__main__":
    RiskyOrNot = feedparser.parse("https://riskyornot.libsyn.com/rss")
    if path.exists(filename):
        with open(filename, "r") as f:
            last_analyzed = f.read()
    else:
        last_analyzed = None

    episodes = list()
    for entry in RiskyOrNot.entries:
        r = entry["summary"].find("☣️")
        nr = entry["summary"].find("👍🏼")
        if r == -1 and nr == -1:
            continue
        elif r == -1:
            don = "👍🏼"
            ben = "👍🏼"
        elif nr == -1:
            don = "☣️"
            ben = "☣️"
        elif nr < r:
            don = "👍🏼"
            ben = "☣️"
        elif r > nr:
            ben = "👍🏼"
            don = "☣️"
        else:
            continue
        episodes.append(
            {
                "title": entry["title"],
                "id": entry["id"],
                "link": entry["link"],
                "dr. don": don,
                "prof. ben": ben,
            }
        )
    df = pd.DataFrame(episodes)
    df = df.set_index("id")

    diff = df[df["dr. don"] != df["prof. ben"]]
    nr = df[(df["dr. don"] == "👍🏼") & (df["prof. ben"] == "👍🏼")]
    r = df[(df["dr. don"] == "☣️") & (df["prof. ben"] == "☣️")]
    nr_perc = format_perc(len(nr) / len(df))
    r_perc = format_perc(len(r) / len(df))
    diff_perc = format_perc(len(diff) / len(df))
    don_nr = len([res for res in list(diff["dr. don"]) if res == "👍🏼"])
    ben_nr = len([res for res in list(diff["prof. ben"]) if res == "👍🏼"])

    if don_nr > ben_nr:
        risk_averse = "Prof. Ben is more risk averse than Dr. Don."
    elif ben_nr < don_nr:
        risk_averse = "Dr. Don is more risk averse than Prof. Ben."
    else:
        risk_averse = "Dr. Don and Prof. Ben are equally risk averse."
    if last_analyzed:
        new = df.loc[:last_analyzed]
    else:
        new = df
    new_diff = new[new["dr. don"] != new["prof. ben"]].to_dict("records")
    diff_str = "\n\t".join(
        [f"{record['title']} ({record['link']})" for record in new_diff]
    )

    tweet_one = f"Risky or Not numbers update for @bugcounter & @benjaminchapman {nr_perc} of the time you agreed it was not risky 👍🏼, {r_perc} of the time you agreed that it was risky ☣️. The remaining {diff_perc} of the time you disagreed. 1/4\n\n"
    tweet_two = f"When you disagreed, Dr. Don said not risky 👍🏼 {don_nr} times, and Prof. Ben said not risky 👍🏼 {ben_nr} times. The data clearly shows that {risk_averse} 2/4\n\n"
    if len(new_diff) > 0:
        tweet_three = f"Between Dr. Don and Prof. Ben disagreed on recent episodes:\n\t{diff_str}\n 3/4\n\n"
    else:
        tweet_three = f"Dr. Don and Prof Ben did not disagree on any recent episodes."

    with open(f"{date}.txt", "w") as f:
        f.write(tweet_one)
        f.write(tweet_two)
        f.write(tweet_three)
        f.write(f"The code for this analysis is available at {project_url} 4/4")

    with open(filename, "w") as f:
        f.write(RiskyOrNot.entries[0]["id"])
