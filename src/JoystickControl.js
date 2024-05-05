import './JoystickControl.css'
import {Joystick} from "react-joystick-component";
import {useState} from "react";
import useWebSocket from "react-use-websocket";

export default function JoystickControl() {
  const [joystickSize, setJoystickSize] = useState(window.screen.width < 400 ? window.screen.width * 0.85 : 400)
  const [stickSize, setStickSize] = useState(joystickSize * 0.4)
  const wsMsgFilter = () => {
    return true
  }
  const {sendJsonMessage, readyState, getWebSocket} = useWebSocket('ws://raspberrypi.local:8000',
    {reconnectInterval: 100, heartbeat: false, filter: wsMsgFilter})
  let leftMotThrust = 0
  let rightMotThrust = 0

  function handleJoystickMove(position) {
    console.log(position)
  }

  function handleJoystickStop() {
    leftMotThrust = rightMotThrust = 0
  }

  return (
  <>
    <div className="joystick-container">
      <Joystick size={joystickSize} stickSize={stickSize} baseShape="square" controlPlaneShape="square" minDistance="10" baseColor="gray" stickColor="black" move={handleJoystickMove} stop={handleJoystickStop}></Joystick>
    </div>
    <p>Control connection: {readyState === 1 ? 'CONNECTED' : 'NOT CONNECTED'}</p>
  </>
  )
}