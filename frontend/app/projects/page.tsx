"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Edit, Trash2, ArrowLeft } from "lucide-react";
import ProjectForm from "@/app/components/ProjectForm";
import Link from "next/link";

interface Project {
  id: number;
  project_name: string;
  project_type: string;
  member_firm: string;
  deployed_region: string;
  is_active: boolean;
  description?: string;
  engagement_code?: string;
  engagement_partner?: string;
  opportunity_code?: string;
  engagement_manager?: string;
  project_startdate: string;
  project_enddate: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_URL}/api/projects/`);
      const data = await response.json();
      setProjects(data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this project?")) return;

    try {
      const response = await fetch(`${API_URL}/api/projects/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        fetchProjects();
      } else {
        alert("Failed to delete project");
      }
    } catch (error) {
      console.error("Error deleting project:", error);
      alert("Error deleting project");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-8 lg:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <Link href="/">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
            <h1 className="text-4xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground mt-2">
              Manage your cloud operations projects
            </p>
          </div>
          <Button onClick={() => setShowForm(!showForm)} className="glass-card">
            <Plus className="mr-2 h-4 w-4" />
            {showForm ? "Cancel" : "Add Project"}
          </Button>
        </div>

        {/* Project Form */}
        {showForm && (
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>{editingProject ? "Edit Project" : "New Project"}</CardTitle>
            </CardHeader>
            <CardContent>
              <ProjectForm
                onSuccess={() => {
                  setShowForm(false);
                  setEditingProject(null);
                  fetchProjects();
                }}
              />
            </CardContent>
          </Card>
        )}

        {/* Projects List */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Card key={project.id} className="glass-card">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-xl">{project.project_name}</CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingProject(project);
                        setShowForm(true);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(project.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex gap-2 mt-2">
                  <span className="text-xs px-2 py-1 bg-primary/20 rounded">
                    {project.project_type}
                  </span>
                  <span className="text-xs px-2 py-1 bg-secondary/50 rounded">
                    {project.deployed_region}
                  </span>
                  {project.is_active && (
                    <span className="text-xs px-2 py-1 bg-green-500/20 rounded">
                      Active
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <p className="text-muted-foreground">{project.description || "No description"}</p>
                  {project.member_firm && (
                    <p><strong>Member Firm:</strong> {project.member_firm}</p>
                  )}
                  {project.engagement_manager && (
                    <p><strong>Manager:</strong> {project.engagement_manager}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {new Date(project.project_startdate).toLocaleDateString()} - {new Date(project.project_enddate).toLocaleDateString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {projects.length === 0 && (
          <Card className="glass-card">
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No projects yet. Create your first project to get started.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
