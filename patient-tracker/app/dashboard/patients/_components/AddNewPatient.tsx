"use client";
import { Button } from "@/components/ui/button";
import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useForm, SubmitHandler } from "react-hook-form";
import { toast } from "sonner";


type Inputs = {
  full_name: string;
  gender: string;
  age: string;
  phone_number: string;
  moderate_hr_min: string;
  moderate_hr_max: string;
  vigorous_hr_min: string;
  vigorous_hr_max: string;
  target_duration_week: string;
  medical_condition: string;
  disability_level: string;
};

type AddNewPatientProps = {
  onPatientAdded: () => void;
};

function AddNewPatient({ onPatientAdded }: AddNewPatientProps) {
  const [open, setOpen] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<Inputs>();

  const moderate_hr_min = watch("moderate_hr_min");
  const vigorous_hr_min = watch("vigorous_hr_min");



  const addPatient = async (data: Inputs) => {
    try {
      const patientDetails = {
        full_name: data.full_name,
        gender: data.gender,
        age: data.age,
        phone_number: data.phone_number,
        moderate_hr_min: data.moderate_hr_min,
        moderate_hr_max: data.moderate_hr_max,
        vigorous_hr_min: data.vigorous_hr_min,
        vigorous_hr_max: data.vigorous_hr_max,
        target_duration_week: data.target_duration_week,
        medical_condition: data.medical_condition,
        disability_level: data.disability_level,
      };

      const addPatientResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/data/add-patient`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patientDetails),
        }
      );

      if (!addPatientResponse.ok) {
        if (addPatientResponse.status === 400) {
          const { message } = await addPatientResponse.json();
          toast.error(message);
          return;
        }

        toast.error("Failed to add patient details.");
        return;
      }

      toast.success("Patient details added successfully.");
      const { patientId } = await addPatientResponse.json();
      return patientId;
    } catch (error) {
      console.error("Error adding patient:", error);
      toast.error("Error adding patient.");
    }
  };

 
  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    try {
      const patientId = await addPatient(data); // ✅ 添加病人，只为写入 Supabase

      

      onPatientAdded(); // 刷新列表
      setOpen(false);   // 关闭弹窗
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Error submitting patient data.");
    }
  };


  return (
    <div>
      <Button onClick={() => setOpen(true)}>Add New Patient</Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent style={{ height: "80vh", overflowY: "scroll" }}>
          <DialogHeader>
            <DialogTitle>Add New Patient</DialogTitle>
            <DialogDescription>
              <form onSubmit={handleSubmit(onSubmit)}>
                <div className="py-3" id="full_name_field">
                  <label>Full Name</label>
                  <Input
                    placeholder="Enter Patient Full Name"
                    {...register("full_name", { required: true })}
                  />
                  {errors.full_name && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="gender_field">
                  <label>Gender</label>
                  <select
                    {...register("gender", { required: true })}
                    className="bg-white border rounded-md p-2 w-full"
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                  {errors.gender && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="age_field">
                  <label>Age</label>
                  <Input
                    type="number"
                    placeholder="Enter Patient Age"
                    {...register("age", { required: true })}
                  />
                  {errors.age && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="phone_number_field">
                    <label>Phone Number</label>
                    <Input
                      placeholder="Enter Patient Phone Number"
                      {...register("phone_number", { required: true })}
                    />
                    {errors.phone_number && (
                      <p className="text-red-500">This field is required</p>
                    )}
                </div>
                <div className="py-3" id="min_moderate_hr_field">
                  <label>Moderate Heart Rate (Min)</label>
                  <Input
                    type="number"
                    placeholder="Enter Min HR"
                    {...register("moderate_hr_min", { required: true })}
                  />
                  {errors.moderate_hr_min && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="max_moderate_hr_field">
                  <label>Moderate Heart Rate (Max)</label>
                  <Input
                    type="number"
                    placeholder="Enter Max HR"
                    {...register("moderate_hr_max", {
                      required: true,
                      validate: (value) =>
                        parseInt(value) > parseInt(moderate_hr_min) ||
                        "Max moderate heart rate must be more than min moderate heart rate",
                    })}
                  />
                  {errors.moderate_hr_max && (
                    <p className="text-red-500">
                      {errors.moderate_hr_max.message ||
                        "This field is required"}
                    </p>
                  )}
                </div>
                <div className="py-3" id="min_vigorous_hr_field">
                  <label>Vigorous Heart Rate (Min)</label>
                  <Input
                    type="number"
                    placeholder="Enter Min Vigorous HR"
                    {...register("vigorous_hr_min", { required: true })}
                  />
                  {errors.vigorous_hr_min && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="max_vigorous_hr_field">
                  <label>Vigorous Heart Rate (Max)</label>
                  <Input
                    type="number"
                    placeholder="Enter Max Vigorous HR"
                    {...register("vigorous_hr_max", {
                      required: true,
                      validate: (value) =>
                        parseInt(value) > parseInt(vigorous_hr_min) ||
                        "Max vigorous heart rate must be more than min vigorous heart rate",
                    })}
                  />
                  {errors.vigorous_hr_max && (
                    <p className="text-red-500">
                      {errors.vigorous_hr_max.message ||
                        "This field is required"}
                    </p>
                  )}
                </div>
                <div className="py-3" id="target_duration_field">
                  <label>Target Duration (Week)</label>
                  <Input
                    type="number"
                    placeholder="Enter Target Duration"
                    {...register("target_duration_week", { required: true })}
                  />
                  {errors.target_duration_week && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="medical_condition_field">
                  <label>Medical Condition</label>
                  <Input
                    placeholder="Enter Medical Condition"
                    {...register("medical_condition", { required: true })}
                  />
                  {errors.medical_condition && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>
                <div className="py-3" id="disability_level_field">
                  <label>Disability Level</label>
                  <select
                    {...register("disability_level", { required: true })}
                    className="bg-white border rounded-md p-2 w-full"
                  >
                    <option value="">Select Disability Level</option>
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                  </select>
                  {errors.disability_level && (
                    <p className="text-red-500">This field is required</p>
                  )}
                </div>


                <div className="flex gap-3 items-center justify-end mt-5">
                  <Button type="submit">Add</Button>
                  <Button type="button" onClick={() => setOpen(false)} variant="ghost">
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default AddNewPatient;

