import { useState } from "react";

export default function CameraGrid({ cameras, token }) {
  const [fullscreen, setFullscreen] = useState(null);

  if (cameras.length === 0) {
    return (
      <div className="bg-cardDark rounded-2xl p-12 border border-gray-800 text-center">
        <div className="text-5xl mb-4">📹</div>
        <p className="text-gray-400 mb-2">No cameras connected</p>
        <p className="text-sm text-gray-500">Add cameras through the API to see live feeds</p>
      </div>
    );
  }

  const streamUrl = (camId) => {
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    return `${baseUrl}/stream/${camId}?t=${Date.now()}`; // Add timestamp to prevent caching
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mt-4">
        {cameras.map((cam) => {
          const camId = cam.id || cam.name || `camera-${cameras.indexOf(cam)}`;
          const camName = cam.location || cam.name || `Camera ${camId}`;
          
          return (
            <div
              key={camId}
              className="bg-cardDark rounded-2xl p-3 shadow-lg border border-gray-800 hover:border-green-500/50 transition-all duration-300 group"
            >
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  {camName}
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">Live</span>
                  <button
                    onClick={() => setFullscreen(camId)}
                    className="text-gray-400 hover:text-white transition-all opacity-0 group-hover:opacity-100"
                    title="Fullscreen"
                  >
                    ⛶
                  </button>
                </div>
              </div>
              <div className="overflow-hidden rounded-xl border border-gray-700 relative bg-black">
                <div className="relative w-full h-56 overflow-hidden">
                  <img
                    src={streamUrl(camId)}
                    alt={camId}
                    className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
                    onError={(e) => {
                      e.target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='480'%3E%3Crect fill='%23111111' width='640' height='480'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%23666' font-size='20'%3EWaiting for feed...%3C/text%3E%3C/svg%3E`;
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                ID: {camId}
              </div>
            </div>
          );
        })}
      </div>

      {fullscreen && (
        <div
          className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4"
          onClick={() => setFullscreen(null)}
        >
          <div className="relative w-full h-full max-w-7xl">
            <button
              onClick={() => setFullscreen(null)}
              className="absolute top-4 right-4 text-white bg-gray-800 hover:bg-gray-700 rounded-full p-3 z-10 transition-all"
            >
              ✕
            </button>
            <img
              src={streamUrl(fullscreen)}
              alt={fullscreen}
              className="w-full h-full object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </>
  );
}
