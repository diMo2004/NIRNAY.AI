import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Share2 } from "lucide-react";
import { Link } from "react-router-dom";

const Report = () => {
  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div>
              <h1 className="font-display text-2xl font-bold">
                Analysis <span className="gradient-text">Report</span>
              </h1>
              <p className="text-sm text-muted-foreground">Generated just now</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Share2 className="w-4 h-4" />
              Share
            </Button>
            <Button size="sm" className="gap-2">
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>
        </div>

        <Card className="p-6 bg-card border-border">
          <h2 className="font-display text-xl font-semibold mb-4">Summary</h2>
          <p className="text-muted-foreground leading-relaxed">
            Your analysis has been completed successfully. This is where the AI-generated insights 
            and recommendations will appear based on your input problem statement.
          </p>
        </Card>

        <Card className="p-6 bg-card border-border mt-4">
          <h2 className="font-display text-xl font-semibold mb-4">Key Findings</h2>
          <ul className="space-y-3 text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
              <span>Finding 1: Placeholder for AI-generated insight</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
              <span>Finding 2: Placeholder for AI-generated insight</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
              <span>Finding 3: Placeholder for AI-generated insight</span>
            </li>
          </ul>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Report;
