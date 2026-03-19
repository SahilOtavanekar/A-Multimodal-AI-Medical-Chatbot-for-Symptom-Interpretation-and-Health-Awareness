'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Lock, CheckCircle2, ShieldAlert, Eye, EyeOff } from 'lucide-react'
import { updatePassword } from '../actions'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

function ResetPasswordForm() {
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const searchParams = useSearchParams()
    const errorMsg = searchParams.get('message')
    const isError = searchParams.get('error') !== 'false'

    return (
        <motion.div
            className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
        >
            <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center shadow-sm text-blue-600">
                    <Lock className="w-8 h-8" />
                </div>
            </div>
            <h2 className="text-3xl font-bold text-center text-slate-900 mb-2">Update Password</h2>
            <p className="text-center text-slate-500 mb-8 px-4">Secure your account with a new password.</p>

            {errorMsg && (
                <div className={`mb-6 p-4 rounded-xl text-sm border flex items-center gap-2 ${isError
                        ? 'bg-red-50 text-red-700 border-red-100'
                        : 'bg-green-50 text-green-700 border-green-100'
                    }`}>
                    <ShieldAlert className="w-4 h-4 shrink-0" />
                    <p>{errorMsg}</p>
                </div>
            )}

            <form className="space-y-5">
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="password">New Password</label>
                    <div className="relative">
                        <input
                            id="password"
                            name="password"
                            type={showPassword ? 'text' : 'password'}
                            required
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-slate-900 pr-11"
                            placeholder="••••••••"
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                    </div>
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="confirmPassword">Confirm New Password</label>
                    <div className="relative">
                        <input
                            id="confirmPassword"
                            name="confirmPassword"
                            type={showConfirmPassword ? 'text' : 'password'}
                            required
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-slate-900 pr-11"
                            placeholder="••••••••"
                        />
                        <button
                            type="button"
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                    </div>
                </div>

                <div className="pt-4">
                    <button
                        formAction={updatePassword}
                        className="w-full bg-slate-900 text-white flex items-center justify-center gap-2 py-3 rounded-xl hover:bg-slate-800 transition-all font-semibold shadow-md"
                    >
                        <CheckCircle2 className="w-4 h-4" /> Save New Password
                    </button>
                </div>
            </form>
        </motion.div>
    )
}

export default function ResetPasswordPage() {
    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
            <Suspense fallback={<div className="w-16 h-16 rounded-full border-4 border-slate-200 border-t-blue-600 animate-spin"></div>}>
                <ResetPasswordForm />
            </Suspense>
        </div>
    )
}
