import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  content: string;
  isBot: boolean;
  timestamp?: string;
}

export const ChatMessage = ({ content, isBot, timestamp }: ChatMessageProps) => {
  return (
    <div
      className={cn(
        "flex gap-3 mb-4 animate-fade-in",
        isBot ? "justify-start" : "justify-end"
      )}
    >
      {isBot && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-card flex items-center justify-center ring-2 ring-primary/30 shadow-lg">
          <Bot className="w-5 h-5 text-primary" />
        </div>
      )}
      
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 transition-all hover:scale-[1.01]",
          isBot
            ? "bg-card text-card-foreground border border-primary/20 shadow-lg"
            : "bg-gradient-to-br from-primary to-accent text-primary-foreground"
        )}
        style={isBot 
          ? { boxShadow: "0 4px 24px hsla(250, 100%, 70%, 0.1)" } 
          : { boxShadow: "var(--shadow-glow)" }
        }
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
        {timestamp && (
          <p className={cn(
            "text-xs mt-1",
            isBot ? "text-muted-foreground" : "text-primary-foreground/80"
          )}>
            {timestamp}
          </p>
        )}
      </div>

      {!isBot && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center ring-2 ring-primary/30 shadow-lg">
          <User className="w-5 h-5 text-primary-foreground" />
        </div>
      )}
    </div>
  );
};
