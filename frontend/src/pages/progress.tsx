import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Brain, Sparkles } from "lucide-react";

const Progress = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/report");
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center animate-fade-in">
        {/* Animated Logo */}
        <div className="relative mb-8">
          <div className="w-20 h-20 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center animate-pulse">
            <Brain className="w-10 h-10 text-primary" />
          </div>
          <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center animate-bounce">
            <Sparkles className="w-3 h-3 text-primary" />
          </div>
        </div>

        {/* Loading Text */}
        <h2 className="font-display text-2xl font-bold mb-3">
          <span className="text-foreground">Analyzing your </span>
          <span className="gradient-text">ideas...</span>
        </h2>
        <p className="text-muted-foreground mb-8">
          Our AI is brainstorming solutions for you
        </p>

        {/* Progress Bar */}
        <div className="w-64 mx-auto">
          <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full animate-[loading_2s_ease-in-out_infinite]" />
          </div>
        </div>

        {/* Loading Steps */}
        <div className="mt-8 space-y-2 text-sm text-muted-foreground">
          <p className="animate-fade-in" style={{ animationDelay: "0.5s" }}>
            ✓ Understanding context...
          </p>
          <p className="animate-fade-in" style={{ animationDelay: "1s" }}>
            ✓ Generating insights...
          </p>
          <p className="animate-fade-in opacity-50" style={{ animationDelay: "1.5s" }}>
            ○ Preparing report...
          </p>
        </div>
      </div>

      <style>{`
        @keyframes loading {
          0% { width: 0%; }
          50% { width: 70%; }
          100% { width: 100%; }
        }
      `}</style>
    </div>
  );
};

export default Progress;
