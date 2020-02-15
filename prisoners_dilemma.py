"""
An iterated prisoner's dilemma written by Arthur Goldman
for Southwest High School in Minneapolis's Computer Science class 2016-2017
arthur@goldman-tribe.org
agol1801@mpsedu.org
"""

import GLOBALS
from teamclass import Team
from pandas import DataFrame
import random
from typing import List

default_module_names = ['examplemodules/example0.py',
                        'examplemodules/example1.py',
                        'examplemodules/example2.py',
                        'examplemodules/example3.py']


def sum_list(list_to_sum: List[int]):
    """
    I feel like this function is pretty intuitive
    given a list of numbers, it adds them together
    """
    count = 0
    for value in list_to_sum:
        count += value
    return count


def load_modules(module_names: List[str]):
    """
    Given a list of strings with paths to modules,
    load them. Return a list of teams, which are
    instances of Team from teamclass.py
    """
    teams = []
    for team_number, module_name in enumerate(module_names):
        teams.append(Team(module_name, team_number))
    return teams


def play_tournament(modules: List[Team]):
    scores = [[False for _ in range(len(modules))] for _ in range(len(modules))]  # an n*n list for scores
    # each player's scores are in scores[that_player][opponent]
    moves = [[False for _ in range(len(modules))] for _ in range(len(modules))]  # an n*n list for moves
    for first_team_index in range(len(modules)):
        for second_team_index in range(first_team_index + 1):
            # each player plays against all the players before them
            if first_team_index == second_team_index:
                # if you're playing yourself, score 0 and make no moves
                scores[first_team_index][first_team_index] = 0
                moves[first_team_index][first_team_index] = ''
            else:
                # play against the opponent, log scores in the lists
                player_1 = modules[first_team_index]
                player_2 = modules[second_team_index]
                player_1_score, player_2_score, player_1_moves, player_2_moves = play_round(player_1, player_2)
                scores[first_team_index][second_team_index] = player_1_score
                scores[second_team_index][first_team_index] = player_2_score
                moves[first_team_index][second_team_index] = player_1_moves
                moves[second_team_index][first_team_index] = player_2_moves
    return scores, moves


def play_round(player_1, player_2):
    NUMBER_OF_ROUNDS = random.randint(100, 200)  # The original module played a random number of rounds between 100 and 200
    player_1_moves = ''  # we store moves as a string of 'b's and 'c's
    player_2_moves = ''
    # That's super inefficent because of how python stores strings
    # a better version of this tool would use booleans for betraying and colluding and have a list of them
    player_1_score = 0
    player_2_score = 0
    for round in range(NUMBER_OF_ROUNDS):
        player_1_single_score, \
            player_2_single_score, \
            player_1_single_move, \
            player_2_single_move \
            = play_single_dilemma(player_1,
                                  player_2,
                                  player_1_score,
                                  player_2_score,
                                  player_1_moves,
                                  player_2_moves)
        player_1_score += player_1_single_score
        player_2_score += player_2_single_score
        player_1_moves += player_1_single_move
        player_2_moves += player_2_single_move
    player_1_score = int(player_1_score / NUMBER_OF_ROUNDS)
    player_2_score = int(player_2_score / NUMBER_OF_ROUNDS)
    # Take the integer average score for each player so that it doesn't matter that we're doing a random number of rounds
    return player_1_score, player_2_score, player_1_moves, player_2_moves


def play_single_dilemma(player_1,
                        player_2,
                        player_1_score,
                        player_2_score,
                        player_1_moves,
                        player_2_moves):

    player_1_move = player_1.move(player_1_moves,
                                  player_2_moves,
                                  player_1_score,
                                  player_2_score)
    player_2_move = player_2.move(player_2_moves,
                                  player_1_moves,
                                  player_2_score,
                                  player_1_score)
    assert player_1_move in GLOBALS.ACCEPTABLE_RESPONSES,\
        f"{player_1.team_name} gave a bad response in a match against {player_2.team_name}"
    assert player_2_move in GLOBALS.ACCEPTABLE_RESPONSES,\
        f"{player_2.team_name} gave a bad response in a match against {player_1.team_name}"
    player_1_round_score = 0
    player_2_round_score = 0
    if (player_1_move == GLOBALS.COLLUDE) and (player_2_move == GLOBALS.COLLUDE):
        player_1_round_score += GLOBALS.REWARD
        player_2_round_score += GLOBALS.REWARD
    elif (player_1_move == GLOBALS.COLLUDE) and (player_2_move == GLOBALS.BETRAY):
        player_1_round_score += GLOBALS.SUCKER
        player_2_round_score += GLOBALS.TEMPTATION
    elif (player_1_move == GLOBALS.BETRAY) and (player_2_move == GLOBALS.COLLUDE):
        player_1_round_score += GLOBALS.TEMPTATION
        player_2_round_score += GLOBALS.SUCKER
    elif (player_1_move == GLOBALS.BETRAY) and (player_2_move == GLOBALS.BETRAY):
        player_1_round_score += GLOBALS.PUNISHMENT
        player_2_round_score += GLOBALS.PUNISHMENT
    return player_1_round_score,\
        player_2_round_score,\
        player_1_move,\
        player_2_move


def make_section_title(title: str):
    print('{:-^80}'.format(''))
    print('{:^80}'.format(title))
    print('{:-^80}'.format(''))


def display_team_info(team: Team):
    print(f'P{team.team_number}: {team.team_name} using {team.strategy_name} ({team.strategy_description})')


def display_lineup(teams: List[Team]):
    make_section_title('Lineup')
    for team in teams:
        display_team_info(team)


def display_pvp_score(scores: List[List[int]]):
    make_section_title('Player vs. Player Scores')
    print("To find player n's average score against player m, check the nth row and the mth column")
    print(DataFrame(scores))


def display_standings(teams: List[Team], scores):
    make_section_title('Standings')
    for team_index in range(len(teams)):
        teams[team_index].summed_scores = sum_list(scores[team_index])
    teams.sort(key=lambda team: team.summed_scores, reverse=True)
    for team_index in range(len(teams)):
        team = teams[team_index]
        print('{0:2}) {1:<16}(P{2}): {3:>8} points with {4:<20}'.format(team_index + 1, team.team_name, team.team_number, team.summed_scores, team.strategy_name))


def main(module_names: List[str], should_random: bool):
    teams = load_modules(module_names)
    if should_random:
        random.shuffle(teams)
    if not teams:
        return 1
    else:
        display_lineup(teams)
        scores, moves = play_tournament(teams)
        display_pvp_score(scores)
        display_standings(teams, scores)
