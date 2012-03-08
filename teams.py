import time
import random

def team_hash(members, teamsize=5):
    today = int(time.strftime("%y%m%d"))
    l_members = list(sorted(members))
    r = random.Random()
    r.seed(today)
    obscure = [(r.random(), m) for m in l_members]
    obscure.sort()
    teams = []
    team = []
    for i, (_, member) in enumerate(obscure):
        if len(team) == teamsize:
            team.sort()
            teams.append(team)
            team = []
        team.append(member)
    if team:
        team.sort()
        teams.append(team)
    return teams

if __name__ == "__main__":
    import sys
    print team_hash(sys.argv[1:])
