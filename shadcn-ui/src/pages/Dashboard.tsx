import { useEffect, useState } from "react";
import {
  Users,
  Building2,
  DollarSign,
  UserCheck,
  TrendingUp,
  Clock,
  CalendarCheck,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  getEmployees,
  getLeaves,
  getAttendance,
  saveAttendance,
} from "@/lib/store";
import { Employee, AttendanceRecord } from "@/types";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    departments: 0,
    avgSalary: 0,
    activeEmployees: 0,
  });
  const [recentEmployees, setRecentEmployees] = useState<Employee[]>([]);
  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [checkInTime, setCheckInTime] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    const data = getEmployees();
    const uniqueDepts = new Set(data.map((e) => e.department));
    const totalSalary = data.reduce((acc, curr) => acc + curr.salary, 0);
    const active = data.filter((e) => e.status === "Active").length;

    setStats({
      totalEmployees: data.length,
      departments: uniqueDepts.size,
      avgSalary: data.length ? Math.round(totalSalary / data.length) : 0,
      activeEmployees: active,
    });

    setRecentEmployees(data.slice(-5).reverse());

    // Check today's attendance
    const today = new Date().toISOString().split("T")[0];
    const attendance = getAttendance();
    const todayRecord = attendance.find(
      (a) => a.date === today && a.employeeId === "current-user"
    ); // Mock user

    if (todayRecord) {
      setIsCheckedIn(!todayRecord.checkOut);
      setCheckInTime(todayRecord.checkIn);
    }
  }, []);

  const handleAttendance = () => {
    const now = new Date();
    const today = now.toISOString().split("T")[0];
    const timeString = now.toLocaleTimeString();
    const allAttendance = getAttendance();

    if (!isCheckedIn) {
      // Check In
      const newRecord: AttendanceRecord = {
        id: Math.random().toString(36).substr(2, 9),
        employeeId: "current-user",
        date: today,
        checkIn: timeString,
        status: now.getHours() > 9 ? "Late" : "Present",
      };
      saveAttendance([...allAttendance, newRecord]);
      setIsCheckedIn(true);
      setCheckInTime(timeString);
      toast({
        title: "Checked In",
        description: `Successfully checked in at ${timeString}`,
      });
    } else {
      // Check Out
      const updated = allAttendance.map((a) => {
        if (
          a.date === today &&
          a.employeeId === "current-user" &&
          !a.checkOut
        ) {
          return { ...a, checkOut: timeString };
        }
        return a;
      });
      saveAttendance(updated);
      setIsCheckedIn(false);
      setCheckInTime(null);
      toast({
        title: "Checked Out",
        description: `Successfully checked out at ${timeString}`,
      });
    }
  };

  const statCards = [
    {
      title: "Total Employees",
      value: stats.totalEmployees,
      icon: Users,
      description: "Total workforce count",
      color: "text-blue-600",
    },
    {
      title: "Departments",
      value: stats.departments,
      icon: Building2,
      description: "Active departments",
      color: "text-indigo-600",
    },
    {
      title: "Avg. Salary",
      value: `$ ${stats.avgSalary.toLocaleString()}`,
      icon: DollarSign,
      description: "Monthly average",
      color: "text-green-600",
    },
    {
      title: "Active Status",
      value: `${stats.activeEmployees}`,
      icon: UserCheck,
      description: "Currently active staff",
      color: "text-emerald-600",
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Here's what's happening today.
          </p>
        </div>

        <Card className="w-full md:w-auto bg-primary/5 border-primary/20">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-background p-2 rounded-full">
              <Clock
                className={`h-6 w-6 ${
                  isCheckedIn ? "text-green-600" : "text-muted-foreground"
                }`}
              />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {isCheckedIn ? "Checked In At" : "Not Checked In"}
              </p>
              <p className="text-lg font-bold">
                {isCheckedIn ? checkInTime : "--:-- --"}
              </p>
            </div>
            <Button
              onClick={handleAttendance}
              variant={isCheckedIn ? "destructive" : "default"}
              className="ml-4"
            >
              {isCheckedIn ? "Check Out" : "Check In"}
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Recent Hires
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentEmployees.map((employee) => (
                <div
                  key={employee.id}
                  className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium text-sm">
                      {employee.name.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium leading-none">
                        {employee.name}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {employee.position}
                      </p>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {employee.hireDate}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarCheck className="h-5 w-5 text-primary" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Button variant="outline" className="w-full justify-start" asChild>
              <a href="/employees">
                <Users className="mr-2 h-4 w-4" />
                Manage Employees
              </a>
            </Button>
            <Button variant="outline" className="w-full justify-start" asChild>
              <a href="/leaves">
                <CalendarCheck className="mr-2 h-4 w-4" />
                Review Leave Requests
              </a>
            </Button>
            <Button variant="outline" className="w-full justify-start" asChild>
              <a href="/analytics">
                <TrendingUp className="mr-2 h-4 w-4" />
                View Analytics
              </a>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
