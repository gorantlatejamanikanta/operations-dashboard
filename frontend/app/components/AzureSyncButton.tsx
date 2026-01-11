"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Cloud, Loader2, X } from "lucide-react";

interface AzureSyncButtonProps {
  onSuccess?: () => void;
}

export default function AzureSyncButton({ onSuccess }: AzureSyncButtonProps) {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    project_id: "",
    resource_group_name: "",
    start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split("T")[0], // 90 days ago
    end_date: new Date().toISOString().split("T")[0], // today
    subscription_id: "",
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleSync = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/azure/sync-costs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          'Authorization': `Bearer demo-token`,
        },
        body: JSON.stringify({
          ...formData,
          project_id: parseInt(formData.project_id),
          subscription_id: formData.subscription_id || undefined,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setShowForm(false);
        setFormData({
          project_id: "",
          resource_group_name: "",
          start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
          end_date: new Date().toISOString().split("T")[0],
          subscription_id: "",
        });
        onSuccess?.();
        alert(`Successfully synced ${result.records_imported} cost records from Azure!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || "Failed to sync costs from Azure"}`);
      }
    } catch (error) {
      console.error("Error syncing Azure costs:", error);
      alert("Error syncing costs from Azure");
    } finally {
      setLoading(false);
    }
  };

  if (!showForm) {
    return (
      <Button onClick={() => setShowForm(true)} variant="outline" className="glass-card">
        <Cloud className="mr-2 h-4 w-4" />
        Sync from Azure
      </Button>
    );
  }

  return (
    <Card className="glass-card">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center">
            <Cloud className="mr-2 h-5 w-5" />
            Sync Costs from Azure
          </CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowForm(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSync} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium mb-1 block">Project ID *</label>
              <Input
                type="number"
                value={formData.project_id}
                onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                required
                placeholder="Enter project ID"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Resource Group Name *</label>
              <Input
                value={formData.resource_group_name}
                onChange={(e) => setFormData({ ...formData, resource_group_name: e.target.value })}
                required
                placeholder="Enter Azure resource group name"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Start Date *</label>
              <Input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">End Date *</label>
              <Input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="text-sm font-medium mb-1 block">Subscription ID (Optional)</label>
              <Input
                value={formData.subscription_id}
                onChange={(e) => setFormData({ ...formData, subscription_id: e.target.value })}
                placeholder="Leave empty to use default subscription"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <Cloud className="mr-2 h-4 w-4" />
                  Sync Costs
                </>
              )}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}