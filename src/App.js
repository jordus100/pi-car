import './App.css';
import JoystickControl from "./JoystickControl";
import {useEffect} from "react";

function App() {
  useEffect(() => {
    document.title = 'Robot remote control'
  }, []);
  return (
    <div className="App">
      <h1>Jordan's robot remote control</h1>
      <img className="streamImg" src="http://raspberrypi.local:9000/stream.mjpg"/>
      <JoystickControl></JoystickControl>
    </div>
  );
}

export default App;