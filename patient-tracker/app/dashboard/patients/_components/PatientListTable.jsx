import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Trash, Search, Bell, Pencil } from "lucide-react";
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
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

function PatientListTable({ reload, setReload }) {
  const pagination = true;
  const paginationPageSize = 10;
  const paginationPageSizeSelector = [25, 50, 100];
  const gridRef = useRef(null);

  const [rowData, setRowData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchInput, setSearchInput] = useState("");
  const [editOpen, setEditOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const [editForm, setEditForm] = useState({
    full_name: "",
    phone_number: "",
    age: "",
    gender: "",
    target_duration_week: "",
    moderate_hr_min: "",
    moderate_hr_max: "",
    vigorous_hr_min: "",
    vigorous_hr_max: "",
    medical_condition: "",
    disability_level: "",
  });

  const openEdit = (row) => {
    setEditing(row);
    setEditForm({
      full_name: row.full_name || "",
      phone_number: row.phone_number || "",
      age: String(row.age || ""),
      gender: row.gender || "",
      target_duration_week: String(row.target_duration_week || ""),
      moderate_hr_min: String(row.moderate_hr_min || ""),
      moderate_hr_max: String(row.moderate_hr_max || ""),
      vigorous_hr_min: String(row.vigorous_hr_min || ""),
      vigorous_hr_max: String(row.vigorous_hr_max || ""),
      medical_condition: row.medical_condition || "",
      disability_level: row.disability_level || "",
    });
    setEditOpen(true);
  };

  const submitEdit = async () => {
    try {
      const updates = { ...editForm };
      // cast numeric fields if present
      ["age","target_duration_week","moderate_hr_min","moderate_hr_max","vigorous_hr_min","vigorous_hr_max"].forEach((k)=>{
        if (updates[k] === "" || updates[k] === null || updates[k] === undefined) return;
        const n = Number(updates[k]);
        if (!Number.isNaN(n)) updates[k] = n;
      });

      // 调试信息
      console.log('=== UPDATE PATIENT DEBUG ===');
      console.log('Environment variables:');
      console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
      console.log('NEXT_PUBLIC_API_PORT:', process.env.NEXT_PUBLIC_API_PORT);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3005';
      const fullUrl = `${apiUrl}/api/data/update-patient`;
      console.log('Full API URL:', fullUrl);
      console.log('Request data:', { id: editing.id, updates });
      
      const res = await fetch(fullUrl, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: editing.id, updates })
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Update failed: ${res.status} ${txt}`);
      }
      toast.success("Patient updated");
      setEditOpen(false);
      setEditing(null);
      setReload(true);
    } catch (e) {
      console.error(e);
      toast.error("Failed to update patient");
    }
  };

  const UploadReportButton = (props) => {
    const fileInputRef = useRef();

    const handleFileChange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      if (!props.data.phone_number) {
        toast.error("No phone number on this patient");
        return;
      }
      const formData = new FormData();
      formData.append("files", file);
      formData.append("phone", props.data.phone_number);
      
      // 调试信息
      console.log('=== UPLOAD WORKOUT DEBUG ===');
      console.log('Environment variables:');
      console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
      console.log('NEXT_PUBLIC_API_PORT:', process.env.NEXT_PUBLIC_API_PORT);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3005';
      const fullUrl = `${apiUrl}/parser/upload-workout`;
      console.log('Full API URL:', fullUrl);
      console.log('File details:', {
        name: file.name,
        size: file.size,
        type: file.type
      });
      console.log('Phone number:', props.data.phone_number);
      
      // FormData 内容检查
      console.log('FormData contents:');
      Array.from(formData.entries()).forEach(([key, value]) => {
        console.log(`${key}:`, value);
      });
      
      try {
        console.log('=== STARTING UPLOAD FETCH ===');
        const res = await fetch(fullUrl, {
          method: "POST",
          body: formData,
        });
        
        console.log('=== UPLOAD RESPONSE ===');
        console.log('Response status:', res.status);
        console.log('Response ok:', res.ok);
        const data = await res.json();
        console.log('Response data:', data);
        toast.success(data.message || "Upload completed");
      } catch (err) {
        console.log('=== UPLOAD ERROR ===');
        console.error('Error details:', err);
        console.log('Error name:', err.name);
        console.log('Error message:', err.message);
        console.log('Error stack:', err.stack);
        toast.error(`Upload failed: ${err.message}`);
      }
    };

    return (
      <>
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current.click()}
        >
          Upload Report
        </Button>
        <input
          type="file"
          accept=".txt"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileChange}
        />
      </>
    );
  };

  const CustomButtons = (props) => {
    return (
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => openEdit(props.data)}
        >
          <Pencil className="h-4 w-4" />
        </Button>
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
          onClick={() => sendNotification(props.data)}
        >
          <Bell className="h-4 w-4" />
        </Button>
        <UploadReportButton data={props.data} />
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

      const fullUrl = `${apiUrl}/api/data/get-patients`;
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
        `${process.env.NEXT_PUBLIC_API_URL}/api/data/delete-patient`,
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

  const sendNotification = async (patient) => {
    try {
      const response = await fetch("http://localhost:5000/notifications/send", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            phone_number: patient.phone_number,
            message: `Hi ${patient.full_name}! 👋\n\n这是您的运动提醒！🏃‍♀️\n\n是时候进行一些运动来保持健康了。您可以：\n• 散步15-30分钟\n• 做一些简单的伸展运动\n• 进行轻度有氧运动\n\n记住，任何运动都比不运动要好！💪\n\n如果您有任何问题，请随时联系我们。`,
            template_name: "hello_world",
            template_lang: "en_US"
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.status === "success") {
        toast.success(`通知已发送给 ${patient.full_name}`);
      } else {
        toast.error("通知发送失败");
      }
    } catch (error) {
      console.error("Error sending notification:", error);
      toast.error("发送通知失败");
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
        <Dialog open={editOpen} onOpenChange={setEditOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Patient</DialogTitle>
            </DialogHeader>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label>Name</label>
                <Input value={editForm.full_name} onChange={(e)=>setEditForm({...editForm, full_name: e.target.value})} />
              </div>
              <div>
                <label>Phone</label>
                <Input value={editForm.phone_number} onChange={(e)=>setEditForm({...editForm, phone_number: e.target.value})} />
              </div>
              <div>
                <label>Age</label>
                <Input value={editForm.age} onChange={(e)=>setEditForm({...editForm, age: e.target.value})} />
              </div>
              <div>
                <label>Gender</label>
                <Input value={editForm.gender} onChange={(e)=>setEditForm({...editForm, gender: e.target.value})} />
              </div>
              <div>
                <label>Weekly Target (min)</label>
                <Input value={editForm.target_duration_week} onChange={(e)=>setEditForm({...editForm, target_duration_week: e.target.value})} />
              </div>
              <div>
                <label>Moderate HR Min</label>
                <Input value={editForm.moderate_hr_min} onChange={(e)=>setEditForm({...editForm, moderate_hr_min: e.target.value})} />
              </div>
              <div>
                <label>Moderate HR Max</label>
                <Input value={editForm.moderate_hr_max} onChange={(e)=>setEditForm({...editForm, moderate_hr_max: e.target.value})} />
              </div>
              <div>
                <label>Vigorous HR Min</label>
                <Input value={editForm.vigorous_hr_min} onChange={(e)=>setEditForm({...editForm, vigorous_hr_min: e.target.value})} />
              </div>
              <div>
                <label>Vigorous HR Max</label>
                <Input value={editForm.vigorous_hr_max} onChange={(e)=>setEditForm({...editForm, vigorous_hr_max: e.target.value})} />
              </div>
              <div className="col-span-2">
                <label>Medical Condition</label>
                <Input value={editForm.medical_condition} onChange={(e)=>setEditForm({...editForm, medical_condition: e.target.value})} />
              </div>
              <div className="col-span-2">
                <label>Disability Level</label>
                <Input value={editForm.disability_level} onChange={(e)=>setEditForm({...editForm, disability_level: e.target.value})} />
              </div>
              <div className="col-span-2 flex justify-end gap-2 mt-2">
                <Button variant="outline" onClick={()=>setEditOpen(false)}>Cancel</Button>
                <Button onClick={submitEdit}>Save</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      )}
    </div>
  );
}

export default PatientListTable;
