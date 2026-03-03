'use client'

import { motion } from 'framer-motion'
import { ShieldAlert, LogIn, UserPlus } from 'lucide-react'
import { login, signup } from './actions'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

function AuthForm() {
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
                <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center shadow-sm">
                    <ShieldAlert className="w-8 h-8 text-blue-600" />
                </div>
            </div>
            <h2 className="text-3xl font-bold text-center text-slate-900 mb-2">Welcome Back</h2>
            <p className="text-center text-slate-500 mb-8">Sign in to access your chat history.</p>

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
                    <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="email">Email Address</label>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        required
                        className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-slate-900"
                        placeholder="you@example.com"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="password">Password</label>
                    <input
                        id="password"
                        name="password"
                        type="password"
                        required
                        className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-slate-900"
                        placeholder="••••••••"
                    />
                </div>

                <div className="flex gap-4 pt-4">
                    <button
                        formAction={login}
                        className="flex-1 bg-slate-900 text-white flex items-center justify-center gap-2 py-3 rounded-xl hover:bg-slate-800 transition-all font-semibold"
                    >
                        <LogIn className="w-4 h-4" /> Sign In
                    </button>
                    <button
                        formAction={signup}
                        className="flex-1 bg-white text-slate-900 border border-slate-200 flex items-center justify-center gap-2 py-3 rounded-xl hover:bg-slate-50 transition-all font-semibold"
                    >
                        <UserPlus className="w-4 h-4" /> Register
                    </button>
                </div>
            </form>
        </motion.div>
    )
}

export default function AuthPage() {
    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
            <Suspense fallback={<div className="w-16 h-16 rounded-full border-4 border-slate-200 border-t-blue-600 animate-spin"></div>}>
                <AuthForm />
            </Suspense>
        </div>
    )
}
