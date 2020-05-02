import { h } from "preact";

import cardsSheet from "../assets/cards.png";

import Panel from "preact-mui/lib/panel";

export const CARD_HEIGHT = 319 / 2;
export const CARD_WIDTH = 208 / 2;

const Suit = {
  cups: 1,
  sword: 2,
  gold: 3,
  clubs: 4,
  joker: 5,
};

const cardPosition = (suit, number) => {
  if (suit === Suit.gold) {
    return [(number - 1) * CARD_WIDTH, 0];
  } else if (suit == Suit.cups) {
    return [(number - 1) * CARD_WIDTH, CARD_HEIGHT];
  } else if (suit == Suit.sword) {
    return [(number - 1) * CARD_WIDTH, 2 * CARD_HEIGHT];
  } else if (suit == Suit.clubs) {
    return [(number - 1) * CARD_WIDTH, 3 * CARD_HEIGHT];
  } else if (suit == Suit.joker) {
    return [0, 4 * CARD_HEIGHT];
  }

  return [CARD_WIDTH, 4 * CARD_HEIGHT];
};

const Card = ({
  cardKind,
  index,
  suit,
  number,
  handleClickCard,
  selected = false,
}) => {
  const [x, y] = cardPosition(suit, number);
  let position = {};

  if (index != -1) {
    const selectedOffset = selected ? 10 : 0;
    const selectedScale = selected ? 1.15 : 1;
    const selectedZIndex = selected ? 9999 : "inherit";

    position = {
      left: `calc(${index * 70}px)`,
      transformOrigin: "center center",
      transform: `translateY(${
        Math.abs(index - 4) * 20 - selectedOffset
      }px) rotate(${(index - 4) * 8}deg) scale(${selectedScale})`,
      zIndex: selectedZIndex,
    };
  }

  return (
    <Panel
      onClick={() => handleClickCard(cardKind, { suit, number }, index)}
      style={{
        position: "absolute",
        height: CARD_HEIGHT,
        width: CARD_WIDTH,
        background: `url(${cardsSheet}) 0px 0px`,
        backgroundPosition: `-${x}px -${y}px`,
        borderRadius: 8,
        ...position,
      }}
    />
  );
};

export default Card;
