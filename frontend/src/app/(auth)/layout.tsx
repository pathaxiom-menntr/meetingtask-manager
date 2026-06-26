export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left: Branding panel */}
      <div className="hidden lg:flex flex-col justify-between bg-[#6366F1] p-12 text-white">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">M</span>
          </div>
          <span className="font-semibold text-lg">Meeting Task Manager</span>
        </div>

        <div className="space-y-6">
          <h1 className="text-4xl font-bold leading-tight">
            Turn meetings into<br />action, automatically.
          </h1>
          <p className="text-indigo-100 text-lg leading-relaxed">
            Upload your meeting transcript and let AI extract every task, assign it, and track it — so nothing falls through the cracks.
          </p>

          <div className="grid grid-cols-2 gap-4 pt-4">
            {[
              { label: "Tasks Generated", value: "12,400+" },
              { label: "Meetings Processed", value: "3,200+" },
              { label: "Teams Using Meeting Task Manager", value: "480+" },
              { label: "Avg. Time Saved", value: "2.4 hrs" },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/10 rounded-xl p-4">
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-indigo-200 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-indigo-200 text-sm">
          © 2026 Meeting Task Manager. Built for async teams.
        </p>
      </div>

      {/* Right: Form area */}
      <div className="flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
