from conga import __version__

from pytest import fixture

from conga.game import Game, GameStatus
from conga.card import Card, Suit, Joker
from conga.player import Player


@fixture
def game_started():
    game = Game()

    game.add_player("player_1")
    game.add_player("player_2")

    game.start_match()

    game.players[0].hand = [
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=2),
        Card(suit=Suit.clubs, number=3),
        Card(suit=Suit.clubs, number=4),
        Card(suit=Suit.gold, number=7),
        Card(suit=Suit.clubs, number=7),
        Card(suit=Suit.sword, number=7),
    ]

    game.players[1].hand = [
        Card(suit=Suit.clubs, number=12),
        Card(suit=Suit.sword, number=12),
        Card(suit=Suit.gold, number=11),
        Card(suit=Suit.cups, number=11),
        Card(suit=Suit.clubs, number=10),
        Card(suit=Suit.sword, number=10),
        Card(suit=Suit.gold, number=7),
    ]

    return game


def test_version():
    assert __version__ == "0.1.0"


def test_game(game_started):
    game = game_started

    game.player_turn_pick()
    game.player_turn_throw(card_id=7)

    for player in game.players:
        player.update_state()

    game._finish_match()

    assert game.status == GameStatus.showcase
    assert game.players[0].score == -10
    assert game.players[1].score == 66  # player discards the 7 card

    game.start_match()
    assert game.status == GameStatus.started


def test_game_finishes(game_started):
    game = game_started

    game.players[0].score = 120
    game.players[1].score = 120

    game.player_turn_pick()
    game.player_turn_throw(card_id=7)

    for player in game.players:
        player.update_state()

    game._finish_match()

    assert game.status == GameStatus.finished
    assert game.players[0].score == 110
    assert game.players[1].score == 186


def test_player_update_state():
    player = Player(name="player_1")

    #
    # repeat same card
    #
    player.hand = [
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
    ]

    player.update_state()
    player.sort_cards()

    assert player.hand_score == 0
    assert len(player.hand_candidates) == 1
    assert len(player.hand_candidates[0]) == 7

    #
    # Introduce some Jockers
    #
    player.hand = [
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Joker.joker, number=0),
        Card(suit=Joker.joker, number=0),
    ]

    player.update_state()
    player.sort_cards()

    assert player.hand_score == 0
    assert len(player.hand_candidates) == 1
    assert len(player.hand_candidates[0]) == 5

    #
    # Introduce some Jockers and flush games with repeated cards
    #
    player.hand = [
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=2),
        Card(suit=Suit.clubs, number=3),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=1),
        Card(suit=Suit.clubs, number=2),
        Card(suit=Suit.gold, number=5),
    ]

    player.update_state()
    player.sort_cards()

    assert len(player.hand) == 7
    assert player.hand_score == 9
    assert len(player.hand_candidates) == 1
    assert len(player.hand_candidates[0]) == 3
