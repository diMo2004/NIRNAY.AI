import { useNavigate } from "react-router-dom";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

const NewAnalysis = () => {
  const navigate = useNavigate();

  const handleGenerateReport = () => {
    navigate("/loading");
  };

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="font-display text-4xl font-bold mb-3">
            Let's Brainstorm <span className="gradient-text">New Ideas</span>
          </h1>
          <p className="text-muted-foreground">
            Describe the real-world problem you want to analyze with AI
          </p>
        </div>

        <div className="card-gradient rounded-xl p-1 glow-shadow">
          <div className="bg-card rounded-lg p-1">
            <Textarea
              placeholder="Describe the real-world problem you want to analyze..."
              className="min-h-[200px] bg-transparent border-0 resize-none focus-visible:ring-0 text-foreground placeholder:text-muted-foreground"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-start">
          <Button size="lg" className="gap-2 font-medium" onClick={handleGenerateReport}>
            <Sparkles className="w-4 h-4" />
            Generate Report
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default NewAnalysis;
