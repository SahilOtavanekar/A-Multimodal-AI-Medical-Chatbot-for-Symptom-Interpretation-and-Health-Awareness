'use client'

import { useState, useRef, useEffect, useCallback, Suspense } from 'react'
import { motion } from 'framer-motion'
import { Send, ImagePlus, User, Bot, Loader2, LogOut, Settings, MessageSquare, PlusCircle, Volume2, Pause, Play, Menu, X, Mic, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/utils/supabase/client'
import ReactMarkdown from 'react-markdown'

function DeletionNotifier() {
    const searchParams = useSearchParams()
    const [deletionSuccess, setDeletionSuccess] = useState(false)

    useEffect(() => {
        if (searchParams.get('deleted') === 'true') {
            setDeletionSuccess(true)
            window.history.replaceState({}, '', '/chat')
            const timer = setTimeout(() => setDeletionSuccess(false), 5000)
            return () => clearTimeout(timer)
        }
    }, [searchParams])

    if (!deletionSuccess) return null

    return (
        <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-20 left-1/2 -translate-x-1/2 z-50 bg-green-50 border border-green-200 text-green-800 px-6 py-3 rounded-2xl shadow-lg flex items-center gap-3 font-semibold"
        >
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            All chat history successfully deleted!
        </motion.div>
    )
}

function ChatInterface() {
    const supabase = createClient()
    const [messages, setMessages] = useState<any[]>([
        { id: 1, role: 'assistant', text: "Hello. I am a health awareness AI. How can I help you today? Please remember, I cannot provide a medical diagnosis." }
    ])
    const [input, setInput] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [sessions, setSessions] = useState<any[]>([])
    const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)
    const [isUploading, setIsUploading] = useState(false)
    const [isSidebarOpen, setIsSidebarOpen] = useState(false)
    const [speakingId, setSpeakingId] = useState<number | null>(null)
    const [isPaused, setIsPaused] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const recognitionRef = useRef<any>(null)

    const fetchSessions = useCallback(async () => {
        try {
            const { data: { session } } = await supabase.auth.getSession()
            if (!session) return

            const isProd = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
            const apiPrefix = '/api'
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (isProd ? '' : 'http://localhost:8000')
            const res = await fetch(`${apiUrl}${apiPrefix}/chat/sessions`, {
                headers: { 'Authorization': `Bearer ${session.access_token}` }
            })
            const data = await res.json()
            if (data.success) {
                setSessions(data.data)
            }
        } catch (error) {
            console.error("Failed to fetch sessions:", error)
        }
    }, [supabase])

    useEffect(() => {
        fetchSessions()
    }, [fetchSessions])

    const loadSession = async (sid: string) => {
        try {
            const { data: { session } } = await supabase.auth.getSession()
            if (!session) return

            const isProd = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
            const apiPrefix = '/api'
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (isProd ? '' : 'http://localhost:8000')

            const res = await fetch(`${apiUrl}${apiPrefix}/chat/history?session_id=${sid}`, {
                headers: { 'Authorization': `Bearer ${session.access_token}` }
            })
            const data = await res.json()
            if (data.success) {
                setSessionId(sid)
                setMessages(data.data) // Assuming data.data holds the messages sorted chronologically
            }
        } catch (error) {
            console.error("Failed to load session history:", error)
        }
    }

    const startNewChat = () => {
        setSessionId(null)
        setMessages([
            { id: 1, role: 'assistant', text: "Hello. I am a health awareness AI. How can I help you today? Please remember, I cannot provide a medical diagnosis." }
        ])
    }

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() && !uploadedImageUrl) return

        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false);
        }

        const currentInput = input
        const currentImageUrl = uploadedImageUrl
        const newMsg = { id: Date.now(), role: 'user', text: currentInput, image_url: currentImageUrl }
        setMessages(prev => [...prev, newMsg])
        setInput('')
        setUploadedImageUrl(null)
        setIsTyping(true)

        try {
            const { data: { session } } = await supabase.auth.getSession()
            const isProd = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
            const apiPrefix = '/api'
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (isProd ? '' : 'http://localhost:8000')
            const res = await fetch(`${apiUrl}${apiPrefix}/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session?.access_token}`
                },
                body: JSON.stringify({
                    message: currentInput || 'See attached image.',
                    session_id: sessionId,
                    image_url: currentImageUrl
                })
            })
            const data = await res.json()
            if (data.success) {
                if (!sessionId && data.data.session_id) {
                    // Refresh the session list strictly if it's the first message of a new thread
                    fetchSessions()
                }
                setSessionId(data.data.session_id)
                setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: data.data.response }])
            } else {
                setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: "Error: " + (data.error || data.detail) }])
            }
        } catch (error: any) {
            console.error(error)
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: "Failed to connect to the backend server." }])
        } finally {
            setIsTyping(false)
        }
    }


    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setIsUploading(true)
        try {
            const { data: { session } } = await supabase.auth.getSession()
            const isProd = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
            const apiPrefix = '/api'
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (isProd ? '' : 'http://localhost:8000')

            const formData = new FormData()
            formData.append('file', file)

            const res = await fetch(`${apiUrl}${apiPrefix}/upload/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session?.access_token}`
                },
                body: formData
            })
            const data = await res.json()
            if (data.success) {
                setUploadedImageUrl(data.data.url)
            } else {
                alert("Upload failed: " + (data.error || data.detail))
            }
        } catch (error) {
            console.error(error)
            alert("Failed to upload image.")
        } finally {
            setIsUploading(false)
        }
    }

    const toggleSpeechToText = () => {
        if (isListening) {
            if (recognitionRef.current) recognitionRef.current.stop();
            setIsListening(false);
            return;
        }

        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Voice input is not supported in this browser. Please use Chrome or Edge.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;
        recognition.lang = 'en-US';
        recognition.interimResults = true;
        recognition.continuous = true;

        const baseInput = input ? input.trim() + " " : "";

        recognition.onstart = () => setIsListening(true);
        
        recognition.onresult = (event: any) => {
            const transcript = Array.from(event.results)
                .map((result: any) => result[0].transcript)
                .join('');
            setInput(baseInput + transcript); 
        };

        recognition.onerror = (e: any) => {
            console.error("Speech recognition error", e);
            if (e.error !== 'no-speech') setIsListening(false);
        };

        recognition.onend = () => setIsListening(false);
        
        recognition.start();
    };

    const chunkText = (text: string, maxLength: number = 150): string[] => {
        // Strip out basic markdown syntax to avoid speech engine breaking on *, #, etc.
        const cleanText = text.replace(/[*#`_]/g, '');
        const chunks: string[] = [];
        let currentChunk = "";
        const words = cleanText.split(" ");

        for (const word of words) {
            if (currentChunk.length + word.length + 1 <= maxLength) {
                currentChunk += (currentChunk ? " " : "") + word;
            } else {
                chunks.push(currentChunk);
                currentChunk = word;
            }
        }
        if (currentChunk) chunks.push(currentChunk);
        return chunks;
    };

    const handleSpeak = (msgId: number, text: string) => {
        if (!('speechSynthesis' in window)) {
            alert("Text-to-speech is not supported in your browser.")
            return
        }

        // Handle pause/resume for the same message
        if (speakingId === msgId) {
            if (isPaused) {
                window.speechSynthesis.resume()
                setIsPaused(false)
            } else {
                window.speechSynthesis.pause()
                setIsPaused(true)
            }
            return
        }

        // Cancel previous speech completely
        window.speechSynthesis.cancel()
        setSpeakingId(msgId)
        setIsPaused(false)

        setTimeout(() => {
            const chunks = chunkText(text)
            const isHindi = /[\u0900-\u097F]/.test(text)
            let currentIndex = 0;

            const speakNextChunk = () => {
                if (currentIndex >= chunks.length) {
                    setSpeakingId(null)
                        ; (window as any)._activeUtterance = null
                    return;
                }

                const utterance = new SpeechSynthesisUtterance(chunks[currentIndex])
                    // Global reference guard
                    ; (window as any)._activeUtterance = utterance

                utterance.lang = isHindi ? 'hi-IN' : 'en-US'

                const voices = window.speechSynthesis.getVoices()
                if (voices.length > 0) {
                    const targetLang = isHindi ? 'hi' : 'en'
                    // Find a specific named voice or fallback by prefix
                    const targetVoice = voices.find(v => v.lang.startsWith(targetLang) || v.lang.startsWith(targetLang.toUpperCase()))
                    if (targetVoice) utterance.voice = targetVoice
                }

                utterance.onend = () => {
                    currentIndex++;
                    speakNextChunk(); // Chain the next chunk recursively
                }

                utterance.onerror = (e) => {
                    console.error("SpeechSynthesis error on chunk:", e)
                    // If error is silent {}, it was likely GC or text length limit. Skip to next chunk.
                    currentIndex++;
                    if (e.error !== 'interrupted' && e.error !== 'canceled') {
                        speakNextChunk();
                    } else {
                        // User genuinely canceled/shifted
                        setSpeakingId(null)
                        setIsPaused(false)
                            ; (window as any)._activeUtterance = null
                    }
                }

                window.speechSynthesis.speak(utterance)
            }

            // Fire the first chunk
            speakNextChunk()

        }, 100) // Slightly longer 100ms yield to clear out the Audio Context
    }

    return (
        <div className="flex h-full w-full relative">
            {/* Mobile Sidebar Overlay */}
            {isSidebarOpen && (
                <div
                    className="absolute inset-0 bg-slate-900/50 z-40 sm:hidden transition-opacity"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`absolute sm:static inset-y-0 left-0 z-50 flex flex-col w-64 bg-white border-r border-slate-200 p-4 shrink-0 transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full sm:translate-x-0'}`}>
                <div className="flex items-center justify-between mb-8 px-2">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">M</div>
                        <span className="font-semibold text-slate-800">Health AI</span>
                    </div>
                    <button onClick={() => setIsSidebarOpen(false)} className="sm:hidden p-1 text-slate-400 hover:text-slate-600 transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto space-y-1">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 mb-2">History</p>

                    <button
                        onClick={() => { startNewChat(); setIsSidebarOpen(false); }}
                        className={`w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg font-medium transition-colors ${!sessionId ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'}`}
                    >
                        <PlusCircle className="w-4 h-4" /> New Chat
                    </button>

                    <div className="pt-2 space-y-1">
                        {sessions.map((session) => (
                            <button
                                key={session.id}
                                onClick={() => { loadSession(session.id); setIsSidebarOpen(false); }}
                                className={`w-full text-left flex items-center gap-2 px-3 py-2 text-sm rounded-lg font-medium transition-colors truncate ${sessionId === session.id ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'}`}
                            >
                                <MessageSquare className="w-4 h-4 shrink-0" />
                                <span className="truncate">{session.title || 'Untitled Session'}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="mt-auto border-t border-slate-100 pt-4 space-y-1">
                    <Link href="/profile" className="flex items-center gap-3 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-lg transition-colors">
                        <Settings className="w-4 h-4" /> Profile & Data
                    </Link>
                    <Link 
                        href="/auth/signout"
                        className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 hover:bg-red-50 hover:text-red-700 rounded-lg transition-colors"
                    >
                        <LogOut className="w-4 h-4" /> Sign Out
                    </Link>
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col min-w-0 bg-white md:rounded-l-[2.5rem] shadow-2xl relative overflow-hidden">
                <Suspense fallback={null}>
                    <DeletionNotifier />
                </Suspense>

                {/* Mobile Header */}
                <header className="sm:hidden bg-white border-b border-slate-200 p-4 flex items-center justify-between shrink-0 sticky top-0 z-10">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div>
                        <span className="font-semibold text-slate-800">Health AI</span>
                    </div>
                    <button onClick={() => setIsSidebarOpen(true)} className="p-2 -mr-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
                        <Menu className="w-5 h-5" />
                    </button>
                </header>

                <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex gap-4 max-w-3xl mx-auto w-full ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            <div className={`w-10 h-10 shrink-0 rounded-full flex items-center justify-center shadow-sm border ${msg.role === 'user' ? 'bg-blue-600 border-blue-700 text-white' : 'bg-white border-slate-200 text-blue-600'}`}>
                                {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                            </div>
                            <div className={`px-5 py-3.5 rounded-2xl shadow-sm text-[15px] leading-relaxed ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-white text-slate-800 border border-slate-100 rounded-tl-sm'}`}>
                                {msg.image_url && (
                                    <div className="mb-2">
                                        <img src={msg.image_url} alt="Uploaded attachment" className="max-w-[200px] rounded-lg" />
                                    </div>
                                )}
                                {msg.role === 'assistant' ? (
                                    <div className="flex flex-col">
                                        <div className="markdown-body text-slate-800">
                                            <ReactMarkdown>{msg.text || msg.content}</ReactMarkdown>
                                        </div>
                                        <div className="mt-3 pt-2 border-t border-slate-100 flex justify-end">
                                            <button
                                                onClick={() => handleSpeak(msg.id, msg.text || msg.content)}
                                                className={`flex items-center gap-1.5 text-xs font-medium transition-colors ${speakingId === msg.id ? 'text-blue-600' : 'text-slate-400 hover:text-blue-600'}`}
                                                title={speakingId === msg.id ? (isPaused ? "Resume reading" : "Pause reading") : "Read response aloud"}
                                            >
                                                {speakingId === msg.id ? (
                                                    isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />
                                                ) : (
                                                    <Volume2 className="w-4 h-4" />
                                                )}
                                                <span>{speakingId === msg.id ? (isPaused ? "Resume" : "Pause") : "Read Aloud"}</span>
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <span className="whitespace-pre-wrap">{msg.text || msg.content}</span>
                                )}
                            </div>
                        </motion.div>
                    ))}
                    {isTyping && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex gap-4 max-w-3xl mx-auto w-full"
                        >
                            <div className="w-10 h-10 shrink-0 rounded-full flex items-center justify-center shadow-sm border bg-white border-slate-200 text-slate-400">
                                <Loader2 className="w-5 h-5 animate-spin" />
                            </div>
                        </motion.div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-4 bg-white border-t border-slate-200 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)]">
                    <form onSubmit={handleSend} className="max-w-3xl mx-auto relative flex flex-col gap-2">
                        {/* Image Preview Area */}
                        {uploadedImageUrl && (
                            <div className="relative inline-block self-start ml-14 mb-2">
                                <img src={uploadedImageUrl} alt="Attachment preview" className="h-20 rounded-lg border border-slate-200 shadow-sm" />
                                <button type="button" onClick={() => setUploadedImageUrl(null)} className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-md hover:bg-red-600 transition-colors">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
                                </button>
                            </div>
                        )}
                        <div className="relative flex items-center">
                            <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/png, image/jpeg, image/jpg, image/webp" />
                            <button type="button" onClick={() => fileInputRef.current?.click()} disabled={isUploading} className={`absolute left-3 p-2 rounded-full transition-colors shrink-0 disabled:opacity-50 ${uploadedImageUrl ? 'text-blue-600 bg-blue-100' : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'}`}>
                                {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ImagePlus className="w-5 h-5" />}
                            </button>
                            
                            <button 
                                type="button" 
                                onClick={toggleSpeechToText}
                                disabled={isUploading}
                                className={`absolute left-12 p-2 rounded-full transition-colors shrink-0 disabled:opacity-50 ${isListening ? 'text-red-500 bg-red-50 animate-pulse' : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'}`}
                                title="Use Voice Typing"
                            >
                                <Mic className="w-5 h-5" />
                            </button>

                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={isUploading ? "Uploading image..." : (isListening ? "Listening... (Speak now)" : "Describe your symptoms or ask a health question...")}
                                disabled={isUploading}
                                className="w-full pl-24 pr-14 py-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white text-slate-900 transition-all placeholder:text-slate-400 disabled:opacity-70"
                            />
                            <button
                                type="submit"
                                disabled={(!input.trim() && !uploadedImageUrl) || isUploading}
                                className="absolute right-3 p-2 text-blue-600 hover:bg-blue-50 rounded-full transition-colors shrink-0 disabled:opacity-40 disabled:hover:bg-transparent"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </form>
                    <p className="text-center text-xs text-slate-400 mt-3 font-medium">Use of this system implies agreement to the Medical Disclaimer.</p>
                </div>
            </main>
        </div>
    )
}

export default function ChatPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center h-screen w-full bg-slate-50">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
        }>
            <ChatInterface />
        </Suspense>
    )
}
