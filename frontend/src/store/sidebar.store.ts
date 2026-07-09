import { create } from "zustand";

interface SidebarStore {
  open: boolean;         // desktop: expanded vs collapsed
  mobileOpen: boolean;   // mobile: drawer visible vs hidden
  toggle: () => void;
  setOpen: (open: boolean) => void;
  toggleMobile: () => void;
  closeMobile: () => void;
}

export const useSidebarStore = create<SidebarStore>((set) => ({
  open: true,
  mobileOpen: false,
  toggle: () => set((s) => ({ open: !s.open })),
  setOpen: (open) => set({ open }),
  toggleMobile: () => set((s) => ({ mobileOpen: !s.mobileOpen })),
  closeMobile: () => set({ mobileOpen: false }),
}));
