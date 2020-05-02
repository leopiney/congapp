import { h, Component } from "preact";
import { Router } from "preact-router";

// Code-splitting is automated for routes
import Home from "../routes/home";

export default class App extends Component {
  /** Gets fired when the route changes.
   *	@param {Object} event		"change" event from [preact-router](http://git.io/preact-router)
   *	@param {string} event.url	The newly routed URL
   */
  handleRoute = (e) => {
    this.currentUrl = e.url;
  };

  render() {
    return (
      <div id="app">
        <Router onChange={this.handleRoute}>
          <Home path="/" />
        </Router>

        <link
          href="//cdn.muicss.com/mui-0.9.6/css/mui.min.css"
          rel="stylesheet"
          type="text/css"
          media="screen"
        />
        <script src="//cdn.muicss.com/mui-0.9.6/js/mui.min.js" />
      </div>
    );
  }
}
