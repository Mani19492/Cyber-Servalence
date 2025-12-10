import { useState, useEffect } from "react";

export default function AlertsPanel({ alerts }) {
  const [selectedAlert, setSelectedAlert] = useState(null);

  const formatTime = (timestamp) => {
    if (!timestamp) return "Unknown";
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence < 0.2) return "text-green-400";
    if (confidence < 0.3) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="bg-cardDark rounded-2xl p-4 shadow-lg border border-gray-800 h-[600px] flex flex-col">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
          <span className={`w-2 h-2 rounded-full ${alerts.length > 0 ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`} />
          Alerts
          {alerts.length > 0 && (
            <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded-full">
              {alerts.length}
            </span>
          )}
        </h2>
        {alerts.length > 0 && (
          <button
            onClick={() => setSelectedAlert(null)}
            className="text-xs text-gray-400 hover:text-white transition-all"
          >
            Clear
          </button>
        )}
      </div>
      <div className="overflow-y-auto space-y-3 text-sm flex-1 pr-2 custom-scrollbar">
        {alerts.length === 0 && (
          <div className="text-center mt-10">
            <div className="text-4xl mb-3">🔍</div>
            <p className="text-gray-500">No detections yet.</p>
            <p className="text-xs text-gray-600 mt-2">
              Alerts will appear here in real-time
            </p>
          </div>
        )}
        {alerts.map((a, i) => {
          const isNew = i === 0;
          const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
          
          return (
            <div
              key={i}
              className={`border rounded-xl p-3 flex flex-col gap-2 transition-all cursor-pointer hover:border-green-500/50 ${
                isNew ? 'border-green-500/50 bg-green-500/5 animate-slideIn' : 'border-gray-700'
              } ${selectedAlert === i ? 'ring-2 ring-green-500' : ''}`}
              onClick={() => setSelectedAlert(selectedAlert === i ? null : i)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <span className="font-semibold text-white text-base flex items-center gap-2">
                    {a.person?.name || "Unknown Person"}
                    {isNew && <span className="text-xs bg-red-500 text-white px-1.5 py-0.5 rounded animate-pulse">NEW</span>}
                  </span>
                  <div className="text-xs text-gray-400 mt-1">
                    Camera: {a.camera_id || "Unknown"}
                  </div>
                </div>
                {a.track_id && (
                  <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">
                    #{a.track_id}
                  </span>
                )}
              </div>
              
              <div className="text-xs text-gray-400 space-y-1">
                <div className="flex items-center gap-2">
                  <span>🕐</span>
                  <span>{formatTime(a.timestamp)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>📊</span>
                  <span className={getConfidenceColor(a.confidence)}>
                    Confidence: {(1 - (a.confidence || 0)).toFixed(1)}%
                  </span>
                  <span className="text-gray-600">
                    (dist: {a.confidence?.toFixed(3)})
                  </span>
                </div>
              </div>

              {a.snapshot && (
                <div className="mt-2 rounded-lg overflow-hidden border border-gray-700">
                  <img
                    src={`${baseUrl}/snapshots/${a.snapshot}`}
                    alt="Detection snapshot"
                    className="w-full h-auto object-contain bg-black"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}

              {selectedAlert === i && (
                <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-gray-400">
                  <div className="grid grid-cols-2 gap-2">
                    <div>Camera ID:</div>
                    <div className="text-white">{a.camera_id}</div>
                    <div>Timestamp:</div>
                    <div className="text-white">{a.timestamp}</div>
                    <div>Confidence:</div>
                    <div className={getConfidenceColor(a.confidence)}>
                      {a.confidence?.toFixed(4)}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
