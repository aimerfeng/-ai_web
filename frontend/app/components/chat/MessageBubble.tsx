import ReactMarkdown from 'react-markdown'
import { motion } from "framer-motion"
import { Sparkles, User, ExternalLink } from "lucide-react"
import { cn } from "@/app/lib/utils"

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: { type: 'product' | 'web', title: string, url?: string }[]
}

export function MessageBubble({ message }: { message: Message }) {
  const isAI = message.role === 'assistant'

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex gap-4 max-w-3xl mx-auto w-full",
        isAI ? "justify-start" : "justify-end"
      )}
    >
      {/* Avatar */}
      {isAI && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-400 to-accent-300 flex items-center justify-center shrink-0 shadow-md">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={cn(
        "flex flex-col gap-2 max-w-[85%]",
        isAI ? "items-start" : "items-end"
      )}>
        <div className={cn(
          "px-5 py-3 rounded-2xl shadow-sm",
          isAI 
            ? "glass rounded-tl-none border border-white/50" 
            : "bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-tr-none"
        )}>
          <div className="prose prose-sm max-w-none dark:prose-invert">
             <ReactMarkdown 
               components={{
                 // Override link styling
                 a: ({node, ...props}) => <a {...props} className={isAI ? "text-primary-600 underline" : "text-white underline"} target="_blank" rel="noopener noreferrer" />,
                 p: ({node, ...props}) => <p {...props} className="mb-1 last:mb-0" />,
                 ul: ({node, ...props}) => <ul {...props} className="list-disc pl-4 mb-2" />,
                 ol: ({node, ...props}) => <ol {...props} className="list-decimal pl-4 mb-2" />,
               }}
             >
               {message.content}
             </ReactMarkdown>
          </div>
        </div>

        {/* Sources */}
        {isAI && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-1">
            {message.sources.map((source, i) => (
              <a 
                key={i} 
                href={source.url || "#"} 
                target="_blank"
                className="flex items-center gap-1 text-xs px-2 py-1 bg-white/40 border border-white/60 rounded-full hover:bg-white/60 transition-colors"
              >
                {source.type === 'product' ? '🧴' : '🌐'}
                <span className="truncate max-w-[150px]">{source.title}</span>
                {source.url && <ExternalLink className="w-3 h-3 opacity-50" />}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* User Avatar */}
      {!isAI && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center shrink-0">
          <User className="w-4 h-4 text-gray-500" />
        </div>
      )}
    </motion.div>
  )
}
