from dataclasses import dataclass, field
from enum import IntEnum
from random import shuffle
from typing import List, Union

from dataclasses_json import dataclass_json


class Suit(IntEnum):
    cups: int = 1
    sword: int = 2
    gold: int = 3
    clubs: int = 4


class Joker(IntEnum):
    joker: int = 5


@dataclass_json
@dataclass
class Card:
    suit: Union[Suit, Joker]
    number: int

    def __hash__(self):
        return self.suit * self.number

    def __eq__(self, other):
        return self.suit == other.suit and self.number == other.number

    def __lt__(self, other):
        return self.number < other.number

    def __le__(self, other):
        return self.number <= other.number

    def __gt__(self, other):
        return self.number > other.number

    def __ge__(self, other):
        return self.number >= other.number

    def __add__(self, other):
        if isinstance(other, int):
            return Card(suit=self.suit, number=min(12, self.number + other))

        raise ValueError(f"Invalid sum between Card and {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, int):
            return Card(suit=self.suit, number=max(1, self.number - other))

        raise ValueError(f"Invalid sum between Card and {type(other)}")

    def __rsub__(self, other):
        return self.__sub__(other)


def build_deck(n_joker=2):
    return [Card(suit, number) for number in range(1, 13) for suit in Suit] + [
        Card(suit=Joker.joker, number=0)
    ] * n_joker


@dataclass_json
@dataclass
class Deck:
    cards: List[Card] = field(default_factory=build_deck)

    def shuffle(self):
        shuffle(self.cards)


@dataclass_json
@dataclass
class DiscardDeck:
    cards: List[Card] = field(default_factory=list)
