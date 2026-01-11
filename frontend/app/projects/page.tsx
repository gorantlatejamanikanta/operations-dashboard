"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Edit, Trash2, ArrowLeft, BarChart3, FileText, List } from "lucide-react";
import ProjectForm from "@/app/components/ProjectForm";
import ProjectStatusManager from "@/app/components/ProjectStatusManager";
import ProjectIntakeForm from "@/app/components/ProjectIntakeForm";
import { ThemeToggle } from "@/app/components/ThemeToggle";
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
  const [showIntakeForm, setShowIntakeForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "status">("status");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_URL}/api/projects/`, {
        headers: {
          'Authorization': `Bearer demo-token`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      
      const data = await response.json();
      console.log('Projects loaded:', data);
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
        headers: {
          'Authorization': `Bearer demo-token`,
        },
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

  const handleFormSuccess = () => {
    setShowForm(false);
    setShowIntakeForm(false);
    setEditingProject(null);
    fetchProjects();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Show intake form if selected
  if (showIntakeForm) {
    return (
      <div className="min-h-screen p-6 md:p-8 lg:p-12">
        <div className="max-w-7xl mx-auto">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
          <ProjectIntakeForm 
            onSuccess={handleFormSuccess}
            onCancel={() => setShowIntakeForm(false)}
          />
        </div>
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
            <h1 className="text-4xl font-bold tracking-tight">Project Management</h1>
            <p className="text-muted-foreground mt-2">
              Manage your cloud operations projects and track their status
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <ThemeToggle />
            <Button
              variant={viewMode === "status" ? "default" : "outline"}
              onClick={() => setViewMode("status")}
            >
              <BarChart3 className="mr-2 h-4 w-4" />
              Status View
            </Button>
            <Button
              variant={viewMode === "list" ? "default" : "outline"}
              onClick={() => setViewMode("list")}
            >
              <List className="mr-2 h-4 w-4" />
              List View
            </Button>
            <Button 
              onClick={() => setShowIntakeForm(true)} 
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <FileText className="mr-2 h-4 w-4" />
              Project Intake Form
            </Button>
            <Button 
              onClick={() => setShowForm(!showForm)} 
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              <Plus className="mr-2 h-4 w-4" />
              {showForm ? "Cancel" : "Quick Add"}
            </Button>
          </div>
        </div>

        {/* Project Form */}
        {showForm && (
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>{editingProject ? "Edit Project" : "Quick Add Project"}</CardTitle>
              <p className="text-sm text-muted-foreground">
                For comprehensive project setup, use the Project Intake Form above.
              </p>
            </CardHeader>
            <CardContent>
              <ProjectForm
                editProject={editingProject}
                onSuccess={handleFormSuccess}
              />
            </CardContent>
          </Card>
        )}

        {/* Content based on view mode */}
        {viewMode === "status" ? (
          <ProjectStatusManager onProjectUpdate={fetchProjects} />
        ) : (
          /* List View */
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
        )}

        {projects.length === 0 && (
          <Card className="glass-card">
            <CardContent className="py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
              <p className="text-muted-foreground mb-4">Get started by creating your first project</p>
              <div className="flex gap-2 justify-center">
                <Button onClick={() => setShowIntakeForm(true)} className="bg-blue-600 hover:bg-blue-700">
                  <FileText className="mr-2 h-4 w-4" />
                  Start Project Intake
                </Button>
                <Button variant="outline" onClick={() => setShowForm(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Quick Add Project
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
