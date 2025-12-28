import { Edit, Trash2, Eye } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import dynamic from "next/dynamic";

const AlertDialog = dynamic(() => import("@/components/ui/alert-dialog"), {
  ssr: false,
});
const AlertDialogAction = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then((mod) => mod.AlertDialogAction),
  { ssr: false }
);
const AlertDialogCancel = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then((mod) => mod.AlertDialogCancel),
  { ssr: false }
);
const AlertDialogContent = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then(
      (mod) => mod.AlertDialogContent
    ),
  { ssr: false }
);
const AlertDialogDescription = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then(
      (mod) => mod.AlertDialogDescription
    ),
  { ssr: false }
);
const AlertDialogFooter = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then((mod) => mod.AlertDialogFooter),
  { ssr: false }
);
const AlertDialogHeader = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then((mod) => mod.AlertDialogHeader),
  { ssr: false }
);
const AlertDialogTitle = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then((mod) => mod.AlertDialogTitle),
  { ssr: false }
);
const AlertDialogTrigger = dynamic(
  () =>
    import("@/components/ui/alert-dialog").then(
      (mod) => mod.AlertDialogTrigger
    ),
  { ssr: false }
);
import { Employee } from "@/types";

interface EmployeeTableProps {
  data: Employee[];
  onEdit: (employee: Employee) => void;
  onDelete: (id: string) => void;
}

const EmployeeTable = ({ data, onEdit, onDelete }: EmployeeTableProps) => {
  const navigate = useNavigate();

  return (
    <div className="rounded-md border bg-card shadow-sm">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Department</TableHead>
            <TableHead>Position</TableHead>
            <TableHead>Salary</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={6}
                className="text-center h-24 text-muted-foreground"
              >
                No employees found.
              </TableCell>
            </TableRow>
          ) : (
            data.map((employee) => (
              <TableRow key={employee.id}>
                <TableCell className="font-medium">{employee.name}</TableCell>
                <TableCell>{employee.department}</TableCell>
                <TableCell>{employee.position}</TableCell>
                <TableCell>$ {employee.salary.toLocaleString()}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      employee.status === "Active" ? "default" : "secondary"
                    }
                    className={
                      employee.status === "Active"
                        ? "bg-green-600 hover:bg-green-700"
                        : ""
                    }
                  >
                    {employee.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => navigate(`/employees/${employee.id}`)}
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(employee)}
                      title="Edit"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>

                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This action cannot be undone. This will permanently
                            delete the employee record.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => onDelete(employee.id)}
                            className="bg-red-600 hover:bg-red-700"
                          >
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default EmployeeTable;
