import { h } from "preact";

import tableBackground from "../assets/table.jpg";
import style from "./styles.css";

import Button from "preact-mui/lib/button";
import Container from "preact-mui/lib/container";
import Panel from "preact-mui/lib/panel";
import Card, { CARD_HEIGHT, CARD_WIDTH } from "./Card";

const Table = ({
  game,
  name,
  selectedCard,
  handleClickCard,
  handleCanFinish,
}) => {
  const player = game.players.find((player) => player.name === name);
  const nextPlayer = game.players[game.match_next_player];
  const isPlayerTurn = nextPlayer.name === name;

  return (
    <Container
      class={style.home}
      style={{
        background: `url(${tableBackground}) 0px 0px`,
        backgroundSize: "cover",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Panel
        style={{
          position: "absolute",
          margin: 10,
          color: isPlayerTurn ? "red" : "black",
          fontSize: "2em",
          opacity: 0.9,
        }}
      >
        {isPlayerTurn ? "Tu turno!" : `Turno de ${nextPlayer.name}`}
      </Panel>

      <div
        style={{
          position: "absolute",
          width: CARD_WIDTH,
          left: "30%",
          top: 20,
        }}
      >
        <Card
          cardKind="deck"
          index={-1}
          suit=""
          number={0}
          handleClickCard={handleClickCard}
        />
      </div>

      {game.discard_deck.cards.length > 0 && (
        <div
          style={{
            position: "absolute",
            width: CARD_WIDTH,
            right: "30%",
            top: 20,
          }}
        >
          <Card
            cardKind="discard_deck"
            index={-1}
            suit={game.discard_deck.cards[0].suit}
            number={game.discard_deck.cards[0].number}
            handleClickCard={handleClickCard}
          />
        </div>
      )}

      {player.can_finish && !player.finish_next_turn && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100vh",
            backgroundColor: "#000000dd",
            zIndex: 9999,
            textAlign: "center",
            paddingTop: "20%",
          }}
        >
          <Button
            color="primary"
            style={{ fontSize: "2em", height: "5em", width: "8em" }}
            onClick={() => handleCanFinish(true)}
          >
            Cortar
          </Button>
          <Button color="danger" onClick={() => handleCanFinish(false)}>
            No cortar
          </Button>
        </div>
      )}

      <div
        style={{
          position: "absolute",
          margin: "100vh 50vw 0",
          transform: `translate(-${player.hand.length === 8 ? 290 : 255}px, -${
            isPlayerTurn ? CARD_HEIGHT + 30 : CARD_HEIGHT
          }px)`,
        }}
      >
        {player.hand.map((card, index) => (
          <Card
            cardKind="hand"
            index={index}
            suit={card.suit}
            number={card.number}
            selected={index === selectedCard}
            handleClickCard={handleClickCard}
            key={`${card.suit}${card.number}${index}`}
          />
        ))}
      </div>
    </Container>
  );
};

export default Table;
