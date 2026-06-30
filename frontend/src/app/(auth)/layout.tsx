import { Zap } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="min-h-screen flex flex-col relative overflow-hidden"
      style={{
        backgroundColor: "#f9fafb",
        backgroundImage: `radial-gradient(circle, #d1d5db 1px, transparent 1px)`,
        backgroundSize: "24px 24px",
      }}
    >
      {/* Soft glow blobs */}
      <div
        className="pointer-events-none absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full opacity-30"
        style={{ background: "radial-gradient(circle, #c7d2fe, transparent 70%)" }}
      />
      <div
        className="pointer-events-none absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full opacity-20"
        style={{ background: "radial-gradient(circle, #a5b4fc, transparent 70%)" }}
      />

      {/* Top nav */}
      <header className="relative w-full flex items-center justify-between px-8 py-5">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-indigo-600 rounded-lg flex items-center justify-center shrink-0">
            <Zap className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-semibold text-sm tracking-tight text-gray-800">MeetingTask</span>
        </div>
        <span className="text-xs text-gray-400 hidden sm:block">AI-powered meeting intelligence</span>
      </header>

      {/* Center content */}
      <div className="relative flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">

          {/* Accent line above card */}
          <div className="w-10 h-0.5 bg-indigo-500 rounded-full mx-auto mb-6" />

          {/* Form card */}
          <div
            className="bg-white rounded-2xl border border-gray-200 shadow-lg px-8 py-10 relative"
            style={{ boxShadow: "0 4px 40px -8px rgba(99,102,241,0.12), 0 1px 3px rgba(0,0,0,0.06)" }}
          >
            {/* Top-right corner decoration */}
            <div className="absolute top-0 right-0 w-24 h-24 pointer-events-none">
              <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
                <circle cx="96" cy="0" r="60" stroke="#e0e7ff" strokeWidth="1" fill="none"/>
                <circle cx="96" cy="0" r="40" stroke="#e0e7ff" strokeWidth="1" fill="none"/>
              </svg>
            </div>

            {children}
          </div>

          {/* Dots decoration below card */}
          <div className="flex justify-center gap-1.5 mt-6">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-300" />
            <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
            <div className="w-1.5 h-1.5 rounded-full bg-gray-200" />
          </div>

          {/* Footer */}
          <p className="text-center text-xs text-gray-400 mt-4">
            © 2026 MeetingTask · Built for async teams
          </p>
        </div>
      </div>
    </div>
  );
}
