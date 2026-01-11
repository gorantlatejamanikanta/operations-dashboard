"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

interface RegionalData {
  region: string;
  cost: number;
}

interface RegionalChartProps {
  data: RegionalData[];
}

const COLORS = {
  US: "#0088FE",
  EU: "#00C49F", 
  APAC: "#FFBB28"
};

export default function RegionalChart({ data }: RegionalChartProps) {
  // Format data for the chart
  const chartData = data.map((item) => ({
    ...item,
    cost: Number(item.cost),
    fill: COLORS[item.region as keyof typeof COLORS] || "#8884d8"
  }));

  const total = chartData.reduce((sum, item) => sum + item.cost, 0);

  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle>Regional Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ region, cost, percent }) => 
                  `${region}: ${(percent * 100).toFixed(1)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="cost"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => [`$${value.toLocaleString()}`, "Cost"]}
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px"
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        {data.length === 0 && (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            No regional data available
          </div>
        )}
        {total > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              Total Cost: <span className="font-semibold">${total.toLocaleString()}</span>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}