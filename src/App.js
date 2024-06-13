import './App.css';
import JoystickControl from "./JoystickControl";

function App() {
  return (
    <div className="App">
      <header>
        <h1>Jordan's robot remote control</h1>
        <img src="http://raspberrypi.local:9000/stream.mjpg" width="640" height="480"/>
        <JoystickControl></JoystickControl>
      </header>
    </div>
  );
}

export default App;