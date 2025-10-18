import { useState, useRef, useEffect } from "react";
import { Sparkles, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { TypingIndicator } from "@/components/TypingIndicator";
import { ExampleQuestions } from "@/components/ExampleQuestions";
import { toast } from "@/hooks/use-toast";

interface Message {
  id: string;
  content: string;
  isBot: boolean;
  timestamp: string;
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      content: "Hello! I'm your SRB AI Assistant. I can help you find information from the Student Resource Book (SRB). Ask me anything about academic policies, procedures, attendance requirements, examination rules, and more!",
      isBot: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isBot: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Create a placeholder bot message for streaming
    const botMessageId = (Date.now() + 1).toString();
    const botMessage: Message = {
      id: botMessageId,
      content: "",
      isBot: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, botMessage]);

    try {
      // Use fetch with proper streaming
      const response = await fetch('http://localhost:7860/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
        body: JSON.stringify({ message: content }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setIsTyping(false); // Stop typing indicator as we start receiving content
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim();
                if (jsonStr) {
                  const data = JSON.parse(jsonStr);
                  
                  if (data.error) {
                    throw new Error(data.error);
                  }
                  
                  if (data.chunk && !data.done) {
                    accumulatedContent += data.chunk;
                    
                    // Update the bot message with accumulated content
                    setMessages(prev => prev.map(msg => 
                      msg.id === botMessageId 
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    ));
                  }
                  
                  if (data.done) {
                    return; // Streaming complete
                  }
                }
              } catch (e) {
                // Skip malformed JSON
                console.warn('Failed to parse JSON:', line);
                continue;
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error calling API:', error);
      const errorMessage = `Sorry, I encountered an error while processing your question. Please make sure the backend server is running on http://localhost:7860`;
      
      setMessages(prev => prev.map(msg => 
        msg.id === botMessageId 
          ? { ...msg, content: errorMessage }
          : msg
      ));
      
      toast({
        title: "Connection Error",
        description: "Unable to connect to the chatbot service. Please try again later.",
        variant: "destructive"
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: "welcome",
        content: "Hello! I'm your SRB AI Assistant. I can help you find information from the Student Resource Book (SRB). Ask me anything about academic policies, procedures, attendance requirements, examination rules, and more!",
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    toast({
      title: "Chat cleared",
      description: "Your conversation has been reset."
    });
  };

  return (
    <div 
      className="min-h-screen flex flex-col relative overflow-hidden"
      style={{ background: "var(--gradient-bg)" }}
    >
      {/* Ambient glow effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[128px] animate-pulse-glow" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-[128px] animate-pulse-glow" style={{ animationDelay: "1s" }} />
      
      {/* Header */}
      <header className="bg-card/70 backdrop-blur-xl border-b border-primary/20 sticky top-0 z-10 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" />
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between relative z-10">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Sparkles className="w-6 h-6 text-primary animate-pulse" />
              <div className="absolute inset-0 blur-lg bg-primary/50" />
            </div>
            <h1 className="text-xl font-semibold text-foreground">SRB Chat Assistant ✨</h1>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearChat}
            className="text-muted-foreground hover:text-foreground hover:bg-primary/10 transition-colors"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear
          </Button>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto relative z-10">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              content={message.content}
              isBot={message.isBot}
              timestamp={message.timestamp}
            />
          ))}
          
          {isTyping && <TypingIndicator />}
          
          {/* Show example questions only when there's just the welcome message */}
          {messages.length === 1 && !isTyping && (
            <ExampleQuestions 
              onQuestionClick={handleSendMessage} 
              disabled={isTyping}
            />
          )}
          
          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <div className="relative z-10">
        <ChatInput onSend={handleSendMessage} disabled={isTyping} />
      </div>
    </div>
  );
};

export default Index;
