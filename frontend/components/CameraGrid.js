export default function CameraGrid({ cameras, token }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mt-4">
      {cameras.map((cam) => (
        <div
          key={cam.id}
          className="bg-cardDark rounded-2xl p-3 shadow-md border border-gray-800"
        >
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-white">
              {cam.location || "Camera"} — {cam.id}
            </h3>
            <span className="text-xs text-gray-400">Live</span>
          </div>
          <div className="overflow-hidden rounded-xl border border-gray-700">
            <img
              src={`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/stream/${cam.id}?token=${token}`}
              alt={cam.id}
              className="w-full h-56 object-cover"
            />
          </div>
        </div>
      ))}
    </div>
  );
}
