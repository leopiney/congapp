import { h } from "preact";

import style from "./styles.css";

import Button from "preact-mui/lib/button";
import Container from "preact-mui/lib/container";
import Row from "preact-mui/lib/row";
import Col from "preact-mui/lib/col";

const SuitEnum = ["", "copa", "esp", "oro", "basto", "comodin"];

const TableFinish = ({ game, name, handleStartMatch }) => {
  const player = game.players.find((player) => player.name === name);
  const winningPlayer = game.players.find((player) => player.won_match);

  return (
    <Container
      fluid={true}
      class={style.home}
      style={{ backgroundColor: "#f5f5f5", padding: "2em" }}
    >
      <Row>
        <Col xs="6">
          <h1>
            {player.won_match
              ? "Ganaste!"
              : `Te ganaron! Cortó ${winningPlayer.name}`}
          </h1>

          <h2>Puntaje: +{player.hand_score}</h2>
          <h2>Puntaje total: {player.score}</h2>
          <h2>Cartas en juego:</h2>
          {player.hand_candidates.map((cand) => (
            <h3 style={{ marginLeft: "2em" }}>
              {cand.reduce(
                (acc, card) =>
                  `${acc} ${card.suit === 5 ? "" : card.number} ${
                    SuitEnum[card.suit]
                  },`,
                ""
              )}
            </h3>
          ))}
          {player.hand_discarded && (
            <div>
              <h2>Cartas colocadas:</h2>
              <h3 style={{ marginLeft: "2em" }}>
                {player.hand_discarded.reduce(
                  (acc, card) =>
                    `${acc} ${card.suit === 5 ? "" : card.number} ${
                      SuitEnum[card.suit]
                    },`,
                  ""
                )}
              </h3>
            </div>
          )}

          <Button
            color="primary"
            onClick={handleStartMatch}
            style={{ marginTop: "4em" }}
          >
            Empezar siguiente mano
          </Button>
        </Col>
        <Col xs="6">
          <h1>Puntajes</h1>
          {game.players.map((player) => (
            <h2 key={player.name}>
              {player.name}: {player.score}
            </h2>
          ))}
        </Col>
      </Row>
    </Container>
  );
};

export default TableFinish;
