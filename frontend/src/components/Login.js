import React from 'react';
import { supabase } from '../supabaseClient';

const Login = () => {
  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin
      }
    });
    if (error) console.error('Giriş hatası:', error.message);
  };

  return (
    <div className="login-container">
      <h2>InClass Platform Giriş</h2>
      <button onClick={handleLogin} className="google-btn">
        Google ile Giriş Yap
      </button>
    </div>
  );
};

export default Login;