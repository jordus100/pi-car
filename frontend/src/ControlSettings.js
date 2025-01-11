import {useEffect, useState} from "react";
import "./ControlSettings.css";
import {getSettings} from "./services/Api";

export default function StatusText({ readyState, pingTime, message, sendJsonMessage}) {
  const [maxPower, setMaxPower] = useState(100); // Default max power
  const [engineTrim, setEngineTrim] = useState(0); // Default engine trim

  useEffect(() => {
    getSettings().then((settings) => {
      setMaxPower(parseInt(settings.find((setting) => { return setting.settingName === "maxMotorPower" }).value))
      setEngineTrim(parseInt(settings.find((setting) => { return setting.settingName === "motorTrim" }).value))
    })
  }, []);
  function handleMaxPowerChange(event) {
    const value = Math.max(0, Math.min(100, event.target.value)); // Clamp between 0 and 100
    setMaxPower(value);
    sendJsonMessage({
      type: "settings",
      params: {
        maxPower: value
      }
    })
  }

  function handleEngineTrimChange(event) {
    const value = Math.max(-50, Math.min(50, event.target.value)); // Clamp between -50 and 50
    setEngineTrim(value);
    sendJsonMessage({
      type: "settings",
      params: {
        motorTrim: value
      }
    })
  }

  return (
    <div className={"control-settings"}>
      <p>Control connection: {readyState === 1 ? "CONNECTED" : "NOT CONNECTED"}</p>
      { readyState === 1 && pingTime > 0 && <p>Ping: {pingTime} ms</p> }
      { readyState === 1 &&
        <div className={"settings"}>
          <div>
            <label>
              Max Engine Power:
              <input
                type="range"
                value={maxPower}
                onMouseUp={handleMaxPowerChange}
                onChange={(event) => setMaxPower(event.target.value)}
                min="0"
                max="100"
              />
              <p className={"value"}>{maxPower}</p>
            </label>
          </div>
          <div>
            <label>
              Motor Trim (bias):&nbsp;&nbsp;&nbsp;
              <input
                type="range"
                value={engineTrim}
                onChange={(event) => setEngineTrim(event.target.value)}
                onMouseUp={handleEngineTrimChange}
                min="-50"
                max="50"
              />
              <p className={"value"}>{engineTrim}</p>
            </label>
          </div>
        </div>
      }
    </div>
  );
}
