import { h } from "preact";

import style from "./styles.css";

import Button from "preact-mui/lib/button";
import Container from "preact-mui/lib/container";

const TableWaiting = ({ game, handleStartMatch }) => (
  <Container
    class={style.home}
    style={{ backgroundColor: "#f5f5f5", padding: "2em" }}
  >
    <h1>Jugadores</h1>
    {game.players.map((player) => (
      <p key={player.name}>{player.name}</p>
    ))}

    <Button color="primary" onClick={handleStartMatch}>
      Empezar juego
    </Button>
  </Container>
);

export default TableWaiting;
