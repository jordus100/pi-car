export default function ControlSettings({ readyState, pingTime, message }) {
  return (
    <div className="control-settings">
      <p>Control connection: {readyState === 1 ? 'CONNECTED' : 'NOT CONNECTED'}</p>
      <p>Ping: {pingTime} ms</p>
      {readyState !== 1 && <p>{message}</p>}
    </div>
  );
}