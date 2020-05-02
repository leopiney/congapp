import { h } from "preact";

import style from "./styles.css";

import Container from "preact-mui/lib/container";

const TableEnd = ({ game }) => {
  const winningPlayer = game.players.find((player) => player.won_match);

  return (
    <Container
      fluid={true}
      class={style.home}
      style={{ backgroundColor: "#f5f5f5", padding: "2em" }}
    >
      <h1>Ganó {winningPlayer.name}</h1>
    </Container>
  );
};

export default TableEnd;
