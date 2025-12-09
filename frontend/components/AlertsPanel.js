export default function AlertsPanel({ alerts }) {
  return (
    <div className="bg-cardDark rounded-2xl p-4 shadow-md border border-gray-800 h-[480px] flex flex-col">
      <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        Alerts
      </h2>
      <div className="overflow-y-auto space-y-3 text-sm">
        {alerts.length === 0 && (
          <p className="text-gray-500 text-center mt-10">
            No detections yet.
          </p>
        )}
        {alerts.map((a, i) => (
          <div
            key={i}
            className="border border-gray-700 rounded-xl p-3 flex flex-col gap-2"
          >
            <div className="flex justify-between items-center">
              <span className="font-semibold text-white">
                {a.person?.name || "Unknown"}
              </span>
              <span className="text-xs text-gray-400">
                {a.camera_id} • {a.track_id ? `Track #${a.track_id}` : ""}
              </span>
            </div>
            <div className="text-xs text-gray-400">
              <div>Time: {a.timestamp}</div>
              <div>Distance: {a.confidence?.toFixed(3)}</div>
            </div>
            {a.snapshot && (
              <img
                src={`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/snapshots/${a.snapshot}`}
                className="w-full rounded-lg border border-gray-700 mt-1"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
