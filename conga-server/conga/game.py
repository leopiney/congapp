import itertools
import math
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from dataclasses_json import dataclass_json
from tqdm import tqdm

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
    """Represent a Conga Game state

    This class provides methods to alter the state as the game goes
    """

    status: GameStatus = GameStatus.lobby
    deck: Deck = None
    discard_deck: DiscardDeck = None
    players: List[Player] = field(default_factory=list)
    match_id: int = 0
    match_next_player: int = 0
    match_start_player: int = 0

    def add_player(self, name: str):
        """Adds a new player only if the game didn't start yet"""
        if self.status == GameStatus.lobby and name not in [player.name for player in self.players]:
            self.players.append(Player(name=name))

    def _prepare_deck(self):
        """Builds a deck and shuffles it. It "adds" a new deck every 4 players"""
        self.deck = Deck()
        self.discard_deck = DiscardDeck()

        n_decks = math.ceil(len(self.players) / 4)

        for i in range(n_decks - 1):
            new_deck = Deck()
            self.deck.cards.extend(new_deck.cards)

        self.deck.shuffle()

    def start_match(self):
        """Starts the match for the first time, or after a showcase state.

        * Updates the `match_start_player` to the player on the right
        * Prepares the deck
        * Sorts and give cards to players
        * Updates players states
        """
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

        self.update_players_state()

    def player_turn_pick(self, pick_discard_pile: bool = False):
        """Current player picks from a deck. Updates players state"""
        player = self.players[self.match_next_player]

        assert len(player.hand) == 7, "Can't pick new card"

        #
        # Pick cards from "the top" of the deck (obviously)
        #
        new_card = self.discard_deck.cards.pop(0) if pick_discard_pile else self.deck.cards.pop(0)
        player.hand.append(new_card)

    def _reshuffle_deck(self):
        """If deck runs out of cards, reshufle the discard deck and start again"""
        self.deck.cards = self.discard_deck.cards
        self.deck.shuffle()
        self.discard_deck = DiscardDeck()

    def update_players_state(self):
        """Updates the state for all players"""
        for player in self.players:
            player.update_state()

    def player_turn_throw(self, card_id: int):
        """Current player discards a card from their hand"""
        player = self.players[self.match_next_player]

        assert len(player.hand) == 8, "Can't throw card"

        self.discard_deck.cards.insert(0, player.hand.pop(card_id))

        #
        # Update state and check if player can finish in this turn
        #
        player.finish_next_turn = False
        player.update_state()

        #
        # If player can finish we want to ask the player if he/she wants to finish the round
        #
        if not player.can_finish:
            self.match_next_player = (self.match_next_player + 1) % len(self.players)

        # Reshuffle deck if it runs out of cards
        if len(self.deck.cards) == 0:
            self._reshuffle_deck()

    def _finish_match(self):
        """Finish a round of the game. Game might end if the enough conditions are given"""
        self.status = GameStatus.showcase

        winning_player = self.players[self.match_next_player]
        winning_player.won_match = True

        #
        # Super complicated way of detecting if players can insert their cards in another player
        # game.
        #
        # TODO: think how this should work for more than 15 minutes
        #
        t = tqdm()

        #
        # Iterate through players in the expected right direction, starting from the player that
        # started the round
        #
        for player_a in (
            self.players[self.match_next_player :] + self.players[: self.match_next_player]
        ):
            for player_b in (
                self.players[self.match_next_player :] + self.players[: self.match_next_player]
            ):
                if player_a == player_b:
                    continue

                for i, candidate in enumerate(player_a.hand_candidates):
                    # Check what player_b' cards can be used to discard points from his/her hand
                    cards_to_discard = [
                        card
                        for card in player_b.hand
                        if card not in list(itertools.chain(*player_b.hand_candidates))
                        and card not in player_b.hand_discarded
                    ]

                    for card in cards_to_discard:
                        t.set_description(
                            f"For {player_a.name}'s game #{i}, looking {player_b.name}'s "
                            "cards to discard"
                        )
                        t.update()

                        #
                        # If we add a card to a game and the resulted score is 0 with no new game
                        # then we can discard that card
                        #
                        disc_candidates, candidate_score = check_cards_values(candidate + [card])
                        if candidate_score == 0 and len(disc_candidates) == 1:
                            #
                            # Add this card to the discarded cards of the player
                            # (can't be discarded twice)
                            #
                            player_b.hand_discarded.append(card)

                            #
                            # Also, update the original candidate game. For example, in a flush game
                            # the discarded cards of a player affect how the other players
                            # can discard cards
                            #
                            candidate.append(card)

        t.close()

        #
        # Reduce score for all the cards discarded
        #
        for player in self.players:
            for card in player.hand_discarded:
                player.hand_score -= card.number

        #
        # Update players scores based on hand values. Also, calculate maximum score if it happens
        # that players can rejoin the game
        #
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

        #
        # Check if game finished: all players lost except the one who won (lol)
        #
        game_finished = all(
            player.status == PlayerStatus.lost
            for ix, player in enumerate(self.players)
            if ix != self.match_next_player
        )
        if game_finished:
            self.status = GameStatus.finished

        #
        # Players might rejoin game if game didn't finish
        #
        if not game_finished:
            for player in self.players:
                if player.status == PlayerStatus.lost and player.restarts < 2:
                    player.status = PlayerStatus.playing
                    player.score = max_score
                    player.restarts += 1

    def player_finish_attempt(self, player_finishes: bool):
        """Player can finish, but he/she might not want to do that"""
        if self.status != GameStatus.started:
            return

        if player_finishes:
            self._finish_match()
        else:
            player = self.players[self.match_next_player]
            player.finish_next_turn = True
            self.match_next_player = (self.match_next_player + 1) % len(self.players)
