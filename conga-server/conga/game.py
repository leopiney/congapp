import itertools
import math
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from dataclasses_json import dataclass_json

from conga.card import Deck, DiscardDeck
from conga.player import Player, PlayerStatus, check_cards_values


class GameStatus(IntEnum):
    lobby: int = 0
    started: int = 1
    showcase: int = 2
    finished: int = 3


@dataclass_json
@dataclass
class Game:
    status: GameStatus = GameStatus.lobby
    deck: Deck = None
    discard_deck: DiscardDeck = None
    players: List[Player] = field(default_factory=list)
    match_id: int = 0
    match_next_player: int = 0
    match_start_player: int = 0

    def add_player(self, name: str):
        if self.status == GameStatus.lobby:
            if all(player.name != name for player in self.players):
                self.players.append(Player(name=name))

    def _prepare_deck(self):
        self.deck = Deck()
        self.discard_deck = DiscardDeck()

        n_decks = math.ceil(len(self.players) / 4)

        for i in range(n_decks - 1):
            new_deck = Deck()
            self.deck.cards.extend(new_deck.cards)

        self.deck.shuffle()

    def start_match(self):
        if self.status != GameStatus.started:
            self.status = GameStatus.started

        self.match_id += 1
        if self.match_id == 1:
            self.match_start_player = 0
        else:
            self.match_start_player = (self.match_start_player + 1) % len(self.players)

        self._prepare_deck()
        self.match_next_player = self.match_start_player

        for player in self.players:
            player.hand = []
            player.hand_discarded = []
            player.won_match = False

        for i in range(7):
            for player in self.players:
                player.hand.append(self.deck.cards.pop())
                player.update_state()

    def player_turn_pick(self, pick_discard_pile: bool = False):
        player = self.players[self.match_next_player]

        assert len(player.hand) == 7, "Can't pick new card"

        new_card = self.discard_deck.cards.pop(0) if pick_discard_pile else self.deck.cards.pop(0)
        player.hand.append(new_card)

    def _finish_match(self):
        self.status = GameStatus.showcase

        winning_player = self.players[self.match_next_player]
        winning_player.won_match = True

        for player_a in (
            self.players[self.match_next_player :] + self.players[: self.match_next_player]
        ):
            for player_b in (
                self.players[self.match_next_player :] + self.players[: self.match_next_player]
            ):
                if player_a == player_b:
                    continue

                updated_candidates = []
                for candidate in player_a.hand_candidates:
                    updated_candidate = candidate
                    cards_to_discard = [
                        card
                        for card in player_b.hand
                        if card not in list(itertools.chain(*player_b.hand_candidates))
                        and card not in player_b.hand_discarded
                    ]

                    for card in cards_to_discard:
                        disc_candidates, candidate_score = check_cards_values(candidate + [card])
                        if candidate_score == 0 and len(disc_candidates) == 1:
                            # this card can be discarded
                            player_b.hand_discarded.append(card)
                            updated_candidate.append(card)

                    updated_candidates.append(updated_candidate)

                player_a.hand_candidates = updated_candidates

        for player in self.players:
            for card in player.hand_discarded:
                player.hand_score -= card.number

        max_score = 0

        for player in self.players:
            if player == winning_player and player.hand_score == 0:
                player.hand_score = -10

            player.score += player.hand_score

            player.can_finish = False

            if player.score > 120:
                player.status = PlayerStatus.lost
            else:
                max_score = max(max_score, player.score)

        for player in self.players:
            if player.status == PlayerStatus.lost and player.restarts < 2:
                player.status = PlayerStatus.playing
                player.score = max_score
                player.restarts += 1

        game_finished = all(
            player.status == PlayerStatus.lost
            for ix, player in enumerate(self.players)
            if ix != self.match_next_player
        )
        if game_finished:
            self.status = GameStatus.finished

    def _reshufle_deck(self):
        self.deck.cards = self.discard_deck.cards
        self.deck.shuffle()
        self.discard_deck = DiscardDeck()

    def player_turn_throw(self, card_id: int):
        player = self.players[self.match_next_player]

        assert len(player.hand) == 8, "Can't throw card"

        self.discard_deck.cards.insert(0, player.hand.pop(card_id))
        player.finish_next_turn = False
        player.update_state()

        if not player.can_finish:
            self.match_next_player = (self.match_next_player + 1) % len(self.players)

        if len(self.deck.cards) == 0:
            self._reshufle_deck()

    def player_finish_attempt(self, player_finishes):
        if self.status != GameStatus.started:
            return

        if player_finishes:
            self._finish_match()
        else:
            player = self.players[self.match_next_player]
            player.finish_next_turn = True
            self.match_next_player = (self.match_next_player + 1) % len(self.players)

        if len(self.deck.cards) == 0:
            self._reshufle_deck()


if __name__ == "__main__":
    game = Game()
    game.add_player("Leo")
    game.add_player("Lu")

    game.start_match()

    game.player_turn_pick()
    game.player_turn_throw(2)

    game.player_turn_pick()
    game.player_turn_throw(4)

    # print(len(game.deck.cards))
    # print(len(game.discard_deck.cards))
    # print("Player 0")
    # pprint.pprint(game.players[0].hand)
    # pprint.pprint(game.players[0].hand_candidates)
    # pprint.pprint(game.players[0].hand_score)
    # print("Player 1")
    # pprint.pprint(game.players[1].hand)
    # pprint.pprint(game.players[1].hand_candidates)
    # pprint.pprint(game.players[1].hand_score)
