"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, DollarSign, Folder, TrendingUp } from "lucide-react";

interface DashboardStatsProps {
  totalProjects: number;
  activeProjects: number;
  totalCost: number;
}

export default function DashboardStats({ totalProjects, activeProjects, totalCost }: DashboardStatsProps) {
  const stats = [
    {
      title: "Total Projects",
      value: totalProjects,
      icon: Folder,
      change: "+12%",
    },
    {
      title: "Active Projects",
      value: activeProjects,
      icon: Activity,
      change: "+8%",
    },
    {
      title: "Total Cost",
      value: `$${totalCost.toLocaleString(undefined, { maximumFractionDigits: 2 })}`,
      icon: DollarSign,
      change: "+5.2%",
    },
    {
      title: "Cost Trend",
      value: "↑",
      icon: TrendingUp,
      change: "Positive",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <Card key={index} className="glass-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.change} from last month</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
