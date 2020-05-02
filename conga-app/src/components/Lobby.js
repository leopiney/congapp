import { h } from "preact";

import style from "./styles.css";

import Container from "preact-mui/lib/container";
import Input from "preact-mui/lib/input";
import Button from "preact-mui/lib/button";

const Lobby = ({
  name,
  handleUpdateName,
  handleEnterTable,
  handleInputName,
}) => (
  <Container
    class={style.home}
    style={{ backgroundColor: "#f5f5f5", padding: "2em" }}
  >
    <h1>Cong•app</h1>
    <Input
      type="text"
      hint="Ingresar nombre"
      value={name}
      onChange={handleUpdateName}
      onKeyDown={handleInputName}
    />

    <Button
      color="primary"
      disabled={name.length < 2}
      onClick={handleEnterTable}
    >
      Ingresar
    </Button>
  </Container>
);

// disabled={
//   typeof window !== "undefined" && localStorage.getItem("player_name")
// }

export default Lobby;
