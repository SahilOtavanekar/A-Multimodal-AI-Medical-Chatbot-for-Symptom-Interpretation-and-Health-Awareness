'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { AlertCircle, ShieldAlert, Activity, ArrowRight } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100 selection:text-blue-900">

      {/* Strict Medical Disclaimer Header */}
      <div className="bg-red-50 border-b border-red-100 px-4 py-3 flex items-start sm:items-center justify-center gap-3 text-red-800 text-sm font-medium">
        <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5 sm:mt-0 text-red-600" />
        <p>
          <strong>MEDICAL DISCLAIMER:</strong> This is a health awareness tool. It does <strong>NOT</strong> provide medical diagnoses or treatment recommendations. Always consult a qualified healthcare professional in medical emergencies.
        </p>
      </div>

      <main className="max-w-5xl mx-auto px-6 py-20 flex flex-col items-center justify-center text-center">

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-sm font-semibold mb-8"
        >
          <Activity className="w-4 h-4" />
          <span>AI-Powered Health Awareness</span>
        </motion.div>

        <motion.h1
          className="text-5xl sm:text-7xl font-bold tracking-tight text-slate-900 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Understand your symptoms with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Multimodal AI.</span>
        </motion.h1>

        <motion.p
          className="text-lg sm:text-xl text-slate-600 max-w-2xl mb-10 leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Upload images of visual symptoms or medical reports, combined with text descriptions, to receive accurate, education-focused health insights backed by leading generative AI.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Link
            href="/auth"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/30 hover:bg-blue-700 hover:-translate-y-0.5 transition-all focus:ring-4 focus:ring-blue-100"
          >
            Get Started <ArrowRight className="w-5 h-5" />
          </Link>
          <button
            onClick={(e) => {
              e.preventDefault();
              document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }}
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-slate-700 rounded-xl font-semibold shadow-sm border border-slate-200 hover:bg-slate-50 transition-all focus:ring-4 focus:ring-slate-100 cursor-pointer"
          >
            Learn More
          </button>
        </motion.div>

        {/* Feature Highlights */}
        <section id="how-it-works" className="w-full mt-48 pt-12">
          <motion.div
            className="grid sm:grid-cols-3 gap-8 text-left"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Multimodal Analysis</h3>
            <p className="text-slate-600 leading-relaxed">Combine images and context text to get a comprehensive understanding of your symptoms.</p>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Safety First Architecture</h3>
            <p className="text-slate-600 leading-relaxed">Built with strict ethical guardrails and emergency escalation logic to ensure user safety.</p>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">HIPAA-Grade Privacy</h3>
            <p className="text-slate-600 leading-relaxed">Your data belongs to you. We strictly enforce deletion policies and guarantee no AI training on user data.</p>
          </div>
        </motion.div>
      </section>

      </main>

      <footer className="py-16 pb-64 text-center text-slate-500 text-sm border-t border-slate-200 mt-24 bg-white">
        <p>&copy; {new Date().getFullYear()} Health AI. All rights reserved. For educational purposes only.</p>
      </footer>
    </div>
  )
}
