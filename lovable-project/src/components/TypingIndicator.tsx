import { Bot } from "lucide-react";

export const TypingIndicator = () => {
  return (
    <div className="flex gap-3 mb-4 animate-fade-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-card flex items-center justify-center ring-2 ring-primary/30 shadow-lg">
        <Bot className="w-5 h-5 text-primary animate-pulse" />
      </div>
      
      <div 
        className="bg-card text-card-foreground border border-primary/20 rounded-2xl px-4 py-3"
        style={{ boxShadow: "0 4px 24px hsla(250, 100%, 70%, 0.1)" }}
      >
        <div className="flex gap-1.5 items-center">
          <div 
            className="w-2 h-2 rounded-full bg-primary animate-typing-dot"
            style={{ animationDelay: "0s" }}
          />
          <div 
            className="w-2 h-2 rounded-full bg-primary animate-typing-dot"
            style={{ animationDelay: "0.2s" }}
          />
          <div 
            className="w-2 h-2 rounded-full bg-primary animate-typing-dot"
            style={{ animationDelay: "0.4s" }}
          />
        </div>
      </div>
    </div>
  );
};
