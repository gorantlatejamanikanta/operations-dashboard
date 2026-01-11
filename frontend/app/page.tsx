"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import DashboardStats from "@/app/components/DashboardStats";
import CostChart from "@/app/components/CostChart";
import RegionalChart from "@/app/components/RegionalChart";
import ChatBot from "@/app/components/ChatBot";
import ProjectForm from "@/app/components/ProjectForm";
import AzureSyncButton from "@/app/components/AzureSyncButton";
import { ThemeToggle } from "@/app/components/ThemeToggle";
import { Cloud } from "lucide-react";
import Link from "next/link";

interface DashboardStatsData {
  total_projects: number;
  active_projects: number;
  total_cost: number;
}

interface CostTrend {
  month: string;
  cost: number;
}

interface RegionalData {
  region: string;
  cost: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStatsData>({
    total_projects: 0,
    active_projects: 0,
    total_cost: 0,
  });
  const [costTrends, setCostTrends] = useState<CostTrend[]>([]);
  const [regionalData, setRegionalData] = useState<RegionalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const headers = {
          'Authorization': `Bearer demo-token`,
        };

        const [statsRes, trendsRes, regionalRes] = await Promise.all([
          fetch(`${API_URL}/api/dashboard/stats`, { headers }),
          fetch(`${API_URL}/api/dashboard/cost-trends`, { headers }),
          fetch(`${API_URL}/api/dashboard/regional-distribution`, { headers }),
        ]);

        if (!statsRes.ok || !trendsRes.ok || !regionalRes.ok) {
          throw new Error('API request failed');
        }

        const [statsData, trendsData, regionalData] = await Promise.all([
          statsRes.json(),
          trendsRes.json(),
          regionalRes.json(),
        ]);

        console.log('Dashboard data loaded:', { statsData, trendsData, regionalData });

        setStats(statsData);
        setCostTrends(trendsData);
        setRegionalData(regionalData);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [API_URL, refreshKey]);

  const handleDataUpdate = () => {
    setRefreshKey((prev) => prev + 1);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-8 lg:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">Multi-Cloud Operations Dashboard</h1>
            <p className="text-muted-foreground">
              Monitor and manage your cloud operations across multiple regions
            </p>
          </div>
          <div className="flex gap-2 mt-4 flex-wrap">
            <ThemeToggle />
            <ProjectForm onSuccess={handleDataUpdate} />
            <AzureSyncButton onSuccess={handleDataUpdate} />
            <Link href="/cloud-onboarding">
              <Button variant="outline" className="glass-card">
                <Cloud className="mr-2 h-4 w-4" />
                Cloud Onboarding
              </Button>
            </Link>
            <Link href="/projects">
              <Button variant="outline" className="glass-card">
                View All Projects
              </Button>
            </Link>
            <Link href="/costs">
              <Button variant="outline" className="glass-card">
                Manage Costs
              </Button>
            </Link>
            <Link href="/status">
              <Button variant="outline" className="glass-card">
                System Status
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats */}
        <DashboardStats
          totalProjects={stats.total_projects}
          activeProjects={stats.active_projects}
          totalCost={stats.total_cost}
        />

        {/* Charts */}
        <div className="grid gap-6 md:grid-cols-2">
          <CostChart data={costTrends} />
          <RegionalChart data={regionalData} />
        </div>
      </div>

      {/* ChatBot */}
      <ChatBot />
    </div>
  );
}
