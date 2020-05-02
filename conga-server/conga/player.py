import itertools
from collections import Counter
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Tuple

from dataclasses_json import dataclass_json

from conga.card import Card, Joker


def _check_flush_joker(comb: List[Card], j: int) -> bool:
    comb = list(comb)

    try:
        prev_ix = j - 1 - [c.suit for c in comb[:j]][::-1].index(Joker.joker)
    except ValueError:
        prev_ix = None

    if prev_ix is None or j - prev_ix > 1:
        prev_ix = j - 1

    ix_diff_to_next = j - prev_ix + 1

    return j > 0 and comb[j].suit == Joker.joker and comb[prev_ix] + ix_diff_to_next == comb[j + 1]


def _check_flush_joker_count(comb: List[Card]) -> bool:
    no_joker_count = len([card for card in comb if card.suit != Joker.joker])
    joker_count = len([card for card in comb if card.suit == Joker.joker])

    return not joker_count > no_joker_count


def _check_flush(cards):
    suit_sorted_hand = sorted(cards, key=lambda card: (card.suit, card.number))
    candidate_hands = []

    for suit, suit_cards in itertools.groupby(suit_sorted_hand, lambda card: card.suit):
        suit_cards = list(suit_cards) + [card for card in cards if card.suit == Joker.joker]

        for i in range(3, 7):
            for comb in itertools.permutations(suit_cards, i):
                if all(
                    comb[j].number != 12
                    and _check_flush_joker_count(comb)
                    and (
                        comb[j] + 1 == comb[j + 1]  # consecutive numbers
                        or comb[j + 1].suit == Joker.joker  # next card is joker
                        or _check_flush_joker(comb, j)
                    )
                    for j in range(i - 1)
                ):
                    candidate_hands.append(comb)

    return candidate_hands


def _check_same_of_a_kind(cards):
    counter = Counter([card.number for card in cards])
    candidate_hands = []
    joker_count = len([card for card in cards if card.suit == Joker.joker])

    for number, count in counter.items():
        if count + joker_count >= 3:
            hand_cards = [
                card for card in cards if card.number == number or card.suit == Joker.joker
            ]

            for i in range(3, count + joker_count + 1):
                candidate_hands.extend(
                    [list(comb) for comb in itertools.permutations(hand_cards, i)]
                )

    return candidate_hands


def check_cards_values(cards):
    better_candidates = []
    better_hand_score = sum([card.number for card in cards])

    candidates = _check_flush(cards) + _check_same_of_a_kind(cards)
    candidates = [list(cand) for cand in candidates]

    for cand in candidates:
        current_hand = cards.copy()
        for card in cand:
            current_hand.remove(card)

        current_score = sum(card.number for card in current_hand)
        if current_score < better_hand_score:
            better_candidates = [cand]
            better_hand_score = current_score

    for cand_a, cand_b in itertools.combinations(candidates, 2):
        current_hand = cards.copy()

        for card in cand_a:
            current_hand.remove(card)

        try:
            for card in cand_b:
                current_hand.remove(card)
        except ValueError:
            # cannot create cand_b candidate with current cards
            continue

        current_score = sum(card.number for card in current_hand)
        if current_score < better_hand_score:
            better_candidates = [cand_a, cand_b]
            better_hand_score = current_score

    return list(better_candidates), better_hand_score


class PlayerStatus(IntEnum):
    playing = 0
    limbo = 1
    lost = 2


@dataclass_json
@dataclass
class Player:
    name: str
    hand_score: int = 0
    hand_candidates: List[List[Card]] = field(default_factory=list)
    can_finish: bool = False
    finish_next_turn: bool = True
    restarts: int = 0
    score: int = 0
    hand: List[Card] = field(default_factory=list)
    hand_discarded: List[Card] = field(default_factory=list)
    status: PlayerStatus = PlayerStatus.playing
    won_match: bool = False

    def _check_hand_values(self) -> Tuple[List[List[Card]], int]:
        return check_cards_values(self.hand)

    def sort_cards(self):
        sorted_hand = []

        for cand in sorted(self.hand_candidates, key=lambda cand: len(cand)):
            sorted_hand.extend(cand)

        project_cards = [card for card in self.hand if card not in sorted_hand]
        project_cards.sort(key=lambda card: (card.number, card.suit))

        self.hand = project_cards + sorted_hand

    def update_state(self):
        self.hand_candidates, self.hand_score = self._check_hand_values()
        self.can_finish = self.hand_score <= 5 and self.score + self.hand_score <= 120
