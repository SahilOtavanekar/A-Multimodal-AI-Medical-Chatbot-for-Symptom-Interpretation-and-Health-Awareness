'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ShieldAlert, Trash2, ShieldCheck, ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'

export default function ProfilePage() {
    const supabase = createClient()
    const router = useRouter()
    const [userEmail, setUserEmail] = useState<string | null>('Loading...')
    const [isClearing, setIsClearing] = useState(false)

    useEffect(() => {
        const fetchUser = async () => {
            const { data: { user } } = await supabase.auth.getUser()
            setUserEmail(user?.email || 'Unknown')
        }
        fetchUser()
    }, [])

    const handleClearHistory = async () => {
        if (!confirm("Are you absolutely sure you want to delete all chat history and uploaded images? This action cannot be undone.")) {
            return
        }

        setIsClearing(true)
        try {
            const { data: { session } } = await supabase.auth.getSession()
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            const res = await fetch(`${apiUrl}/chat/all`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${session?.access_token}`
                }
            })
            const data = await res.json()
            if (res.ok && data.success) {
                alert("All chat history and data successfully deleted.")
                router.push('/chat')
            } else {
                alert("Failed to clear chat history: " + (data.error || data.detail || "Unknown error"))
            }
        } catch (error) {
            console.error(error)
            alert("Failed to connect to the server to delete history.")
        } finally {
            setIsClearing(false)
        }
    }

    return (
        <div className="min-h-screen bg-slate-50 p-6 md:p-12 font-sans text-slate-900">

            <div className="max-w-3xl mx-auto space-y-8">

                {/* Header */}
                <div className="flex items-center gap-4">
                    <Link href="/chat" className="p-2 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition-colors">
                        <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </Link>
                    <h1 className="text-3xl font-bold tracking-tight">Profile & Privacy Settings</h1>
                </div>

                {/* Privacy Notice */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-blue-50 border border-blue-100 rounded-2xl p-6 shadow-sm flex items-start sm:items-center gap-4 text-blue-800"
                >
                    <ShieldCheck className="w-8 h-8 shrink-0 text-blue-600" />
                    <div>
                        <h3 className="font-bold mb-1">Your Privacy is Protected</h3>
                        <p className="text-sm">We adhere to minimal data retention policies. Your data is <strong>never</strong> used to train our AI models. You have full control over your chat history and uploaded medical images.</p>
                    </div>
                </motion.div>

                {/* Account Details */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm"
                >
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                        Account Details
                    </h2>
                    <div className="space-y-4">
                        <div className="flex justify-between py-3 border-b border-slate-100">
                            <span className="text-sm font-medium text-slate-500">Email Address</span>
                            <span className="font-semibold text-slate-900">{userEmail}</span>
                        </div>
                        <div className="flex justify-between py-3 border-b border-slate-100">
                            <span className="text-sm font-medium text-slate-500">Account Status</span>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Active
                            </span>
                        </div>
                    </div>
                </motion.div>

                {/* Data Controls */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white border border-red-100 rounded-2xl p-6 shadow-sm"
                >
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-red-700">
                        <Trash2 className="w-5 h-5" /> Data Deletion
                    </h2>
                    <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                        You can delete your entire chat history and uploaded images. Once deleted, this information cannot be recovered.
                    </p>
                    <div className="space-y-4">
                        <button
                            onClick={handleClearHistory}
                            disabled={isClearing}
                            className="w-full sm:w-auto px-6 py-3 bg-red-50 text-red-700 font-semibold rounded-xl border border-red-200 hover:bg-red-100 hover:border-red-300 transition-all flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isClearing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                            {isClearing ? "Clearing Data..." : "Clear All Chat History"}
                        </button>
                        <p className="text-xs text-red-600 flex items-center justify-center sm:justify-start gap-1">
                            <ShieldAlert className="w-3 h-3" /> This will permanently erase records from our databases.
                        </p>
                    </div>
                </motion.div>

            </div>
        </div>
    )
}
