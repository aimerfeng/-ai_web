"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Sidebar } from "@/app/components/chat/Sidebar"
import { MessageBubble } from "@/app/components/chat/MessageBubble"
import { ChatInput } from "@/app/components/chat/ChatInput"
import { useChat } from "@/app/hooks/useChat"

export default function ChatPage() {
  const router = useRouter()
  const { messages, isLoading, sendMessage, setConversationId } = useChat()
  const [activeId, setActiveId] = useState<string | null>(null)
  
  // Mock conversations for UI demo
  const [conversations] = useState([
    { id: '1', title: '抗老护肤流程', updatedAt: new Date() },
    { id: '2', title: '干皮保湿建议', updatedAt: new Date() }
  ])

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/auth/login")
    }
  }, [router])

  return (
    <div className="flex h-screen aurora-bg overflow-hidden">
      <Sidebar 
        conversations={conversations}
        activeId={activeId}
        onSelect={(id) => {
          setActiveId(id)
          setConversationId(id)
        }}
        onNew={() => {
          setActiveId(null)
          setConversationId(null)
        }}
        onLogout={() => {
          localStorage.removeItem("token")
          router.push("/auth/login")
        }}
      />
      
      <div className="flex-1 flex flex-col h-full relative z-10">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-6">
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-8 rounded-full glass bg-white/30 backdrop-blur-xl shadow-2xl"
              >
                <div className="text-6xl mb-2">✨</div>
              </motion.div>
              <div className="space-y-2">
                <h1 className="text-4xl font-serif font-bold bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text text-transparent">
                  你好，我是 SkinTech
                </h1>
                <p className="text-gray-500 max-w-md mx-auto">
                  您的个人 AI 护肤配方师。请咨询我关于成分、护肤流程或产品分析的问题。
                </p>
              </div>
            </div>
          ) : (
            <div className="py-6 space-y-6">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-4 max-w-3xl mx-auto w-full justify-start"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-400 to-accent-300 flex items-center justify-center shrink-0 shadow-md">
                    <motion.div 
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                      className="w-2 h-2 bg-white rounded-full"
                    />
                  </div>
                  <div className="px-5 py-3 rounded-2xl glass rounded-tl-none border border-white/50 text-gray-500 text-sm italic">
                    正在分析配方成分...
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}
