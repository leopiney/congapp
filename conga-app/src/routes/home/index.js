import { h, Component } from "preact";

import Lobby from "../../components/Lobby";
import TableWaiting from "../../components/TableWaiting";
import Table from "../../components/Table";
import TableFinish from "../../components/TableFinish";
import TableEnd from "../../components/TableEnd";

const WS_ADDRESS = "ws://localhost:8000/ws";

export default class Home extends Component {
  state = {
    game: null,
    isInTable: false,
    name: "",
    selectedCard: null,
  };

  webSocket = null;

  send = (action, action_params = {}) =>
    this.webSocket.send(JSON.stringify({ action, action_params }));

  handleInputName = (event) => {
    if (event.key === "Enter") {
      this.setState({ name: event.target.value, isInTable: true });
    }
  };

  handleUpdateName = (event) => {
    this.setState({ name: event.target.value });
  };

  handleEnterTable = () => {
    setTimeout(() => {
      this.setState({ isInTable: true });
      localStorage.setItem("player_name", this.state.name);
    }, 500);
  };

  handleStartMatch = () => this.send("start_match");

  handleClickCard = (cardKind, card, index) => {
    console.log(`Clicking ${cardKind} card #${index} ${JSON.stringify(card)} `);
    const { game, name } = this.state;

    const nextPlayer = game.players[game.match_next_player];
    const isPlayerTurn = nextPlayer.name === name;

    if (cardKind === "hand") {
      // Picking from hand
      if (
        this.state.selectedCard === null ||
        this.state.selectedCard !== index
      ) {
        this.setState({ selectedCard: index });
      } else if (
        this.state.selectedCard !== null &&
        this.state.selectedCard === index &&
        isPlayerTurn
      ) {
        this.setState({ selectedCard: null });
        this.send("player_turn_throw", { card_id: index });
      }
    } else if (isPlayerTurn) {
      // Picking from deck or discard_deck
      this.send("player_turn_pick", {
        pick_discard_pile: cardKind === "discard_deck",
      });
    }
  };

  handleCanFinish = (player_finishes) =>
    this.send("player_finish_attempt", { player_finishes });

  wsOnMessage = (event) => {
    console.log("Receiving message");
    const game = JSON.parse(event.data).game;
    console.log("Game status", game);
    this.setState({ game });
  };

  componentWillMount() {
    if (typeof window !== "undefined") {
      localStorage.clear();
      if (localStorage.getItem("player_name") && !this.state.name) {
        this.setState({ name: localStorage.getItem("player_name") });
      }
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (!prevState.isInTable && this.state.isInTable) {
      this.webSocket = new WebSocket(WS_ADDRESS);
      this.webSocket.onmessage = this.wsOnMessage;

      // Send message as soon as we connect to WS server
      this.webSocket.onopen = () =>
        this.send("add_player", { name: this.state.name });
    }
  }

  render({}, { game, name, isInTable, selectedCard }) {
    if (!isInTable) {
      return (
        <Lobby
          name={name}
          handleUpdateName={this.handleUpdateName}
          handleEnterTable={this.handleEnterTable}
          handleInputName={this.handleInputName}
        />
      );
    } else if (game && game.status === 0) {
      return (
        <TableWaiting game={game} handleStartMatch={this.handleStartMatch} />
      );
    } else if (game && game.status === 1) {
      return (
        <Table
          name={name}
          game={game}
          selectedCard={selectedCard}
          handleClickCard={this.handleClickCard}
          handleCanFinish={this.handleCanFinish}
        />
      );
    } else if (game && game.status === 2) {
      return (
        <TableFinish
          name={name}
          game={game}
          handleStartMatch={this.handleStartMatch}
        />
      );
    } else if (game && game.status === 3) {
      return <TableEnd game={game} />;
    }

    return <h3>Cargando...</h3>;
  }
}
