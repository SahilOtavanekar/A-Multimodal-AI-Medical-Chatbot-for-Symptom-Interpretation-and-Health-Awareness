'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldAlert, LogIn, UserPlus, KeyRound, ArrowLeft, Send, Eye, EyeOff } from 'lucide-react'
import { login, signup, resetPassword } from './actions'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

function AuthError() {
    const searchParams = useSearchParams()
    const errorMsg = searchParams.get('message')
    const isError = searchParams.get('error') !== 'false'

    if (!errorMsg) return null

    return (
        <div className={`mb-6 p-4 rounded-xl text-sm border flex items-center gap-2 ${isError
                ? 'bg-red-50 text-red-700 border-red-100'
                : 'bg-green-50 text-green-700 border-green-100'
            }`}>
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <p>{errorMsg}</p>
        </div>
    )
}

function AuthForm() {
    const [mode, setMode] = useState<'signin' | 'reset'>('signin')
    const [showPassword, setShowPassword] = useState(false)

    return (
        <motion.div
            layout
            className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
        >
            <AnimatePresence mode="wait">
                <motion.div
                    key={mode}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.2 }}
                >
                    <div className="flex justify-center mb-6">
                        <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center shadow-sm">
                            {mode === 'signin' ? <ShieldAlert className="w-8 h-8 text-blue-600" /> : <KeyRound className="w-8 h-8 text-blue-600" />}
                        </div>
                    </div>
                    <h2 className="text-3xl font-bold text-center text-slate-900 mb-2">
                        {mode === 'signin' ? 'Welcome Back' : 'Forgot Password?'}
                    </h2>
                    <p className="text-center text-slate-500 mb-8 px-4">
                        {mode === 'signin' 
                            ? 'Sign in to access your chat history.' 
                            : 'Enter your email and we\'ll send you a secure link to reset your account.'}
                    </p>

                    <Suspense fallback={null}>
                        <AuthError />
                    </Suspense>

                    <form className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="email">Email Address</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                readOnly
                                onFocus={(e) => e.target.readOnly = false}
                                autoComplete="off"
                                defaultValue=""
                                className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-slate-900"
                                placeholder="you@example.com"
                            />
                        </div>

                        {mode === 'signin' && (
                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <label className="block text-sm font-medium text-slate-700" htmlFor="password">Password</label>
                                    <button 
                                        type="button" 
                                        onClick={() => setMode('reset')}
                                        className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                                    >
                                        Forgot Password?
                                    </button>
                                </div>
                                <div className="relative">
                                    <input
                                        id="password"
                                        name="password"
                                        type={showPassword ? 'text' : 'password'}
                                        required
                                        readOnly
                                        onFocus={(e) => e.target.readOnly = false}
                                        autoComplete="off"
                                        defaultValue=""
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
                        )}

                        <div className="flex gap-4 pt-4">
                            {mode === 'signin' ? (
                                <>
                                    <button
                                        formAction={login}
                                        className="flex-1 bg-slate-900 text-white flex items-center justify-center gap-2 py-3 rounded-xl hover:bg-slate-800 transition-all font-semibold shadow-sm"
                                    >
                                        <LogIn className="w-4 h-4" /> Sign In
                                    </button>
                                    <button
                                        formAction={signup}
                                        className="flex-1 bg-white text-slate-900 border border-slate-200 flex items-center justify-center gap-2 py-3 rounded-xl hover:bg-slate-50 transition-all font-semibold"
                                    >
                                        <UserPlus className="w-4 h-4" /> Register
                                    </button>
                                </>
                            ) : (
                                <div className="w-full space-y-3">
                                    <button
                                        formAction={resetPassword}
                                        className="w-full bg-blue-600 text-white flex items-center justify-center gap-2 py-3 rounded-xl hover:bg-blue-700 transition-all font-semibold shadow-md"
                                    >
                                        <Send className="w-4 h-4" /> Send Reset Link
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setMode('signin')}
                                        className="w-full text-slate-500 text-sm font-medium hover:text-slate-800 transition-colors flex items-center justify-center gap-2"
                                    >
                                        <ArrowLeft className="w-4 h-4" /> Back to Sign In
                                    </button>
                                </div>
                            )}
                        </div>
                    </form>
                </motion.div>
            </AnimatePresence>
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
