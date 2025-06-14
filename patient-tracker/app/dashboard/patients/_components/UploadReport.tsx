import React, { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function UploadReport() {
  const [open, setOpen] = useState(false);
  const [patientId, setPatientId] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!patientId && !phoneNumber) {
      toast.error("Please enter Patient ID or Phone Number.");
      return;
    }
    setUploading(true);
    const formData = new FormData();
    formData.append("files", file);
    if (patientId) formData.append("patientId", patientId);
    if (phoneNumber) formData.append("phone", phoneNumber);
    try {
      const res = await fetch("http://localhost:3005/parser/upload-workout", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        toast.success(data.message || "Upload completed");
        setOpen(false);
        setPatientId("");
        setPhoneNumber("");
      } else {
        toast.error(data.message || "Upload failed");
      }
    } catch (err) {
      toast.error("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Upload Report
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Exercise Report</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-3 mt-2">
            <label>Patient ID (optional)</label>
            <Input
              placeholder="Enter Patient ID"
              value={patientId}
              onChange={e => setPatientId(e.target.value)}
              type="text"
            />
            <label>Phone Number (optional)</label>
            <Input
              placeholder="Enter Phone Number"
              value={phoneNumber}
              onChange={e => setPhoneNumber(e.target.value)}
              type="text"
            />
            <label>Report File (.txt)</label>
            <Input
              type="file"
              accept=".txt"
              ref={fileInputRef}
              onChange={handleFileChange}
              disabled={uploading}
            />
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              variant="default"
            >
              {uploading ? "Uploading..." : "Select File"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
} 