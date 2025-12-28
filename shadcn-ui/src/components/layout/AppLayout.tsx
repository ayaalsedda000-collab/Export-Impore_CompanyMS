import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  BarChart3,
  Menu,
  X,
  LogOut,
  CalendarDays,
  Moon,
  Sun,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/sonner";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout = ({ children }: AppLayoutProps) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { signOut, user } = useAuth();

  useEffect(() => {
    const isDark = localStorage.getItem("theme") === "dark";
    setIsDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    if (newMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  const handleLogout = async () => {
    try {
      await signOut();
      toast.success("تم تسجيل الخروج بنجاح");
      navigate("/login");
    } catch (error) {
      toast.error("حدث خطأ أثناء تسجيل الخروج");
    }
  };

  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/" },
    { icon: Users, label: "Employees", path: "/employees" },
    { icon: CalendarDays, label: "Leaves", path: "/leaves" },
    { icon: BarChart3, label: "Analytics", path: "/analytics" },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Mobile Sidebar Overlay */}
      {!isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setIsSidebarOpen(true)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-30
          w-64 bg-card border-r border-border transition-transform duration-300 ease-in-out
          ${
            !isSidebarOpen
              ? "-translate-x-full lg:translate-x-0 lg:w-[70px]"
              : "translate-x-0"
          }
        `}
      >
        <div className="h-full flex flex-col">
          <div
            className={`h-16 flex items-center px-4 border-b border-border ${
              !isSidebarOpen ? "justify-center" : "justify-between"
            }`}
          >
            {isSidebarOpen ? (
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                EMS Pro
              </span>
            ) : (
              <span className="text-xl font-bold text-blue-600">E</span>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setIsSidebarOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <nav className="flex-1 py-4 px-2 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center px-3 py-2 rounded-md transition-colors
                  ${
                    location.pathname === item.path
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }
                  ${!isSidebarOpen ? "justify-center" : ""}
                `}
                title={!isSidebarOpen ? item.label : ""}
              >
                <item.icon
                  className={`h-5 w-5 ${isSidebarOpen ? "mr-3" : ""}`}
                />
                {isSidebarOpen && <span>{item.label}</span>}
              </Link>
            ))}
          </nav>

          <div className="p-4 border-t border-border space-y-2">
            <Button
              variant="ghost"
              className={`w-full justify-start ${
                !isSidebarOpen ? "px-2 justify-center" : ""
              }`}
              onClick={toggleTheme}
            >
              {isDarkMode ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
              {isSidebarOpen && (
                <span className="ml-3">
                  {isDarkMode ? "Light Mode" : "Dark Mode"}
                </span>
              )}
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 ${
                !isSidebarOpen ? "px-2 justify-center" : ""
              }`}
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5" />
              {isSidebarOpen && <span className="ml-3">Logout</span>}
            </Button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-4 lg:px-8">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="mr-4"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-4">
            <div className="text-sm text-muted-foreground hidden sm:block">
              {user?.email || "Welcome, User"}
            </div>
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium">
              {user?.email ? user.email[0].toUpperCase() : "U"}
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8 overflow-auto bg-muted/30">
          {children}
        </main>
      </div>
      <Toaster />
    </div>
  );
};

export default AppLayout;
