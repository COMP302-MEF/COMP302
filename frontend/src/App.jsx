import { useState } from 'react'
import { GoogleLogin, googleLogout } from '@react-oauth/google'
import { jwtDecode } from 'jwt-decode'

function App() {
  const [user, setUser] = useState(null)

  const handleSuccess = (credentialResponse) => {
    if (!credentialResponse.credential) return

    const decoded = jwtDecode(credentialResponse.credential)

    setUser({
      name: decoded.name,
      email: decoded.email,
      picture: decoded.picture,
    })
  }

  const handleError = () => {
    console.log('Login failed')
  }

  const handleLogout = () => {
    googleLogout()
    setUser(null)
  }

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial' }}>
      <h1>Google Login Test</h1>

      {!user ? (
        <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
      ) : (
        <div>
          <img
            src={user.picture}
            alt={user.name}
            width="80"
            style={{ borderRadius: '50%' }}
          />
          <h2>{user.name}</h2>
          <p>{user.email}</p>
          <button onClick={handleLogout}>Çıkış Yap</button>
        </div>
      )}
    </div>
  )
}

export default App