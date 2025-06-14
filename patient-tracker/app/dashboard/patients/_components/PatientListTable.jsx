import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Trash, Search, Bell } from "lucide-react";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";

function PatientListTable({ reload, setReload }) {
  const pagination = true;
  const paginationPageSize = 10;
  const paginationPageSizeSelector = [25, 50, 100];
  const gridRef = useRef(null);

  const [rowData, setRowData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchInput, setSearchInput] = useState("");

  const CustomButtons = (props) => {
    return (
      <div className="flex gap-2">
        <AlertDialog>
          <AlertDialogTrigger>
            <Button variant="destructive" size="sm">
              <Trash className="h-4 w-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the
                patient's data.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => {
                  deletePatient(props.data.id);
                  setReload(true);
                }}
              >
                Continue
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
        <Button
          variant="outline"
          size="sm"
          onClick={() => sendNotification(props.data.patient_id)}
        >
          <Bell className="h-4 w-4" />
        </Button>
      </div>
    );
  };

  const [colDefs, setColDefs] = useState([
    { field: "id", headerName: "Patient ID", hide: true },
    { field: "full_name", headerName: "Name", filter: true },
    { field: "phone_number", headerName: "Phone Number", filter: true },
    { field: "age", headerName: "Age", filter: true, maxWidth: 100 },
    { field: "gender", headerName: "Gender", filter: true, maxWidth: 100 },
    {
      field: "medical_condition",
      headerName: "Medical Condition",
      filter: true,
    },
    { field: "disability_level", headerName: "Disability Level", filter: true },
    {
      field: "action",
      headerName: "Action",
      cellRenderer: CustomButtons,
      maxWidth: 120,
    },
  ]);

  const fetchPatients = async () => {
    setLoading(true); // 可选，确保一开始设置 loading 状态
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;

      if (!apiUrl) {
        throw new Error("Environment variable NEXT_PUBLIC_API_URL is not defined");
      }

      const fullUrl = `${apiUrl}/get-patients`;
      console.log("Fetching data from:", fullUrl);

      const response = await fetch(fullUrl);

      console.log("Response status:", response.status);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      console.log("Received data:", data);

      if (!data || !Array.isArray(data.patients)) {
        throw new Error("Invalid data format: 'patients' field is missing or not an array");
      }

      setRowData(data.patients);
    } catch (error) {
      console.error("Error during fetchPatients:", error);
      setError(error.message || "Failed to fetch patients data");
    } finally {
      setLoading(false);
    }
  };

  const deletePatient = async (patientId) => {
    try {
      const response = await fetch(     
        `${process.env.NEXT_PUBLIC_API_URL}/delete-patient`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: patientId }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      toast.success("Patient deleted successfully");
    } catch (error) {
      console.error("Error deleting patient:", error);
      toast.error("Failed to delete patient");
    }
  };

  const sendNotification = async (patientId) => {
    try {
      const response = await fetch("/notifications/send", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userId: patientId, // Using patientId here
            title: "FitBuddy: Exercise Time!",
            body: "Click on me to find something exciting to do. Get up and let's get moving!",
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      toast.success("Notification sent successfully");
    } catch (error) {
      console.error("Error sending notification:", error);
      toast.error("Failed to send notification");
    }
  };

  useEffect(() => {
    if (gridRef.current) {
      gridRef.current.api.sizeColumnsToFit();
    }
  }, [rowData]);

  useEffect(() => {
    setLoading(true);
    fetchPatients();
    setReload(false); // Reset reload after fetching data
  }, [reload]);

  return (
    <div style={{ marginTop: 30, marginBottom: 30 }}>
      {loading ? (
        <p>Loading data...</p>
      ) : error ? (
        <p>Error: {error}</p>
      ) : (
        <div className="ag-theme-quartz" style={{ height: 500 }}>
          <div className="flex justify-start" style={{ marginBottom: 15 }}>
            <div
              className="p-2 rounded-lg border shadow-sm flex items-center gap-2"
              style={{ width: "50%", maxWidth: "400px" }}
            >
              <Search className="text-gray-500" />
              <input
                type="text"
                placeholder="Search Patients"
                className="bg-white outline-none w-full p-1"
                onChange={(event) => setSearchInput(event.target.value)}
              />
            </div>
          </div>
          <AgGridReact
            rowData={rowData}
            columnDefs={colDefs}
            quickFilterText={searchInput}
            pagination={pagination}
            paginationPageSize={paginationPageSize}
            paginationPageSizeSelector={paginationPageSizeSelector}
            onGridReady={(params) => (gridRef.current = params)}
          />
        </div>
      )}
    </div>
  );
}

export default PatientListTable;
