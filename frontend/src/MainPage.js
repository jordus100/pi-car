import JoystickControl from "./JoystickControl";
import './MainPage.css';
import {AuthContext} from "./services/AuthProvider";
import {useContext} from "react";

export default function MainPage() {
  const {username, isAdmin} = useContext(AuthContext);
  const streamUrl = process.env.REACT_APP_CAMERA_URL;
  return (
    <div className="App">
      <h1>Surveillance robot remote control</h1>
      <p>Welcome, {username}!</p>
      <img className="streamImg" src={streamUrl}/>
      <JoystickControl></JoystickControl>
    </div>
  );
}