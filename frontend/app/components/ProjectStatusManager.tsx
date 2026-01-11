"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { 
  Play, 
  Pause, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Search,
  Filter,
  Calendar,
  DollarSign,
  Users,
  Settings,
  Cloud
} from "lucide-react";

interface Project {
  id: number;
  project_name: string;
  project_type: string;
  member_firm: string;
  deployed_region: string;
  is_active: boolean;
  description?: string;
  engagement_manager?: string;
  project_startdate: string;
  project_enddate: string;
  status?: "planning" | "active" | "on-hold" | "completed" | "cancelled";
  progress?: number;
  budget?: number;
  spent?: number;
}

interface ProjectStatusManagerProps {
  onProjectUpdate?: () => void;
}

export default function ProjectStatusManager({ onProjectUpdate }: ProjectStatusManagerProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [regionFilter, setRegionFilter] = useState<string>("all");

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
      console.log('ProjectStatusManager - Projects loaded:', data);
      
      // Enhance projects with calculated status and progress
      const enhancedProjects = data.map((project: Project) => ({
        ...project,
        status: calculateProjectStatus(project),
        progress: calculateProgress(project),
        budget: Math.random() * 100000 + 50000, // Mock budget data
        spent: Math.random() * 80000 + 20000    // Mock spent data
      }));
      
      setProjects(enhancedProjects);
    } catch (error) {
      console.error("Error fetching projects:", error);
    } finally {
      setLoading(false);
    }
  };

  const calculateProjectStatus = (project: Project): "planning" | "active" | "on-hold" | "completed" | "cancelled" => {
    const now = new Date();
    const startDate = new Date(project.project_startdate);
    const endDate = new Date(project.project_enddate);

    if (!project.is_active) {
      return now > endDate ? "completed" : "cancelled";
    }
    
    if (now < startDate) {
      return "planning";
    } else if (now > endDate) {
      return "completed";
    } else {
      return "active";
    }
  };

  const calculateProgress = (project: Project): number => {
    const now = new Date();
    const startDate = new Date(project.project_startdate);
    const endDate = new Date(project.project_enddate);
    
    if (now < startDate) return 0;
    if (now > endDate) return 100;
    
    const totalDuration = endDate.getTime() - startDate.getTime();
    const elapsed = now.getTime() - startDate.getTime();
    
    return Math.round((elapsed / totalDuration) * 100);
  };

  const updateProjectStatus = async (projectId: number, newStatus: boolean) => {
    try {
      const response = await fetch(`${API_URL}/api/projects/${projectId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          'Authorization': `Bearer demo-token`,
        },
        body: JSON.stringify({ is_active: newStatus }),
      });

      if (response.ok) {
        fetchProjects();
        onProjectUpdate?.();
      }
    } catch (error) {
      console.error("Error updating project status:", error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "planning":
        return <Clock className="h-4 w-4" />;
      case "active":
        return <Play className="h-4 w-4" />;
      case "on-hold":
        return <Pause className="h-4 w-4" />;
      case "completed":
        return <CheckCircle className="h-4 w-4" />;
      case "cancelled":
        return <XCircle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "planning":
        return "bg-blue-500/20 text-blue-700 border-blue-500/30";
      case "active":
        return "bg-green-500/20 text-green-700 border-green-500/30";
      case "on-hold":
        return "bg-yellow-500/20 text-yellow-700 border-yellow-500/30";
      case "completed":
        return "bg-emerald-500/20 text-emerald-700 border-emerald-500/30";
      case "cancelled":
        return "bg-red-500/20 text-red-700 border-red-500/30";
      default:
        return "bg-gray-500/20 text-gray-700 border-gray-500/30";
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress < 30) return "bg-red-500";
    if (progress < 70) return "bg-yellow-500";
    return "bg-green-500";
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.engagement_manager?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.member_firm.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === "all" || project.status === statusFilter;
    const matchesRegion = regionFilter === "all" || project.deployed_region === regionFilter;
    
    return matchesSearch && matchesStatus && matchesRegion;
  });

  const statusCounts = projects.reduce((acc, project) => {
    acc[project.status || "unknown"] = (acc[project.status || "unknown"] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div className="grid gap-4 md:grid-cols-5">
        {Object.entries(statusCounts).map(([status, count]) => (
          <Card key={status} className="glass-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                {getStatusIcon(status)}
                <div>
                  <p className="text-sm font-medium capitalize">{status}</p>
                  <p className="text-2xl font-bold">{count}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Project Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Search Projects</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name, manager, or firm..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="all">All Statuses</option>
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on-hold">On Hold</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Region</label>
              <select
                value={regionFilter}
                onChange={(e) => setRegionFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="all">All Regions</option>
                <option value="US">US</option>
                <option value="EU">EU</option>
                <option value="APAC">APAC</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Projects List */}
      <div className="grid gap-4">
        {filteredProjects.map((project) => (
          <Card key={project.id} className="glass-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{project.project_name}</h3>
                    <Badge className={`${getStatusColor(project.status || "unknown")} border`}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(project.status || "unknown")}
                        <span className="capitalize">{project.status}</span>
                      </div>
                    </Badge>
                    <Badge variant="outline">{project.project_type}</Badge>
                    <Badge variant="secondary">{project.deployed_region}</Badge>
                  </div>
                  
                  <p className="text-muted-foreground mb-3">{project.description}</p>
                  
                  <div className="grid gap-4 md:grid-cols-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Manager</p>
                        <p className="text-muted-foreground">{project.engagement_manager || "Not assigned"}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Timeline</p>
                        <p className="text-muted-foreground">
                          {new Date(project.project_startdate).toLocaleDateString()} - {new Date(project.project_enddate).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Budget</p>
                        <p className="text-muted-foreground">
                          ${project.spent?.toLocaleString()} / ${project.budget?.toLocaleString()}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <p className="font-medium mb-1">Progress</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getProgressColor(project.progress || 0)}`}
                            style={{ width: `${project.progress || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-xs font-medium">{project.progress || 0}%</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-2 ml-4">
                  <Button
                    variant={project.is_active ? "destructive" : "default"}
                    size="sm"
                    onClick={() => updateProjectStatus(project.id, !project.is_active)}
                  >
                    {project.is_active ? (
                      <>
                        <Pause className="h-4 w-4 mr-1" />
                        Pause
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Activate
                      </>
                    )}
                  </Button>
                  
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-1" />
                    Manage
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <Card className="glass-card">
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No projects match your current filters.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}