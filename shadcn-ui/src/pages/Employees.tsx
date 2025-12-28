import { useState, useEffect } from "react";
import { Plus, Search, Download, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import EmployeeTable from "@/components/employees/EmployeeTable";
import EmployeeForm from "@/components/employees/EmployeeForm";
import { Employee, DEPARTMENTS, STATUSES } from "@/types";
import { getEmployees, saveEmployees } from "@/lib/store";
import * as XLSX from "xlsx";

const Employees = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [filteredData, setFilteredData] = useState<Employee[]>([]);
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    const data = getEmployees();
    setEmployees(data);
    setFilteredData(data);
  }, []);

  useEffect(() => {
    let result = employees;

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (e) =>
          e.name.toLowerCase().includes(q) ||
          e.position.toLowerCase().includes(q) ||
          e.department.toLowerCase().includes(q)
      );
    }

    if (deptFilter && deptFilter !== "All") {
      result = result.filter((e) => e.department === deptFilter);
    }

    if (statusFilter && statusFilter !== "All") {
      result = result.filter((e) => e.status === statusFilter);
    }

    setFilteredData(result);
  }, [employees, search, deptFilter, statusFilter]);

  const handleAdd = (data: Omit<Employee, "id"> | Employee) => {
    const newEmployee = {
      ...data,
      id: Math.random().toString(36).substr(2, 9),
    } as Employee;

    const updated = [...employees, newEmployee];
    setEmployees(updated);
    saveEmployees(updated);
    toast({ title: "Success", description: "Employee added successfully" });
  };

  const handleEdit = (data: Omit<Employee, "id"> | Employee) => {
    const empData = data as Employee;
    const updated = employees.map((e) => (e.id === empData.id ? empData : e));
    setEmployees(updated);
    saveEmployees(updated);
    setEditingEmployee(null);
    toast({ title: "Success", description: "Employee updated successfully" });
  };

  const handleDelete = (id: string) => {
    const updated = employees.filter((e) => e.id !== id);
    setEmployees(updated);
    saveEmployees(updated);
    toast({ title: "Success", description: "Employee deleted successfully" });
  };

  const exportToExcel = () => {
    const ws = XLSX.utils.json_to_sheet(filteredData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Employees");
    XLSX.writeFile(wb, "employees_data.xlsx");
    toast({
      title: "Exported",
      description: "Data exported to Excel successfully",
    });
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Employees</h1>
          <p className="text-muted-foreground mt-1">
            Manage your employee records and information.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportToExcel}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button
            onClick={() => {
              setEditingEmployee(null);
              setIsFormOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Employee
          </Button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-center bg-white p-4 rounded-lg border shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, position..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <Select value={deptFilter} onValueChange={setDeptFilter}>
            <SelectTrigger className="w-[180px]">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All Departments</SelectItem>
              {DEPARTMENTS.map((d) => (
                <SelectItem key={d} value={d}>
                  {d}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All Statuses</SelectItem>
              {STATUSES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <EmployeeTable
        data={filteredData}
        onEdit={(emp) => {
          setEditingEmployee(emp);
          setIsFormOpen(true);
        }}
        onDelete={handleDelete}
      />

      <EmployeeForm
        open={isFormOpen}
        onOpenChange={(open) => {
          setIsFormOpen(open);
          if (!open) setEditingEmployee(null);
        }}
        onSubmit={editingEmployee ? handleEdit : handleAdd}
        initialData={editingEmployee}
      />
    </div>
  );
};

export default Employees;
