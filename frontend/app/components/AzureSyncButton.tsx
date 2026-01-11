"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Cloud, Loader2, CheckCircle2 } from "lucide-react";

interface AzureSyncButtonProps {
  projectId: number;
  resourceGroupName?: string;
}

export default function AzureSyncButton({ projectId, resourceGroupName = "" }: AzureSyncButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);
  const [resourceGroupNameInput, setResourceGroupNameInput] = useState(resourceGroupName);
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);
  const [message, setMessage] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const checkAzureConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/api/azure/configured`);
      const data = await response.json();
      setIsConfigured(data.configured);
      if (!data.configured) {
        setMessage(data.message);
      }
    } catch (error) {
      console.error("Error checking Azure config:", error);
      setIsConfigured(false);
    }
  };

  const handleSync = async () => {
    if (!resourceGroupNameInput.trim()) {
      alert("Please enter a resource group name");
      return;
    }

    setIsSyncing(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/azure/sync-costs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_id: projectId,
          resource_group_name: resourceGroupNameInput,
          start_date: `${startDate}T00:00:00Z`,
          end_date: `${endDate}T23:59:59Z`,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`✅ Successfully synced ${data.records_imported} cost records`);
        setTimeout(() => {
          setIsOpen(false);
          window.location.reload();
        }, 2000);
      } else {
        setMessage(`❌ Error: ${data.detail || "Failed to sync costs"}`);
      }
    } catch (error) {
      console.error("Error syncing costs:", error);
      setMessage("❌ Error: Failed to sync costs. Check console for details.");
    } finally {
      setIsSyncing(false);
    }
  };

  if (!isOpen) {
    return (
      <Button onClick={() => {
        setIsOpen(true);
        checkAzureConfig();
      }} variant="outline" className="glass-card">
        <Cloud className="mr-2 h-4 w-4" />
        Sync from Azure
      </Button>
    );
  }

  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle>Sync Costs from Azure</CardTitle>
        <CardDescription>
          Import cost data from Azure Cost Management API
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isConfigured === false && (
          <div className="p-3 bg-yellow-500/20 border border-yellow-500/50 rounded text-sm">
            ⚠️ Azure credentials not configured. Please set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, 
            AZURE_TENANT_ID, and AZURE_SUBSCRIPTION_ID in backend/.env
          </div>
        )}

        <div>
          <label className="text-sm font-medium mb-1 block">Resource Group Name *</label>
          <Input
            value={resourceGroupNameInput}
            onChange={(e) => setResourceGroupNameInput(e.target.value)}
            placeholder="e.g., rg-production"
            required
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="text-sm font-medium mb-1 block">Start Date *</label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">End Date *</label>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
          </div>
        </div>

        {message && (
          <div className={`p-3 rounded text-sm ${
            message.startsWith("✅") 
              ? "bg-green-500/20 border border-green-500/50" 
              : "bg-red-500/20 border border-red-500/50"
          }`}>
            {message}
          </div>
        )}

        <div className="flex gap-2 pt-4">
          <Button
            onClick={handleSync}
            disabled={isSyncing || !isConfigured}
            className="flex-1"
          >
            {isSyncing ? (
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
          <Button
            variant="outline"
            onClick={() => {
              setIsOpen(false);
              setMessage("");
            }}
            disabled={isSyncing}
          >
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
