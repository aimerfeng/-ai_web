import { useState, useCallback, useRef } from 'react'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { Message } from '@/app/components/chat/MessageBubble'

interface UseChatOptions {
  onComplete?: (message: Message) => void
  onError?: (error: Error) => void
}

export function useChat({ onComplete, onError }: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    const token = localStorage.getItem('token')
    if (!token) {
      onError?.(new Error("Unauthorized"))
      return
    }

    setIsLoading(true)
    
    // Add User Message Immediately
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content
    }
    setMessages(prev => [...prev, userMsg])

    // Prepare AI Message Placeholder
    const aiMsgId = (Date.now() + 1).toString()
    setMessages(prev => [...prev, {
      id: aiMsgId,
      role: 'assistant',
      content: ''
    }])

    abortControllerRef.current = new AbortController()

    try {
      await fetchEventSource('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId
        }),
        signal: abortControllerRef.current.signal,
        
        onmessage(msg) {
          try {
            const data = JSON.parse(msg.data)
            
            if (data.error) {
              throw new Error(data.error)
            }

            if (data.conversation_id) {
              setConversationId(data.conversation_id)
            }
            
            if (data.content) {
              setMessages(prev => prev.map(m => {
                if (m.id === aiMsgId) {
                  return { ...m, content: m.content + data.content }
                }
                return m
              }))
            }
            
            if (data.sources) {
              setMessages(prev => prev.map(m => {
                if (m.id === aiMsgId) {
                  return { ...m, sources: data.sources }
                }
                return m
              }))
            }
            
          } catch (err) {
            console.error("Error parsing SSE data", err)
          }
        },
        
        onerror(err) {
          console.error("SSE Error", err)
          // Don't retry automatically for this demo
          throw err
        }
      })
    } catch (err) {
      onError?.(err as Error)
      setMessages(prev => prev.map(m => {
        if (m.id === aiMsgId) {
          return { ...m, content: m.content + "\n\n*[Error: Failed to get response]*" }
        }
        return m
      }))
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }, [conversationId, onError])

  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsLoading(false)
    }
  }, [])

  return {
    messages,
    isLoading,
    sendMessage,
    abort,
    setMessages, // For loading history
    setConversationId
  }
}
