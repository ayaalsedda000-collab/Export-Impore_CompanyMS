export interface Employee {
  id: string;
  name: string;
  department: string;
  position: string;
  salary: number;
  hireDate: string; // ISO
  email: string;
  phone: string;
  status: "Active" | "Inactive" | "On Leave";
}

export interface LeaveRequest {
  id: string;
  employeeId: string;
  employeeName: string;
  type: "Annual" | "Sick" | "Emergency" | "Maternity" | "Other";
  startDate: string;
  endDate: string;
  reason: string;
  status: "Pending" | "Approved" | "Rejected";
  appliedOn: string;
}

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  date: string; // ISO
  checkIn: string;
  checkOut?: string;
  status: "Present" | "Late";
}
