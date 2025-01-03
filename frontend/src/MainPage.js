import JoystickControl from "./JoystickControl";

export default function MainPage() {
  return (
    <div className="App">
      <h1>Surveillance robot remote control</h1>
      <img className="streamImg" src="http://raspberrypi.local:9000/stream.mjpg"/>
      <JoystickControl></JoystickControl>
    </div>
  );
}