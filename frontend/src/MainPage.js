import JoystickControl from "./JoystickControl";
import './MainPage.css';
import {AuthContext} from "./services/AuthProvider";
import {useContext} from "react";

export default function MainPage() {
  const {username, isAdmin} = useContext(AuthContext);
  return (
    <div className="App">
      <h1>Surveillance robot remote control</h1>
      <p>Welcome, {username}!</p>
      <img className="streamImg" src="http://raspberrypi.local:9000/stream.mjpg"/>
      <JoystickControl></JoystickControl>
    </div>
  );
}