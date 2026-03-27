import React, { useState } from "react";
import { registerUser, loginUser } from "../api";

function Auth({ setToken }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const register = async () => {
  const data = await registerUser(email, password);
  console.log("data", data);
  if (data.detail) {
    setMessage("❌ " + data.detail);
  } else {
    setMessage("✅ Registered successfully!");
  }
};

  const login = async () => {
  const data = await loginUser(email, password);
  console.log("data", data);

  if (data.detail) {
    setMessage("❌ " + data.detail);
    return;
  }

  setMessage("✅ Login successful!");

  localStorage.setItem("token", data.access_token);
  setToken(data.access_token);
};

  return (
    <>
      <h3>Register / Login</h3>

      <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />

      <button onClick={register}>Register</button>
      <button onClick={login}>Login</button>
          <p>{message}</p>
    </>
  );
}

export default Auth;