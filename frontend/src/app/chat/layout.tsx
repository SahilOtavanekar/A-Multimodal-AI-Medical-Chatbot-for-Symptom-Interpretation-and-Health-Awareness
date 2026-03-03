import { ShieldAlert } from 'lucide-react'

export default function ChatLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex flex-col h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100 selection:text-blue-900">
            <div className="bg-red-50 border-b border-red-100 px-4 py-2 flex items-start sm:items-center justify-center gap-2 text-red-800 text-xs sm:text-sm font-medium shrink-0 z-10 w-full shadow-sm">
                <ShieldAlert className="w-4 h-4 mb-0.5 sm:mb-0 shrink-0 text-red-600" />
                <p>
                    <strong>MEDICAL DISCLAIMER:</strong> This AI tool is for health awareness only. It <strong>CANNOT</strong> diagnose conditions, prescribe treatments, or replace professional medical advice.
                </p>
            </div>
            <div className="flex-1 overflow-hidden flex flex-col sm:flex-row relative">
                {children}
            </div>
        </div>
    )
}
