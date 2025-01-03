import './JoystickControl.css'
import {Joystick} from "react-joystick-component";
import {useEffect, useRef, useState} from "react";
import useWebSocket from "react-use-websocket";

export default function JoystickControl() {
  const [joystickSize, setJoystickSize] = useState(window.screen.width < 400 ? window.screen.width * 0.85 : 400)
  const [stickSize, setStickSize] = useState(joystickSize * 0.4)
  const wsMsgFilter = () => {
    return true
  }
  const {sendJsonMessage, sendMessage, readyState, getWebSocket} = useWebSocket('ws://raspberrypi.local:8000',
    {reconnectInterval: 100, heartbeat: false, filter: wsMsgFilter})
  const JOYSTICK_DEADZONE = 10
  let leftMotThrust = useRef(0)
  let rightMotThrust = useRef(0)

  function rescaleJoystickPos(posValue) {
    const pos = Math.abs(posValue) * 100
    if (pos <= JOYSTICK_DEADZONE) return 0
    else {
      return (pos - JOYSTICK_DEADZONE) / (100 - JOYSTICK_DEADZONE) * 100
    }
  }
  function handleJoystickMove(position) {
    console.log(position)
    const power = rescaleJoystickPos(position.y)
    const turn = rescaleJoystickPos(position.x)
    let outsideWheelSpeed = power
    let insideWheelSpeed = (100 - turn) * power / 100
    if (position.y < 0) {
      outsideWheelSpeed *= -1
      insideWheelSpeed *= -1
    }
    if (position.x > 0) {
      leftMotThrust.current = outsideWheelSpeed
      rightMotThrust.current = insideWheelSpeed
    } else {
      leftMotThrust.current = insideWheelSpeed
      rightMotThrust.current = outsideWheelSpeed
      console.log(leftMotThrust)
    }
  }

  function sendControlData() {
    sendJsonMessage({
      type: 'motorControl',
      params: {
        leftMotor: {
          action: Math.abs(leftMotThrust.current) > 0 ? 'drive' : 'stop',
          thrust: leftMotThrust.current
        },
        rightMotor: {
          action: Math.abs(rightMotThrust.current) > 0 ? 'drive' : 'stop',
          thrust: rightMotThrust.current
        }
      }
    }, false)
  }

  useEffect(() => {
    const interval = setInterval(sendControlData, 100);
    return () => clearInterval(interval);
  });

  function onShutdownClick() {
    sendMessage("shutdown", false)
  }

  return (
  <>
    <div className="joystick-container">
      <Joystick size={joystickSize} stickSize={stickSize} baseShape="square" controlPlaneShape="square" minDistance={JOYSTICK_DEADZONE} baseColor="gray" stickColor="black" move={handleJoystickMove} stop={handleJoystickMove}></Joystick>
    </div>
    <p>Control connection: {readyState === 1 ? 'CONNECTED' : 'NOT CONNECTED'}</p>
    <button className="turnoff-btn" onClick={onShutdownClick}>Turn off robot</button>
  </>
  )
}