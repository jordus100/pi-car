import {getIpData, getSftpSettings, joinZerotierNetwork, saveSftpSettings} from "../services/Api";
import {useEffect, useState} from "react";

export default function Networking() {
  const [message, setMessage] = useState('')
  const [networkId, setNetworkId] = useState('')
  const [sftpUsername, setSftpUsername] = useState('')
  const [sftpPassword, setSftpPassword] = useState('')
  const [sftpPort, setSftpPort] = useState('')
  const [sftpHost, setSftpHost] = useState('')
  const [ipData, setIpData] = useState([])

  async function onJoinBtnClick() {
    setMessage('')
    if (networkId) {
      try {
        await joinZerotierNetwork(networkId)
        setMessage('Joined to ZeroTier network')
      } catch (e) {
        if (e.response) {
          setMessage(e.response.data.message)
        } else {
          setMessage('Failed to join ZeroTier network')
        }
      }
    }
  }

  async function onSaveSftpClick() {
    setMessage('')
    try {
      await saveSftpSettings(sftpUsername, sftpPassword, sftpPort, sftpHost)
      setMessage('SFTP credentials saved')
    } catch (e) {
      if (e.response) {
        setMessage(e.response.data.message)
      } else {
        setMessage('Failed to save SFTP credentials')
      }
    }
  }

  function getSftp() {
    getSftpSettings().then((data) => {
      setSftpUsername(data.username)
      setSftpPassword(data.password)
      setSftpPort(data.port)
      setSftpHost(data.host)
    }).catch((e) => {
      console.error(e)
    })
  }

  function getIp() {
    getIpData().then((data) => {
      setIpData(data)
    }).catch((e) => {
      console.error(e)
    })
  }

  useEffect(() => {
    getSftp()
    getIp()
  }, []);

  return (
    <section className="user-management">
      <h2>Networking</h2>
      <h3>IP addresses</h3>
      <ul>
        {ipData.map((ip, index) => (
          <li key={index}>{ip}</li>
        ))}
      </ul>
      <div className="simple-form">
        <input
          type="text"
          placeholder="Network ID"
          value={networkId}
          onChange={(e) => setNetworkId(e.target.value)}
        />
        <button onClick={onJoinBtnClick}>Join to ZeroTier network</button>
      </div>
      <p>{message}</p>
      <h2>SFTP (photos transfer)</h2>
      <div className="simple-form">
        <div className={'input-wrapper'}>
          <label>username</label>
          <input
            type="text"
            placeholder="SFTP username"
            value={sftpUsername}
            onChange={(e) => setSftpUsername(e.target.value)}
          />
        </div>
        <div className={'input-wrapper'}>
          <label>password</label>
          <input
            type="text"
            placeholder="SFTP password"
            value={sftpPassword}
            onChange={(e) => setSftpPassword(e.target.value)}
          />
        </div>
        <div className={'input-wrapper'}>
          <label>port</label>
          <input
            type="text"
            placeholder="SFTP port"
            value={sftpPort}
            onChange={(e) => setSftpPort(e.target.value)}
          />
        </div>
        <div className={'input-wrapper'}>
          <label>host</label>
          <input
            type="text"
            placeholder="SFTP host"
            value={sftpHost}
            onChange={(e) => setSftpHost(e.target.value)}
          />
        </div>
        <button onClick={onSaveSftpClick}>Save SFTP credentials</button>
      </div>
    </section>
  )
}
