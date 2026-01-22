import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Clock, FileText } from "lucide-react";

const mockHistory = [
  { id: 1, title: "Market Analysis Q4 2025", date: "2 hours ago" },
  { id: 2, title: "Customer Sentiment Report", date: "Yesterday" },
  { id: 3, title: "Supply Chain Optimization", date: "3 days ago" },
];

const History = () => {
  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold mb-2">
            Analysis <span className="gradient-text">History</span>
          </h1>
          <p className="text-muted-foreground">
            View your previous analyses and reports
          </p>
        </div>

        <div className="space-y-4">
          {mockHistory.map((item) => (
            <Card
              key={item.id}
              className="p-4 bg-card border-border hover:border-primary/50 transition-colors cursor-pointer group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <FileText className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-foreground group-hover:text-primary transition-colors">
                    {item.title}
                  </h3>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Clock className="w-3 h-3" />
                    <span>{item.date}</span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default History;
