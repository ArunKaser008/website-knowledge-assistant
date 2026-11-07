
import { useState } from 'react'
import './App.css'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatSource {
  source_id: number
  title: string
  url: string
}

interface ChatApiResponse {
  question: string
  answer: string
  sources: ChatSource[]
  retrieved_chunks: number
}

interface ChatMessage {
  id: number
  role: 'assistant' | 'user'
  content: string
  sources?: ChatSource[]
}

const suggestedQuestions = [
  'How does MentorMuni help students prepare for placements?',
  'What services does MentorMuni offer to colleges?',
  'How can I check my interview readiness?',
  'What makes MentorMuni different from online courses?',
]

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: 'assistant',
      content:
        "Hi! Welcome to MentorMuni. 👋 I'm your AI assistant. I can help you understand our placement preparation platform, student services, college solutions, and interview readiness.",
    },
  ])

  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async (value?: string) => {
    const trimmedQuestion = (value ?? question).trim()

    if (!trimmedQuestion || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: trimmedQuestion,
    }

    setMessages((previous) => [...previous, userMessage])
    setQuestion('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          conversation_history: messages
            .filter((message) => message.id !== 1)
            .slice(-10)
            .map((message) => ({
              role: message.role,
              content: message.content,
            })),
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)

        throw new Error(
          errorData?.detail || `Request failed with status ${response.status}`,
        )
      }

      const data: ChatApiResponse = await response.json()

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }

      setMessages((previous) => [...previous, assistantMessage])
    } catch (error) {
      console.error('Chat API error:', error)

      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Something went wrong. Please try again.'

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Sorry, I couldn't process your question. ${errorMessage}`,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="top-header">
        <a className="brand" href="https://www.mentormuni.com">
          <img
            src="/mentormuni-logo.png"
            alt="MentorMuni"
            className="brand-logo"    
          />
          <span>
            Mentor<span className="brand-highlight">Muni</span>
          </span>
        </a>

        <div className="header-status">
          <span className="status-dot"></span>
          AI Assistant
        </div>
      </header>

      <main className="chat-container">
        <section className="welcome-section">
          <div className="assistant-avatar">
            <img src="/mentormuni-logo.png" alt="MentorMuni AI" />
          </div>
          <p className="eyebrow">YOUR PLACEMENT COMPANION</p>
          <h1>Let's make your career journey clearer.</h1>
          <p className="welcome-description">
            Ask anything about MentorMuni, placement preparation,
            interview readiness, or our solutions for colleges.
          </p>
        </section>

        <section className="conversation" aria-live="polite">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${message.role}`}
            >
              {message.role === 'assistant' && (
                <div className="message-avatar">
                 <img src="/mentormuni-logo.png" alt="MentorMuni AI" />
                </div>
              )}

              <div className="message-content">
                <span className="message-author">
                  {message.role === 'assistant' ? 'MentorMuni AI' : 'You'}
                </span>

               <div className="message-bubble markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
              </div>

                {message.sources && message.sources.length > 0 && (
                  <div className="sources-container">
                    <p className="sources-heading">Sources</p>

                    {message.sources.map((source) => (
                      <a
                        key={source.source_id}
                        className="source-link"
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <span>{source.source_id}.</span>
                        {source.title}
                        <span aria-hidden="true">↗</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-row assistant">
              <div className="message-avatar">
                 <img src="/mentormuni-logo.png" alt="MentorMuni AI" />
              </div>
              <div className="message-content">
                <span className="message-author">MentorMuni AI</span>
                <div className="message-bubble loading-message">
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-text">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </section>

        {messages.length === 1 && (
          <section className="suggestions-section">
            <p className="suggestions-heading">SUGGESTED QUESTIONS</p>

            <div className="suggestions-grid">
              {suggestedQuestions.map((item) => (
                <button
                  key={item}
                  className="suggestion-card"
                  onClick={() => handleSend(item)}
                  disabled={isLoading}
                >
                  <span>{item}</span>
                  <span className="suggestion-arrow">↗</span>
                </button>
              ))}
            </div>
          </section>
        )}

        <section className="composer-section">
          <div className="message-composer">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  void handleSend()
                }
              }}
              placeholder="Ask me anything about MentorMuni..."
              rows={1}
              disabled={isLoading}
            />

            <button
              className="send-button"
              onClick={() => void handleSend()}
              disabled={!question.trim() || isLoading}
              aria-label="Send message"
            >
              ↑
            </button>
          </div>

          <p className="composer-note">
            MentorMuni AI can make mistakes. Verify important information.
          </p>
        </section>
      </main>

      <footer className="app-footer">
        Powered by <a href="https://www.mentormuni.com">MentorMuni</a>
      </footer>
    </div>
  )
}

export default App
