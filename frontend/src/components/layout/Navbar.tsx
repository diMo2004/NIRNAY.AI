import { Brain } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

const navLinks = [
  { label: "New Analysis", path: "/" },
  { label: "History", path: "/history" },
];

const Navbar = () => {
  const location = useLocation();

  return (
    <header className="h-16 border-b border-border bg-navbar flex items-center justify-between px-6 sticky top-0 z-50">
      {/* Logo Section */}
      <Link to="/" className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
          <Brain className="w-6 h-6 text-primary" />
        </div>
        <span className="font-display text-xl font-bold tracking-tight">
          <span className="text-foreground">NIRNAY</span>
          <span className="gradient-text">.AI</span>
        </span>
      </Link>

      {/* Navigation Links */}
      <nav className="flex items-center gap-1">
        {navLinks.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-colors",
              location.pathname === link.path
                ? "text-primary bg-primary/10"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary"
            )}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
};

export default Navbar;