"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/app/components/ui/button"
import { Input } from "@/app/components/ui/input"
import { motion } from "framer-motion"

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // TODO: Integrate with backend API
      const formDataBody = new FormData()
      formDataBody.append("username", formData.username)
      formDataBody.append("password", formData.password)
      
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        body: formDataBody,
      })

      if (res.ok) {
        const data = await res.json()
        localStorage.setItem("token", data.access_token)
        router.push("/chat")
      } else {
        alert("Login failed")
      }
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center aurora-bg p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md glass rounded-3xl p-8 space-y-6"
      >
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-serif font-bold bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text text-transparent">
            欢迎回来
          </h1>
          <p className="text-sm text-gray-500">登录您的 SkinTech 账号</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium ml-1">用户名</label>
            <Input 
              required
              placeholder="请输入用户名"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium ml-1">密码</label>
            <Input 
              required
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "登录中..." : "登录"}
          </Button>
        </form>

        <div className="text-center text-sm text-gray-500">
          还没有账号？{" "}
          <Link href="/auth/register" className="text-primary-600 font-medium hover:underline">
            立即注册
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
