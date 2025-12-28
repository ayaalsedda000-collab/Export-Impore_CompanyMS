import { useState, useEffect } from "react";
import { Plus, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { getEmployees, getLeaves, saveLeaves } from "@/lib/store";
import { LeaveRequest, LEAVE_TYPES, LeaveType } from "@/types";

const Leaves = () => {
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { toast } = useToast();
  const employees = getEmployees();

  // Form state
  const [formData, setFormData] = useState({
    employeeId: "",
    type: "",
    startDate: "",
    endDate: "",
    reason: "",
  });

  useEffect(() => {
    setLeaves(getLeaves());
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const employee = employees.find((e) => e.id === formData.employeeId);

    if (!employee) return;

    const newLeave: LeaveRequest = {
      id: Math.random().toString(36).substr(2, 9),
      employeeId: formData.employeeId,
      employeeName: employee.name,
      type: formData.type as LeaveType,
      startDate: formData.startDate,
      endDate: formData.endDate,
      reason: formData.reason,
      status: "Pending",
      appliedOn: new Date().toISOString().split("T")[0],
    };

    const updatedLeaves = [newLeave, ...leaves];
    setLeaves(updatedLeaves);
    saveLeaves(updatedLeaves);
    setIsDialogOpen(false);
    setFormData({
      employeeId: "",
      type: "",
      startDate: "",
      endDate: "",
      reason: "",
    });
    toast({ title: "Success", description: "Leave request submitted" });
  };

  const handleStatusChange = (id: string, status: "Approved" | "Rejected") => {
    const updatedLeaves = leaves.map((leave) =>
      leave.id === id ? { ...leave, status } : leave
    );
    setLeaves(updatedLeaves);
    saveLeaves(updatedLeaves);
    toast({
      title: status === "Approved" ? "Approved" : "Rejected",
      description: `Leave request ${status.toLowerCase()}`,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Approved":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
      case "Rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
      default:
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400";
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Leave Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage employee leave requests and approvals.
          </p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Request
        </Button>
      </div>

      <div className="rounded-md border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Applied On</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leaves.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="text-center h-24 text-muted-foreground"
                >
                  No leave requests found.
                </TableCell>
              </TableRow>
            ) : (
              leaves.map((leave) => (
                <TableRow key={leave.id}>
                  <TableCell className="font-medium">
                    {leave.employeeName}
                  </TableCell>
                  <TableCell>{leave.type}</TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {leave.startDate}{" "}
                      <span className="text-muted-foreground">to</span>{" "}
                      {leave.endDate}
                    </div>
                  </TableCell>
                  <TableCell
                    className="max-w-[200px] truncate"
                    title={leave.reason}
                  >
                    {leave.reason}
                  </TableCell>
                  <TableCell>{leave.appliedOn}</TableCell>
                  <TableCell>
                    <Badge
                      variant="secondary"
                      className={getStatusColor(leave.status)}
                    >
                      {leave.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    {leave.status === "Pending" && (
                      <div className="flex justify-end gap-2">
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50"
                          onClick={() =>
                            handleStatusChange(leave.id, "Approved")
                          }
                          title="Approve"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() =>
                            handleStatusChange(leave.id, "Rejected")
                          }
                          title="Reject"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>New Leave Request</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="employee">Employee</Label>
              <Select
                value={formData.employeeId}
                onValueChange={(val) =>
                  setFormData({ ...formData, employeeId: val })
                }
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select employee" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={emp.id}>
                      {emp.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Leave Type</Label>
              <Select
                value={formData.type}
                onValueChange={(val) => setFormData({ ...formData, type: val })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  {LEAVE_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={formData.startDate}
                  onChange={(e) =>
                    setFormData({ ...formData, startDate: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate">End Date</Label>
                <Input
                  id="endDate"
                  type="date"
                  value={formData.endDate}
                  onChange={(e) =>
                    setFormData({ ...formData, endDate: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="reason">Reason</Label>
              <Textarea
                id="reason"
                value={formData.reason}
                onChange={(e) =>
                  setFormData({ ...formData, reason: e.target.value })
                }
                placeholder="Brief description of the leave request"
                required
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Submit Request</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Leaves;
