import { Button } from "@/components/ui/button";
import { Lightbulb } from "lucide-react";

interface ExampleQuestionsProps {
  onQuestionClick: (question: string) => void;
  disabled?: boolean;
}

export const ExampleQuestions = ({ onQuestionClick, disabled = false }: ExampleQuestionsProps) => {
  const examples = [
    "Explain the attendance rules.",
    "What are the medical leave policies?",
    "Summarize the grading and evaluation criteria.",
    "What are the library borrowing limits?",
    "What happens if I use unfair means in an exam?",
    "Tell me about examination rules and procedures."
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <div className="bg-card/30 backdrop-blur-xl border border-primary/20 rounded-2xl p-6 relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 pointer-events-none" />
        
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <div className="relative">
              <Lightbulb className="w-5 h-5 text-primary" />
              <div className="absolute inset-0 blur-lg bg-primary/30" />
            </div>
            <h3 className="text-lg font-medium text-foreground">💡 Try asking:</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples.map((example, index) => (
              <Button
                key={index}
                variant="outline"
                className="justify-start text-left h-auto p-3 bg-card/50 border-primary/30 hover:bg-primary/10 hover:border-primary/50 transition-all duration-200 text-muted-foreground hover:text-foreground"
                onClick={() => onQuestionClick(example)}
                disabled={disabled}
              >
                <span className="text-sm leading-relaxed">{example}</span>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
