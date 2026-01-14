"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Sparkles } from "lucide-react"
import { Button } from "@/app/components/ui/button"
import { motion } from "framer-motion"

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!input.trim() || isLoading) return
    onSend(input)
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [input])

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-6">
      <motion.div 
        className="relative glass rounded-[2rem] p-2 shadow-xl flex items-end gap-2"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="flex-1 min-h-[50px] relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="向 SkinTech 咨询护肤问题..."
            className="w-full bg-transparent border-none focus:ring-0 resize-none py-3 px-4 max-h-[200px] scrollbar-hide text-base placeholder:text-gray-400"
            rows={1}
            disabled={isLoading}
          />
        </div>

        <Button 
          size="icon" 
          onClick={() => handleSubmit()} 
          disabled={!input.trim() || isLoading}
          className="rounded-full w-10 h-10 mb-1 shrink-0 bg-gradient-to-tr from-primary-500 to-accent-400 hover:scale-105 transition-transform"
        >
          {isLoading ? (
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            >
              <Sparkles className="w-5 h-5" />
            </motion.div>
          ) : (
            <Send className="w-5 h-5 ml-0.5" />
          )}
        </Button>
      </motion.div>
      <p className="text-center text-xs text-gray-400 mt-2">
        AI 建议仅供参考，如有医疗需求请咨询专业医生。
      </p>
    </div>
  )
}
