import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "../App";
import Dashboard from "../pages/Dashboard";
import Employees from "../pages/Employees";
import EmployeeDetails from "../pages/EmployeeDetails";
import Leaves from "../pages/Leaves";
import Analytics from "../pages/Analytics";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />, // App is a layout component
    children: [
      { index: true, element: <Dashboard /> },
      { path: "employees", element: <Employees /> },
      { path: "employees/:id", element: <EmployeeDetails /> },
      { path: "leaves", element: <Leaves /> },
      { path: "analytics", element: <Analytics /> },
    ],
  },
]);

export default function Router() {
  return <RouterProvider router={router} />;
}
