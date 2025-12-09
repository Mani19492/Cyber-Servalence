import { useEffect, useState } from "react";
import axios from "axios";
import CameraGrid from "../components/CameraGrid";
import AlertsPanel from "../components/AlertsPanel";

const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [alerts, setAlerts] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [ws, setWs] = useState(null);

  const loggedIn = !!token;

  useEffect(() => {
    if (!token) return;

    // fetch cameras (simple - you can secure endpoint)
    axios
      .get(`${BACKEND}/api/cameras`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setCameras(res.data || []))
      .catch(() => setCameras([]));
  }, [token]);

  useEffect(() => {
    if (!token) return;

    const socket = new WebSocket(`${BACKEND.replace("http", "ws")}/ws/alerts`);
    socket.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        if (data.type === "detection") {
          setAlerts((prev) => [data.data, ...prev].slice(0, 100));
        }
      } catch (e) {}
    };
    setWs(socket);
    return () => socket.close();
  }, [token]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);
      const res = await axios.post(`${BACKEND}/auth/login`, form);
      setToken(res.data.access_token);
    } catch (e) {
      alert("Login failed");
    }
  };

  return (
    <div className="min-h-screen p-6 md:p-10">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white">
            Cyber Servalence
          </h1>
          <p className="text-gray-400 text-sm">
            Real-time multi-camera face search & tracking dashboard
          </p>
        </div>
        {!loggedIn ? (
          <form
            onSubmit={handleLogin}
            className="bg-cardDark border border-gray-800 rounded-2xl px-4 py-3 flex flex-col md:flex-row gap-2 items-stretch md:items-end"
          >
            <div className="flex flex-col">
              <label className="text-xs text-gray-400">Email</label>
              <input
                className="bg-gray-900 border border-gray-700 rounded-lg px-2 py-1 text-sm focus:outline-none"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
                required
              />
            </div>
            <div className="flex flex-col">
              <label className="text-xs text-gray-400">Password</label>
              <input
                className="bg-gray-900 border border-gray-700 rounded-lg px-2 py-1 text-sm focus:outline-none"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                required
              />
            </div>
            <button
              type="submit"
              className="bg-accent hover:bg-green-500 text-black font-semibold rounded-lg px-4 py-2 text-sm mt-1 md:mt-0"
            >
              Login
            </button>
          </form>
        ) : (
          <button
            onClick={() => {
              setToken("");
              setAlerts([]);
            }}
            className="text-sm text-gray-300 border border-gray-700 rounded-lg px-3 py-1 hover:bg-gray-800"
          >
            Logout
          </button>
        )}
      </header>

      {!loggedIn ? (
        <div className="mt-10 text-gray-400">
          <p>Login as an operator or admin to view live streams and alerts.</p>
        </div>
      ) : (
        <main className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          <section className="xl:col-span-3">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Live Cameras</h2>
              <span className="text-xs text-gray-500">
                {cameras.length} connected
              </span>
            </div>
            <CameraGrid cameras={cameras} token={token} />
          </section>

          <section className="xl:col-span-1">
            <AlertsPanel alerts={alerts} />
          </section>
        </main>
      )}
    </div>
  );
}
