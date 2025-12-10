import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import CameraGrid from "../components/CameraGrid";
import AlertsPanel from "../components/AlertsPanel";

const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [alerts, setAlerts] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [ws, setWs] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const loggedIn = !!token;

  const fetchCameras = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND}/api/cameras`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setCameras(res.data || []);
    } catch (err) {
      console.error("Failed to fetch cameras:", err);
      setCameras([]);
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [token, fetchCameras]);

  useEffect(() => {
    if (!token) return;

    let socket;
    let reconnectTimeout;
    let shouldReconnect = true;

    const connectWebSocket = () => {
      try {
        const wsUrl = `${BACKEND.replace("http://", "ws://").replace("https://", "wss://")}/ws/alerts`;
        socket = new WebSocket(wsUrl);
        
        socket.onopen = () => {
          console.log("WebSocket connected");
          setError("");
          shouldReconnect = true;
        };
        
        socket.onmessage = (msg) => {
          try {
            const data = JSON.parse(msg.data);
            if (data.type === "detection") {
              setAlerts((prev) => [data.data, ...prev].slice(0, 100));
              // Trigger notification if browser supports it
              if (typeof window !== "undefined" && window.Notification && Notification.permission === "granted") {
                new Notification(`Detection: ${data.data.person?.name || "Unknown"}`, {
                  body: `Detected on camera ${data.data.camera_id}`,
                  icon: "/favicon.ico",
                });
              }
            }
          } catch (e) {
            console.error("Error parsing WebSocket message:", e);
          }
        };
        
        socket.onerror = (err) => {
          console.error("WebSocket error:", err);
          setError("Connection error. Please check if backend is running.");
        };
        
        socket.onclose = () => {
          console.log("WebSocket disconnected");
          if (shouldReconnect && token) {
            // Attempt to reconnect after 3 seconds
            reconnectTimeout = setTimeout(() => {
              connectWebSocket();
            }, 3000);
          }
        };
        
        setWs(socket);
      } catch (err) {
        console.error("Failed to create WebSocket:", err);
        setError("Failed to establish WebSocket connection.");
      }
    };

    connectWebSocket();
    
    // Request notification permission
    if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
    
    return () => {
      shouldReconnect = false;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (socket) socket.close();
    };
  }, [token]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    
    if (!email) {
      setError("Email/username is required");
      setLoading(false);
      return;
    }
    
    try {
      const res = await axios.post(`${BACKEND}/login`, {
        email,
        // No password needed
      });
      setToken(res.data.access_token);
      // Store token in localStorage
      if (typeof window !== "undefined") {
        localStorage.setItem("auth_token", res.data.access_token);
      }
    } catch (e) {
      setError(e.response?.data?.detail || "Login failed. User not found.");
      console.error("Login error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Restore token from localStorage
    if (typeof window !== "undefined") {
      const savedToken = localStorage.getItem("auth_token");
      if (savedToken) {
        setToken(savedToken);
      }
    }
  }, []);

  const handleLogout = () => {
    setToken("");
    setAlerts([]);
    setCameras([]);
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
    if (ws) {
      ws.close();
      setWs(null);
    }
  };

  return (
    <div className="min-h-screen p-6 md:p-10 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-1 flex items-center gap-2">
            <span className="text-green-400">🔒</span>
            Cyber Servalence
          </h1>
          <p className="text-gray-400 text-sm">
            Real-time multi-camera face search & tracking dashboard
          </p>
        </div>
        {!loggedIn ? (
          <form
            onSubmit={handleLogin}
            className="bg-cardDark border border-gray-800 rounded-2xl px-4 py-3 flex flex-col md:flex-row gap-3 items-stretch md:items-end shadow-lg w-full md:w-auto"
          >
            <div className="flex flex-col">
              <label className="text-xs text-gray-400 mb-1">Email / Username</label>
              <input
                className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition-all text-white"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="text"
                placeholder="admin@cyber.com"
                required
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-black font-semibold rounded-lg px-6 py-2 text-sm transition-all transform hover:scale-105 active:scale-95 shadow-lg"
            >
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>
        ) : (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${ws?.readyState === WebSocket.OPEN ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-xs text-gray-400">
                {ws?.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-300 border border-gray-700 rounded-lg px-4 py-2 hover:bg-gray-800 transition-all hover:border-red-500 hover:text-red-400"
            >
              Logout
            </button>
            <button
              onClick={() => {
                setRefreshKey(prev => prev + 1);
                fetchCameras();
              }}
              className="text-sm text-gray-300 border border-gray-700 rounded-lg px-4 py-2 hover:bg-gray-800 transition-all"
              title="Refresh cameras"
            >
              🔄
            </button>
          </div>
        )}
      </header>

      {error && (
        <div className="mb-4 bg-red-900/30 border border-red-500 rounded-lg px-4 py-3 text-red-300 text-sm animate-pulse">
          {error}
        </div>
      )}

      {!loggedIn ? (
        <div className="mt-20 flex flex-col items-center justify-center text-center">
          <div className="bg-cardDark border border-gray-800 rounded-2xl p-8 max-w-md shadow-2xl">
            <div className="text-6xl mb-4">👁️</div>
            <h2 className="text-xl font-semibold text-white mb-2">Welcome to Cyber Servalence</h2>
            <p className="text-gray-400 text-sm mb-6">
              Login as an operator or admin to view live camera streams and real-time alerts.
            </p>
            <div className="text-xs text-gray-500">
              <p>Login with email:</p>
              <p className="mt-2 font-mono">admin@cyber.com</p>
              <p className="mt-1 text-gray-600">(No password required)</p>
            </div>
          </div>
        </div>
      ) : (
        <main className="grid grid-cols-1 xl:grid-cols-4 gap-6 animate-fadeIn">
          <section className="xl:col-span-3">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                Live Cameras
              </h2>
              <span className="text-xs text-gray-500 bg-gray-800 px-3 py-1 rounded-full">
                {cameras.length} {cameras.length === 1 ? 'camera' : 'cameras'} connected
              </span>
            </div>
            <CameraGrid key={refreshKey} cameras={cameras} token={token} />
          </section>

          <section className="xl:col-span-1">
            <AlertsPanel alerts={alerts} />
          </section>
        </main>
      )}
    </div>
  );
}
