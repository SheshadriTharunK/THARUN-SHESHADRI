import React, { useState } from "react";
import "./App.css";
import Auth from "./components/Auth";
import Dashboard from "./components/Dashboard";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <div className="container">
      <h2>TruthShield AI 🔍</h2>

      {!token ? (
        <Auth setToken={setToken} />
      ) : (
        <Dashboard token={token} logout={logout} />
      )}
    </div>
  );
}

export default App;