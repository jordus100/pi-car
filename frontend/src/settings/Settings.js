import React, {useContext, useState} from 'react';
import './Settings.css';
import ChangePassword from "./ChangePassword";
import UserManagement from "./UserManagement";
import {AuthContext} from "../services/AuthProvider";
import {turnOffRobot} from "../services/Api";
import Networking from "./Networking";

const Settings = () => {
  const { isAdmin } = useContext(AuthContext);
  const [shutdownMsg, setShutdownMsg] = useState('');
  function onTurnOffBtnClick() {
    if(window.confirm('Are you sure you want to turn off the robot?')) {
      turnOffRobot()
        .finally(() => {
          setShutdownMsg('Shutdown command sent');
        });
    }
  }

  return (
    <div className="admin-user-menu">
      <header className="menu-header">
        <h1>Settings</h1>
      </header>
      <ChangePassword/>
      <button className={'toggle-btn'} onClick={onTurnOffBtnClick}>Turn off robot</button>
      {shutdownMsg && <p>{shutdownMsg}</p>}
      {isAdmin && <h1>Admin Settings</h1>}
      {isAdmin && (
        <>
          <UserManagement/>
          <Networking/>
        </>
      )}
    </div>
  );
};

export default Settings;