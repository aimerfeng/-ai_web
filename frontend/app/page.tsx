"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Sparkles, ArrowRight } from "lucide-react"
import { Button } from "@/app/components/ui/button"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center aurora-bg relative overflow-hidden p-4">
      
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <motion.div 
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
            opacity: [0.3, 0.5, 0.3] 
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary-200/30 to-accent-200/30 blur-3xl rounded-full"
        />
        <motion.div 
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, -60, 0],
            opacity: [0.2, 0.4, 0.2] 
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-accent-200/30 to-primary-200/30 blur-3xl rounded-full"
        />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto text-center space-y-8">
        
        {/* Logo / Icon */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mx-auto w-20 h-20 glass rounded-3xl flex items-center justify-center shadow-xl mb-8"
        >
          <Sparkles className="w-10 h-10 text-primary-500" />
        </motion.div>

        {/* Headlines */}
        <div className="space-y-4">
          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-5xl md:text-7xl font-serif font-bold tracking-tight bg-gradient-to-r from-primary-600 via-primary-500 to-accent-500 bg-clip-text text-transparent"
          >
            SkinTech AI
          </motion.h1>
          <motion.p 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl md:text-2xl text-gray-600 font-light max-w-2xl mx-auto leading-relaxed"
          >
            Your intelligent cosmetic chemist. <br/>
            Personalized analysis, scientific recommendations, real-time advice.
          </motion.p>
        </div>

        {/* CTA Buttons */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8"
        >
          <Link href="/auth/register">
            <Button size="lg" className="rounded-full px-8 text-lg h-14 shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
              Get Started <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
          <Link href="/auth/login">
            <Button variant="ghost" size="lg" className="rounded-full px-8 text-lg h-14 hover:bg-white/50">
              Sign In
            </Button>
          </Link>
        </motion.div>

        {/* Features Grid */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 text-left"
        >
          {[
            { title: "Smart Analysis", desc: "AI-driven skin type & concern detection based on your chat." },
            { title: "Ingredient Check", desc: "Deep dive into product formulations and safety warnings." },
            { title: "Routine Builder", desc: "Customized AM/PM routines that fit your budget and lifestyle." }
          ].map((item, i) => (
            <div key={i} className="glass p-6 rounded-2xl border-white/40 hover:bg-white/40 transition-colors">
              <h3 className="font-semibold text-primary-700 mb-2">{item.title}</h3>
              <p className="text-sm text-gray-500">{item.desc}</p>
            </div>
          ))}
        </motion.div>
      </div>
      
      <div className="absolute bottom-4 text-xs text-gray-400">
        © 2026 SkinTech AI Consultant
      </div>
    </div>
  )
}
