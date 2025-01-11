import './JoystickControl.css'
import {Joystick} from "react-joystick-component";
import {useEffect, useRef, useState} from "react";
import useWebSocket, {ReadyState} from "react-use-websocket";
import {getRobotControlWsData} from "./services/Api";
import ControlSettings from "./ControlSettings";

export default function JoystickControl() {
  const [joystickSize, setJoystickSize] = useState(window.screen.width < 500 ? window.screen.width * 0.75 : 400)
  const [stickSize, setStickSize] = useState(joystickSize * 0.4)
  const [wsUrl, setWsUrl] = useState('')
  const {sendJsonMessage, sendMessage, readyState } =
    useWebSocket(wsUrl, {reconnectInterval: 1000, onMessage: onWsMessage})
  const [message, setMessage] = useState('Connecting to control server...')
  const [pingTime, setPingTime] = useState(0)
  const pingMsgTime = useRef(0)

  const JOYSTICK_DEADZONE = 10
  let leftMotThrust = useRef(0)
  let rightMotThrust = useRef(0)

  async function initWsConnection() {
    if (readyState === ReadyState.OPEN) return
    try {
      const wsData = await getRobotControlWsData()
      setWsUrl(`ws://${process.env.REACT_APP_WS_HOST}:${wsData.wsPort}/robotControlWs?token=${wsData.token}`)
    } catch (e) {
      if (e.response && e.response.status === 400) {
        setMessage('Someone else is already controlling the robot')
      } else {
        setMessage('Failed to connect to control server')
      }
      console.error('Failed to get WS data', e)
    }
  }

  function onWsMessage(event) {
    const msg = event.data
    if (msg === 'pongMsg') {
      const pingTime = Date.now() - pingMsgTime.current
      setPingTime(pingTime)
    }
  }

  function rescaleJoystickPos(posValue) {
    const pos = Math.abs(posValue) * 100
    if (pos <= JOYSTICK_DEADZONE) return 0
    else {
      return (pos - JOYSTICK_DEADZONE) / (100 - JOYSTICK_DEADZONE) * 100
    }
  }

  function handleJoystickMove(position) {
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

  function sendPing() {
    sendMessage('pingMsg', false)
    pingMsgTime.current = Date.now()
  }

  useEffect(() => {
    initWsConnection()
  }, []);
  useEffect(() => {
    const controlMsgInterval = setInterval(sendControlData, 50);
    return () => {
      clearInterval(controlMsgInterval)
    }
  }, [sendJsonMessage]);
  useEffect(() => {
    const pingInterval = setInterval(sendPing, 5000)
    return () => {
      clearInterval(pingInterval)
    }
  }, [sendMessage]);
  useEffect(() => {
    // check every 10 seconds if the connection is still open, if not try to reconnect
    const reconnectInterval = setInterval(initWsConnection, 10000)
    return () => {
      clearInterval(reconnectInterval)
    }
  }, [readyState]);

  return (
    <div className={"robot-control"}>
      <div className="dummy"></div>
      <div className="joystick-container">
        {readyState !== ReadyState.OPEN ? <p>{message}</p> :
          <Joystick size={joystickSize} stickSize={stickSize} baseShape="square" controlPlaneShape="square"
                    minDistance={JOYSTICK_DEADZONE} baseColor="gray" stickColor="black" move={handleJoystickMove}
                    stop={handleJoystickMove}></Joystick>
        }
      </div>
      <div className="control-settings-container">
        <ControlSettings readyState={readyState} pingTime={pingTime} message={message} sendJsonMessage={sendJsonMessage}/>
      </div>
    </div>
  )
}