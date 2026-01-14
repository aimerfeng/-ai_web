"use client"

import { useState } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { MessageSquare, Plus, LogOut, Settings, User } from "lucide-react"
import { Button } from "@/app/components/ui/button"
import { cn } from "@/app/lib/utils"

interface Conversation {
  id: string
  title: string
  updatedAt: Date
}

interface SidebarProps {
  conversations: Conversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  onLogout: () => void
}

export function Sidebar({ conversations, activeId, onSelect, onNew, onLogout }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <motion.div 
      initial={{ width: 280 }}
      animate={{ width: isOpen ? 280 : 80 }}
      className={cn(
        "h-screen glass border-r border-primary-100 flex flex-col transition-all duration-300 relative z-20",
        !isOpen && "items-center"
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-primary-50">
        <Button 
          variant="default" 
          className={cn("w-full shadow-lg", !isOpen && "w-10 h-10 p-0 rounded-full")}
          onClick={onNew}
        >
          <Plus className="w-4 h-4" />
          {isOpen && <span className="ml-2">新对话</span>}
        </Button>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2 scrollbar-hide">
        {conversations.map((conv) => (
          <Button
            key={conv.id}
            variant={activeId === conv.id ? "secondary" : "ghost"}
            className={cn(
              "w-full justify-start text-left font-normal",
              !isOpen && "justify-center px-0"
            )}
            onClick={() => onSelect(conv.id)}
          >
            <MessageSquare className="w-4 h-4 min-w-[16px]" />
            {isOpen && (
              <span className="ml-2 truncate max-w-[200px]">{conv.title}</span>
            )}
          </Button>
        ))}
      </div>

      {/* User Footer */}
      <div className="p-4 border-t border-primary-50 space-y-2">
        <div className={cn("flex items-center gap-3 px-2", !isOpen && "justify-center")}>
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
            <User className="w-4 h-4 text-primary-600" />
          </div>
          {isOpen && (
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium truncate">用户</p>
              <p className="text-xs text-gray-500 truncate">普通会员</p>
            </div>
          )}
        </div>
        
        <Button 
          variant="ghost" 
          className={cn("w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50", !isOpen && "justify-center")}
          onClick={onLogout}
        >
          <LogOut className="w-4 h-4" />
          {isOpen && <span className="ml-2">退出登录</span>}
        </Button>
      </div>
      
      {/* Toggle Button (Mobile/Desktop) */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-3 top-1/2 w-6 h-6 bg-white border border-gray-200 rounded-full flex items-center justify-center shadow-sm hover:scale-110 transition-transform"
      >
        <div className="w-1 h-3 bg-gray-300 rounded-full" />
      </button>
    </motion.div>
  )
}
