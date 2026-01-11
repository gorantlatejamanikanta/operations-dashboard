"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Loader2 } from "lucide-react";

interface ProjectFormProps {
  onSuccess?: () => void;
  editProject?: any;
}

export default function ProjectForm({ onSuccess, editProject }: ProjectFormProps) {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    project_name: editProject?.project_name || "",
    project_type: editProject?.project_type || "Internal",
    member_firm: editProject?.member_firm || "",
    deployed_region: editProject?.deployed_region || "US",
    is_active: editProject?.is_active ?? true,
    description: editProject?.description || "",
    engagement_code: editProject?.engagement_code || "",
    engagement_partner: editProject?.engagement_partner || "",
    opportunity_code: editProject?.opportunity_code || "",
    engagement_manager: editProject?.engagement_manager || "",
    project_startdate: editProject?.project_startdate || new Date().toISOString().split("T")[0],
    project_enddate: editProject?.project_enddate || new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = editProject 
        ? `${API_URL}/api/projects/${editProject.id}`
        : `${API_URL}/api/projects/`;
      
      const method = editProject ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          'Authorization': `Bearer demo-token`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowForm(false);
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
        onSuccess?.();
        alert(`Project ${editProject ? "updated" : "created"} successfully!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || `Failed to ${editProject ? "update" : "create"} project`}`);
      }
    } catch (error) {
      console.error("Error submitting project:", error);
      alert(`Error ${editProject ? "updating" : "creating"} project`);
    } finally {
      setLoading(false);
    }
  };

  if (!showForm && !editProject) {
    return (
      <Button 
        onClick={() => setShowForm(true)} 
        className="bg-primary hover:bg-primary/90 text-primary-foreground"
      >
        <Plus className="mr-2 h-4 w-4" />
        Add Project
      </Button>
    );
  }

  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle>{editProject ? "Edit Project" : "New Project"}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium mb-1 block">Project Name *</label>
              <Input
                value={formData.project_name}
                onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                required
                placeholder="Enter project name"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Project Type *</label>
              <select
                value={formData.project_type}
                onChange={(e) => setFormData({ ...formData, project_type: e.target.value })}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="Internal">Internal</option>
                <option value="External">External</option>
                <option value="Client Demo">Client Demo</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Member Firm *</label>
              <Input
                value={formData.member_firm}
                onChange={(e) => setFormData({ ...formData, member_firm: e.target.value })}
                required
                placeholder="Enter member firm"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Deployed Region *</label>
              <select
                value={formData.deployed_region}
                onChange={(e) => setFormData({ ...formData, deployed_region: e.target.value })}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="US">US</option>
                <option value="EU">EU</option>
                <option value="APAC">APAC</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Start Date *</label>
              <Input
                type="date"
                value={formData.project_startdate}
                onChange={(e) => setFormData({ ...formData, project_startdate: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">End Date *</label>
              <Input
                type="date"
                value={formData.project_enddate}
                onChange={(e) => setFormData({ ...formData, project_enddate: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Engagement Manager</label>
              <Input
                value={formData.engagement_manager}
                onChange={(e) => setFormData({ ...formData, engagement_manager: e.target.value })}
                placeholder="Enter engagement manager"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Engagement Partner</label>
              <Input
                value={formData.engagement_partner}
                onChange={(e) => setFormData({ ...formData, engagement_partner: e.target.value })}
                placeholder="Enter engagement partner"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Engagement Code</label>
              <Input
                value={formData.engagement_code}
                onChange={(e) => setFormData({ ...formData, engagement_code: e.target.value })}
                placeholder="Enter engagement code"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Opportunity Code</label>
              <Input
                value={formData.opportunity_code}
                onChange={(e) => setFormData({ ...formData, opportunity_code: e.target.value })}
                placeholder="Enter opportunity code"
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter project description"
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              rows={3}
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4"
            />
            <label htmlFor="is_active" className="text-sm font-medium">
              Active Project
            </label>
          </div>

          <div className="flex gap-2">
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {editProject ? "Updating..." : "Creating..."}
                </>
              ) : (
                editProject ? "Update Project" : "Create Project"
              )}
            </Button>
            {!editProject && (
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}