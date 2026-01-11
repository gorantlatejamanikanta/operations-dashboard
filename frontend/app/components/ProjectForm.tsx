"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Loader2, Plus } from "lucide-react";

interface ProjectFormData {
  project_name: string;
  project_type: string;
  member_firm: string;
  deployed_region: string;
  is_active: boolean;
  description: string;
  engagement_code: string;
  engagement_partner: string;
  opportunity_code: string;
  engagement_manager: string;
  project_startdate: string;
  project_enddate: string;
}

export default function ProjectForm({ onSuccess }: { onSuccess?: () => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<ProjectFormData>({
    project_name: "",
    project_type: "Internal",
    member_firm: "",
    deployed_region: "US",
    is_active: true,
    description: "",
    engagement_code: "",
    engagement_partner: "",
    opportunity_code: "",
    engagement_manager: "",
    project_startdate: new Date().toISOString().split("T")[0],
    project_enddate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/api/projects/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create project");
      }

      const newProject = await response.json();
      console.log("Project created:", newProject);
      
      // Reset form
      setFormData({
        project_name: "",
        project_type: "Internal",
        member_firm: "",
        deployed_region: "US",
        is_active: true,
        description: "",
        engagement_code: "",
        engagement_partner: "",
        opportunity_code: "",
        engagement_manager: "",
        project_startdate: new Date().toISOString().split("T")[0],
        project_enddate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
      });

      setIsOpen(false);
      if (onSuccess) {
        onSuccess();
      }
      alert("Project created successfully!");
    } catch (error) {
      console.error("Error creating project:", error);
      alert(`Error: ${error instanceof Error ? error.message : "Failed to create project"}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  if (!isOpen) {
    return (
      <Button onClick={() => setIsOpen(true)} className="glass-card">
        <Plus className="mr-2 h-4 w-4" />
        Add New Project
      </Button>
    );
  }

  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle>Onboard New Project</CardTitle>
        <CardDescription>Create a new project in the system</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium mb-1 block">Project Name *</label>
              <Input
                name="project_name"
                value={formData.project_name}
                onChange={handleChange}
                required
                placeholder="Enter project name"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Project Type *</label>
              <select
                name="project_type"
                value={formData.project_type}
                onChange={handleChange}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="Internal">Internal</option>
                <option value="External">External</option>
                <option value="Client Demo">Client Demo</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Member Firm *</label>
              <Input
                name="member_firm"
                value={formData.member_firm}
                onChange={handleChange}
                required
                placeholder="e.g., US Office"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Deployed Region *</label>
              <select
                name="deployed_region"
                value={formData.deployed_region}
                onChange={handleChange}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="US">US</option>
                <option value="EU">EU</option>
                <option value="APAC">APAC</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Start Date *</label>
              <Input
                name="project_startdate"
                type="date"
                value={formData.project_startdate}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">End Date *</label>
              <Input
                name="project_enddate"
                type="date"
                value={formData.project_enddate}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Engagement Code</label>
              <Input
                name="engagement_code"
                value={formData.engagement_code}
                onChange={handleChange}
                placeholder="e.g., ENG-001"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Engagement Partner</label>
              <Input
                name="engagement_partner"
                value={formData.engagement_partner}
                onChange={handleChange}
                placeholder="Partner name"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Opportunity Code</label>
              <Input
                name="opportunity_code"
                value={formData.opportunity_code}
                onChange={handleChange}
                placeholder="e.g., OPP-001"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Engagement Manager</label>
              <Input
                name="engagement_manager"
                value={formData.engagement_manager}
                onChange={handleChange}
                placeholder="Manager name"
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Project description"
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData((prev) => ({ ...prev, is_active: e.target.checked }))}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="is_active" className="text-sm font-medium">
              Active Project
            </label>
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Project"
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
