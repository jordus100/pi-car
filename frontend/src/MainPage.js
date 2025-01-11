import JoystickControl from "./JoystickControl";
import './MainPage.css';
import {AuthContext} from "./services/AuthProvider";
import {useContext} from "react";
import {useNavigate} from "react-router-dom";

export default function MainPage() {
  const {username, isAdmin, logout} = useContext(AuthContext);
  const streamUrl = process.env.REACT_APP_CAMERA_URL;
  const navigate = useNavigate();
  function onLogoutBtnClick() {
    logout();
  }
  function onSettingsBtnClick() {
    navigate('/settings');
  }
  return (
    <div className="App">
      <div className={"header-center"}>
        <h1>Surveillance robot remote control</h1>
        <p>Welcome, {username}!</p>
      </div>
      <div className="header">
        <div className={"header-left"}>
        </div>
        <div className={"header-right"}>
          <button className={"button-3"} onClick={onSettingsBtnClick}>Settings</button>
          <button className={"button-3"} onClick={onLogoutBtnClick}>Log out</button>
        </div>
      </div>
      <img className="streamImg" src={streamUrl}/>
      <JoystickControl></JoystickControl>
    </div>
  );
}