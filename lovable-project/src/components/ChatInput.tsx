import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "./ui/button";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div 
      className="p-4 bg-card/90 backdrop-blur-xl border-t border-primary/20 relative"
      style={{ boxShadow: "var(--shadow-float), var(--shadow-ambient)" }}
    >
      <div className="absolute inset-0 bg-gradient-to-t from-primary/5 to-transparent pointer-events-none" />
      <div className="max-w-4xl mx-auto flex gap-3 items-end relative z-10">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask me anything about the SRB (Student Resource Book)..."
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 pr-12 rounded-2xl border border-primary/30 bg-background/80 backdrop-blur-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none transition-all"
            style={{ 
              minHeight: "48px",
              maxHeight: "120px",
              boxShadow: "inset 0 0 20px hsla(250, 100%, 70%, 0.05), var(--shadow-soft)"
            }}
          />
        </div>
        <Button
          onClick={handleSend}
          disabled={!input.trim() || disabled}
          size="icon"
          className="h-12 w-12 rounded-full bg-gradient-to-br from-primary to-accent hover:scale-110 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100"
          style={{ boxShadow: "var(--shadow-glow)" }}
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>
    </div>
  );
};
