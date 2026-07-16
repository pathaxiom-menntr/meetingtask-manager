"use client";

import { useAuthStore } from "@/store/auth.store";
import { motion } from "framer-motion";
import { User, Mail, Key, Save, Loader2 } from "lucide-react";
import { getInitials } from "@/lib/utils";
import { useState } from "react";
import { toast } from "sonner";
import { usersService } from "@/services/users.service";

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState(user?.full_name ?? "");

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error("Name cannot be empty");
      return;
    }
    setSaving(true);
    try {
      const updated = await usersService.updateProfile({ full_name: name.trim() });
      setUser(updated);
      toast.success("Profile updated!");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);

  const handleUpdatePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error("Please fill in all password fields");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }
    if (newPassword.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setPasswordSaving(true);
    try {
      await usersService.updatePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      toast.success("Password updated successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update password");
    } finally {
      setPasswordSaving(false);
    }
  };

  return (
    <div className="w-full space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground text-sm mt-0.5">Manage your account information</p>
      </motion.div>

      {/* Avatar card */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card border rounded-2xl p-6 flex items-center gap-5"
      >
        <div className="w-16 h-16 bg-indigo-500 rounded-2xl flex items-center justify-center text-white text-xl font-bold">
          {user ? getInitials(user.full_name) : "U"}
        </div>
        <div>
          <p className="font-semibold text-lg">{user?.full_name}</p>
          <p className="text-sm text-muted-foreground">{user?.email}</p>
        </div>
      </motion.div>

      {/* Info form */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-card border rounded-2xl p-6 space-y-5"
      >
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <User className="w-4 h-4 text-indigo-500" /> Personal Information
        </h2>

        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Email Address</label>
            <input
              type="email"
              value={user?.email ?? ""}
              disabled
              className="w-full px-4 py-2.5 rounded-xl border bg-muted text-sm text-muted-foreground cursor-not-allowed"
            />
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl text-sm font-medium transition disabled:opacity-60"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </motion.div>

      {/* Change password */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card border rounded-2xl p-6 space-y-5"
      >
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <Key className="w-4 h-4 text-indigo-500" /> Change Password
        </h2>

        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Current Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">New Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Confirm New Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            />
          </div>
        </div>

        <button 
          onClick={handleUpdatePassword}
          disabled={passwordSaving}
          className="flex items-center gap-2 px-4 py-2.5 border hover:bg-accent rounded-xl text-sm font-medium transition disabled:opacity-60"
        >
          {passwordSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
          {passwordSaving ? "Updating..." : "Update Password"}
        </button>
      </motion.div>
    </div>
  );
}
