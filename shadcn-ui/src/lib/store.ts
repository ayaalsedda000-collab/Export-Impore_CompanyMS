import { Employee, LeaveRequest, AttendanceRecord } from "@/types";

const STORAGE_KEY_EMPLOYEES = "ems_data";
const STORAGE_KEY_LEAVES = "ems_leaves";
const STORAGE_KEY_ATTENDANCE = "ems_attendance";

const MOCK_EMPLOYEES: Employee[] = [
  {
    id: "1",
    name: "Ahmed Ali",
    department: "IT",
    position: "Senior Developer",
    salary: 15000,
    hireDate: "2023-01-15",
    email: "ahmed@company.com",
    phone: "0501234567",
    status: "Active",
  },
  {
    id: "2",
    name: "Sara Mohammed",
    department: "HR",
    position: "HR Manager",
    salary: 12000,
    hireDate: "2022-05-20",
    email: "sara@company.com",
    phone: "0507654321",
    status: "Active",
  },
  {
    id: "3",
    name: "Khalid Omar",
    department: "Sales",
    position: "Sales Executive",
    salary: 8000,
    hireDate: "2023-08-01",
    email: "khalid@company.com",
    phone: "0509876543",
    status: "On Leave",
  },
  {
    id: "4",
    name: "Fatima Hassan",
    department: "Marketing",
    position: "Marketing Specialist",
    salary: 9500,
    hireDate: "2023-03-10",
    email: "fatima@company.com",
    phone: "0501122334",
    status: "Active",
  },
  {
    id: "5",
    name: "Omar Abdullah",
    department: "Finance",
    position: "Accountant",
    salary: 11000,
    hireDate: "2021-11-15",
    email: "omar@company.com",
    phone: "0505566778",
    status: "Inactive",
  },
];

const MOCK_LEAVES: LeaveRequest[] = [
  {
    id: "l1",
    employeeId: "3",
    employeeName: "Khalid Omar",
    type: "Annual",
    startDate: "2023-11-20",
    endDate: "2023-11-25",
    reason: "Family vacation",
    status: "Approved",
    appliedOn: "2023-11-10",
  },
  {
    id: "l2",
    employeeId: "1",
    employeeName: "Ahmed Ali",
    type: "Sick",
    startDate: "2023-12-01",
    endDate: "2023-12-02",
    reason: "Flu",
    status: "Pending",
    appliedOn: "2023-12-01",
  },
];

export const getEmployees = (): Employee[] => {
  const data = localStorage.getItem(STORAGE_KEY_EMPLOYEES);
  if (data) {
    return JSON.parse(data);
  }
  localStorage.setItem(STORAGE_KEY_EMPLOYEES, JSON.stringify(MOCK_EMPLOYEES));
  return MOCK_EMPLOYEES;
};

export const saveEmployees = (employees: Employee[]) => {
  localStorage.setItem(STORAGE_KEY_EMPLOYEES, JSON.stringify(employees));
};

export const getLeaves = (): LeaveRequest[] => {
  const data = localStorage.getItem(STORAGE_KEY_LEAVES);
  if (data) {
    return JSON.parse(data);
  }
  localStorage.setItem(STORAGE_KEY_LEAVES, JSON.stringify(MOCK_LEAVES));
  return MOCK_LEAVES;
};

export const saveLeaves = (leaves: LeaveRequest[]) => {
  localStorage.setItem(STORAGE_KEY_LEAVES, JSON.stringify(leaves));
};

export const getAttendance = (): AttendanceRecord[] => {
  const data = localStorage.getItem(STORAGE_KEY_ATTENDANCE);
  if (data) {
    return JSON.parse(data);
  }
  return [];
};

export const saveAttendance = (attendance: AttendanceRecord[]) => {
  localStorage.setItem(STORAGE_KEY_ATTENDANCE, JSON.stringify(attendance));
};
