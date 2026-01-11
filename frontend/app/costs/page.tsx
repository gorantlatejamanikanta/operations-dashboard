"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Plus, Loader2 } from "lucide-react";
import Link from "next/link";

interface Cost {
  project_id: number;
  resource_group_id: number;
  month: string;
  cost: number;
}

interface Project {
  id: number;
  project_name: string;
}

interface ResourceGroup {
  id: number;
  resource_group_name: string;
  project_id: number;
}

export default function CostsPage() {
  const [costs, setCosts] = useState<Cost[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [resourceGroups, setResourceGroups] = useState<ResourceGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    project_id: "",
    resource_group_id: "",
    month: new Date().toISOString().split("T")[0].substring(0, 7) + "-01",
    cost: "",
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (formData.project_id) {
      fetchResourceGroups(parseInt(formData.project_id));
    }
  }, [formData.project_id]);

  const fetchData = async () => {
    try {
      const [costsRes, projectsRes] = await Promise.all([
        fetch(`${API_URL}/api/costs/monthly`),
        fetch(`${API_URL}/api/projects/`),
      ]);

      const [costsData, projectsData] = await Promise.all([
        costsRes.json(),
        projectsRes.json(),
      ]);

      setCosts(costsData);
      setProjects(projectsData);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchResourceGroups = async (projectId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/resource-groups/?project_id=${projectId}`);
      const data = await response.json();
      setResourceGroups(data);
    } catch (error) {
      console.error("Error fetching resource groups:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/api/costs/monthly`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_id: parseInt(formData.project_id),
          resource_group_id: parseInt(formData.resource_group_id),
          month: formData.month,
          cost: parseFloat(formData.cost),
        }),
      });

      if (response.ok) {
        setShowForm(false);
        setFormData({
          project_id: "",
          resource_group_id: "",
          month: new Date().toISOString().split("T")[0].substring(0, 7) + "-01",
          cost: "",
        });
        fetchData();
        alert("Cost added successfully!");
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || "Failed to add cost"}`);
      }
    } catch (error) {
      console.error("Error adding cost:", error);
      alert("Error adding cost");
    }
  };

  const getProjectName = (projectId: number) => {
    return projects.find((p) => p.id === projectId)?.project_name || `Project ${projectId}`;
  };

  const getResourceGroupName = (resourceGroupId: number) => {
    return resourceGroups.find((rg) => rg.id === resourceGroupId)?.resource_group_name || `RG ${resourceGroupId}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-8 lg:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-start">
          <div>
            <Link href="/">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
            <h1 className="text-4xl font-bold tracking-tight">Cost Management</h1>
            <p className="text-muted-foreground mt-2">View and manage monthly costs</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)} className="glass-card">
            <Plus className="mr-2 h-4 w-4" />
            {showForm ? "Cancel" : "Add Cost"}
          </Button>
        </div>

        {showForm && (
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>Add Monthly Cost</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Project *</label>
                    <select
                      value={formData.project_id}
                      onChange={(e) => setFormData({ ...formData, project_id: e.target.value, resource_group_id: "" })}
                      required
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Select project</option>
                      {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.project_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-1 block">Resource Group *</label>
                    <select
                      value={formData.resource_group_id}
                      onChange={(e) => setFormData({ ...formData, resource_group_id: e.target.value })}
                      required
                      disabled={!formData.project_id}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Select resource group</option>
                      {resourceGroups.map((rg) => (
                        <option key={rg.id} value={rg.id}>
                          {rg.resource_group_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-1 block">Month *</label>
                    <Input
                      type="month"
                      value={formData.month.substring(0, 7)}
                      onChange={(e) => setFormData({ ...formData, month: e.target.value + "-01" })}
                      required
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-1 block">Cost ($) *</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={formData.cost}
                      onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
                      required
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <Button type="submit">Add Cost</Button>
              </form>
            </CardContent>
          </Card>
        )}

        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Monthly Costs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Project</th>
                    <th className="text-left p-2">Resource Group</th>
                    <th className="text-left p-2">Month</th>
                    <th className="text-right p-2">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {costs.map((cost, index) => (
                    <tr key={index} className="border-b">
                      <td className="p-2">{getProjectName(cost.project_id)}</td>
                      <td className="p-2">{getResourceGroupName(cost.resource_group_id)}</td>
                      <td className="p-2">{new Date(cost.month).toLocaleDateString("en-US", { year: "numeric", month: "short" })}</td>
                      <td className="p-2 text-right">${cost.cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {costs.length === 0 && (
                <div className="py-8 text-center text-muted-foreground">
                  No costs found. Add your first cost entry above.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
