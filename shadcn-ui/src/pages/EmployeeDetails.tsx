import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  User,
  Mail,
  Phone,
  Briefcase,
  Calendar,
  DollarSign,
  MapPin,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getEmployees, getLeaves } from "@/lib/store";
import { Employee, LeaveRequest } from "@/types";

const EmployeeDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);

  useEffect(() => {
    if (id) {
      const employees = getEmployees();
      const found = employees.find((e) => e.id === id);
      if (found) {
        setEmployee(found);
        const allLeaves = getLeaves();
        setLeaves(allLeaves.filter((l) => l.employeeId === id));
      }
    }
  }, [id]);

  if (!employee) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <h2 className="text-2xl font-bold text-muted-foreground">
          Employee Not Found
        </h2>
        <Button variant="link" onClick={() => navigate("/employees")}>
          Back to Employees
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <Button
        variant="ghost"
        onClick={() => navigate("/employees")}
        className="pl-0"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to List
      </Button>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Profile Card */}
        <Card className="md:col-span-1">
          <CardContent className="pt-6 flex flex-col items-center text-center">
            <div className="h-24 w-24 rounded-full bg-primary/10 flex items-center justify-center text-primary text-3xl font-bold mb-4">
              {employee.name.charAt(0)}
            </div>
            <h2 className="text-2xl font-bold">{employee.name}</h2>
            <p className="text-muted-foreground">{employee.position}</p>
            <Badge
              className="mt-2"
              variant={employee.status === "Active" ? "default" : "secondary"}
            >
              {employee.status}
            </Badge>

            <div className="w-full mt-6 space-y-4 text-left">
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{employee.email || "No email provided"}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span>{employee.phone || "No phone provided"}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span>Riyadh, Saudi Arabia</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Details & History */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Employment Details</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Briefcase className="h-4 w-4" />
                  Department
                </div>
                <p className="font-medium">{employee.department}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Calendar className="h-4 w-4" />
                  Hire Date
                </div>
                <p className="font-medium">{employee.hireDate}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <DollarSign className="h-4 w-4" />
                  Salary
                </div>
                <p className="font-medium">
                  $ {employee.salary.toLocaleString()}
                </p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <User className="h-4 w-4" />
                  Employee ID
                </div>
                <p className="font-medium font-mono text-sm">{employee.id}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Leave History</CardTitle>
            </CardHeader>
            <CardContent>
              {leaves.length > 0 ? (
                <div className="space-y-4">
                  {leaves.map((leave) => (
                    <div
                      key={leave.id}
                      className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                    >
                      <div>
                        <p className="font-medium">{leave.type} Leave</p>
                        <p className="text-sm text-muted-foreground">
                          {leave.startDate} to {leave.endDate}
                        </p>
                      </div>
                      <Badge
                        variant="outline"
                        className={
                          leave.status === "Approved"
                            ? "text-green-600 border-green-200"
                            : leave.status === "Rejected"
                            ? "text-red-600 border-red-200"
                            : "text-yellow-600 border-yellow-200"
                        }
                      >
                        {leave.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">
                  No leave history found.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDetails;
