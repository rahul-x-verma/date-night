'use client'

import { useState, useEffect } from 'react'
import { 
  Container,
  Paper,
  TextField,
  Button,
  Box,
  Typography,
  CircularProgress
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'

export default function Home() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([])
  const [isLoading, setIsLoading] = useState(false)
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/chat')
    
    ws.onopen = () => {
      console.log('Connected to WebSocket')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.thread_id) {
        setThreadId(data.thread_id)
      }
      setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }])
      setIsLoading(false)
      setMessage('')
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsLoading(false)
    }

    ws.onclose = () => {
      console.log('Disconnected from WebSocket')
    }

    setSocket(ws)

    // Cleanup on unmount
    return () => {
      ws.close()
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || !socket) return

    setIsLoading(true)
    setChatHistory(prev => [...prev, { role: 'user', content: message }])
    
    try {
      socket.send(JSON.stringify({ 
        message,
        thread_id: threadId
      }))
    } catch (error) {
      console.error('Error:', error)
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Typography 
        variant="h4" 
        component="h1" 
        sx={{ 
          mb: 3, 
          textAlign: 'center',
          fontWeight: 600,
          color: '#2C2C2E'
        }}
      >
        Date Night Assistant
      </Typography>
      <Paper elevation={2} sx={{ 
        p: 2, 
        flexGrow: 1,
        display: 'flex', 
        flexDirection: 'column',
        bgcolor: '#ffffff',
        borderRadius: 2,
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <Box sx={{ 
          flexGrow: 1, 
          overflow: 'auto', 
          mb: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}>
          {chatHistory.map((msg, i) => (
            <Box
              key={i}
              sx={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%'
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  bgcolor: msg.role === 'user' ? '#007AFF' : '#E8E8E8',
                  color: msg.role === 'user' ? '#ffffff' : '#2C2C2E',
                  borderRadius: 2
                }}
              >
                <Typography>{msg.content}</Typography>
              </Paper>
            </Box>
          ))}
        </Box>

        <Box component="form" onSubmit={handleSubmit} sx={{ 
          display: 'flex', 
          gap: 1,
          bgcolor: '#f8f8f8',
          p: 2,
          borderRadius: 1,
          mt: 'auto'
        }}>
          <TextField
            fullWidth
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
            size="small"
            autoFocus
            multiline
            maxRows={4}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: '#ffffff'
              }
            }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            disabled={isLoading}
            endIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
            sx={{
              bgcolor: '#007AFF',
              '&:hover': {
                bgcolor: '#0056b3'
              }
            }}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Container>
  )
}