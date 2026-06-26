export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left: Branding panel */}
      <div className="hidden lg:flex flex-col justify-between relative bg-gradient-to-br from-indigo-600 via-indigo-500 to-violet-600 p-12 text-white overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-white/5 pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-[480px] h-[480px] rounded-full bg-white/5 pointer-events-none" />
        <div className="absolute top-1/2 -translate-y-1/2 right-0 w-64 h-64 rounded-full border border-white/10 pointer-events-none" />
        <div className="absolute top-1/2 -translate-y-1/2 right-[-3rem] w-80 h-80 rounded-full border border-white/10 pointer-events-none" />

        <div className="relative flex items-center gap-2.5">
          <div className="w-9 h-9 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30">
            <span className="text-white font-bold text-sm">M</span>
          </div>
          <span className="font-semibold text-lg">Meeting Task Manager</span>
        </div>

        <div className="relative space-y-6">
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
              { label: "Teams Using", value: "480+" },
              { label: "Avg. Time Saved", value: "2.4 hrs" },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-indigo-200 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        <p className="relative text-indigo-200/80 text-sm">
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
