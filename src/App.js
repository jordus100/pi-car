import './App.css';
import JoystickControl from "./JoystickControl";
import {useEffect} from "react";

function App() {
  useEffect(() => {
    document.title = 'Robot remote control'
  }, []);
  return (
    <div className="App">
      <header>
        <h1>Jordan's robot remote control</h1>
        <img src="http://raspberrypi.local:9000/stream.mjpg" width="1640" height="1232"/>
        <JoystickControl></JoystickControl>
      </header>
    </div>
  );
}

export default App;