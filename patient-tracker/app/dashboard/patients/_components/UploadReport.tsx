import React, { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function UploadReport() {
  const [open, setOpen] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!phoneNumber) {
      toast.error("Please enter Phone Number.");
      return;
    }
    
    // 详细的调试信息
    console.log('=== UPLOAD DEBUG START ===');
    console.log('File details:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    });
    console.log('Phone number:', phoneNumber);
    
    // 环境变量检查
    console.log('Environment variables:');
    console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
    console.log('NEXT_PUBLIC_API_PORT:', process.env.NEXT_PUBLIC_API_PORT);
    console.log('NODE_ENV:', process.env.NODE_ENV);
    
    // 构建URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3005';
    const fullUrl = `${apiUrl}/parser/upload-workout`;
    console.log('Full API URL:', fullUrl);
    
    setUploading(true);
    const formData = new FormData();
    formData.append("files", file);
    formData.append("phone", phoneNumber);
    
    // FormData 内容检查
    console.log('FormData contents:');
    Array.from(formData.entries()).forEach(([key, value]) => {
      console.log(`${key}:`, value);
    });
    
    try {
      console.log('=== STARTING FETCH REQUEST ===');
      console.log('Request URL:', fullUrl);
      console.log('Request method: POST');
      console.log('Request body type:', formData.constructor.name);
      
      const res = await fetch(fullUrl, {
        method: "POST",
        body: formData,
      });
      
      console.log('=== FETCH RESPONSE ===');
      console.log('Response status:', res.status);
      console.log('Response statusText:', res.statusText);
      console.log('Response headers:', Object.fromEntries(res.headers.entries()));
      console.log('Response ok:', res.ok);
      
      const data = await res.json();
      console.log('Response data:', data);
      
      if (res.ok) {
        toast.success(data.message || "Upload completed");
        setOpen(false);
        setPhoneNumber("");
      } else {
        toast.error(data.message || "Upload failed");
      }
    } catch (err) {
      console.log('=== FETCH ERROR ===');
      console.error('Error details:', err);
      const error = err as Error;
      console.log('Error name:', error.name);
      console.log('Error message:', error.message);
      console.log('Error stack:', error.stack);
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
      console.log('=== UPLOAD DEBUG END ===');
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
            <label>Phone Number</label>
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