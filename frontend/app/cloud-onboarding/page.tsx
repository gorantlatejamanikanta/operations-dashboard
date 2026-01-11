"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/app/components/ThemeToggle";
import { 
  ArrowLeft, 
  Cloud, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Settings,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  RefreshCw,
  ExternalLink
} from "lucide-react";
import Link from "next/link";

interface CloudProvider {
  id: string;
  name: string;
  icon: string;
  color: string;
  status: "connected" | "disconnected" | "error" | "configuring";
  lastSync?: string;
  resourceCount?: number;
  monthlyCost?: number;
}

interface CloudConnection {
  id: string;
  provider: string;
  name: string;
  credentials: {
    [key: string]: string;
  };
  status: "active" | "inactive" | "error";
  lastSync?: string;
  regions?: string[];
}

export default function CloudOnboardingPage() {
  const [providers, setProviders] = useState<CloudProvider[]>([
    {
      id: "aws",
      name: "Amazon Web Services",
      icon: "🟠",
      color: "bg-orange-500",
      status: "disconnected",
    },
    {
      id: "azure",
      name: "Microsoft Azure",
      icon: "🔵",
      color: "bg-blue-500",
      status: "connected",
      lastSync: "2024-01-15T10:30:00Z",
      resourceCount: 24,
      monthlyCost: 15420.50
    },
    {
      id: "gcp",
      name: "Google Cloud Platform",
      icon: "🟡",
      color: "bg-yellow-500",
      status: "disconnected",
    }
  ]);

  const [connections, setConnections] = useState<CloudConnection[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string>("");
  const [showCredentials, setShowCredentials] = useState<{[key: string]: boolean}>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: "",
    provider: "",
    credentials: {} as {[key: string]: string}
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchProviderStatus();
    fetchConnections();
  }, []);

  const fetchProviderStatus = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_URL}/api/cloud-providers/status`, {
        headers: {
          'Authorization': `Bearer demo-token`,
        },
      });
      
      if (response.ok) {
        const providerStatuses = await response.json();
        console.log('Provider status loaded:', providerStatuses);
        
        // Update providers with real status data
        setProviders(providers.map(provider => {
          const status = providerStatuses.find((p: any) => p.provider === provider.id);
          if (status) {
            return {
              ...provider,
              status: status.status,
              lastSync: status.last_sync,
              resourceCount: status.resource_count,
              monthlyCost: status.monthly_cost
            };
          }
          return provider;
        }));
      } else {
        setError('Failed to fetch provider status');
      }
    } catch (error) {
      console.error('Error fetching provider status:', error);
      setError('Network error while fetching provider status');
    }
  };

  const fetchConnections = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_URL}/api/cloud-providers/connections`, {
        headers: {
          'Authorization': `Bearer demo-token`,
        },
      });
      
      if (response.ok) {
        const connectionsData = await response.json();
        console.log('Connections loaded:', connectionsData);
        
        // Transform backend data to frontend format
        const transformedConnections = connectionsData.map((conn: any) => ({
          id: conn.id.toString(),
          provider: conn.provider,
          name: conn.name,
          credentials: { status: "configured" }, // Don't expose real credentials
          status: conn.status,
          lastSync: conn.last_sync,
          regions: conn.regions || []
        }));
        
        setConnections(transformedConnections);
      } else {
        setError('Failed to fetch connections');
      }
    } catch (error) {
      console.error('Error fetching connections:', error);
      setError('Network error while fetching connections');
      // Fallback to empty array on error
      setConnections([]);
    }
  };

  const getProviderConfig = (provider: string) => {
    const configs = {
      aws: {
        fields: [
          { key: "access_key_id", label: "Access Key ID", type: "text", required: true },
          { key: "secret_access_key", label: "Secret Access Key", type: "password", required: true },
          { key: "region", label: "Default Region", type: "select", options: ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"], required: true },
          { key: "account_id", label: "Account ID", type: "text", required: false }
        ],
        docs: "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html"
      },
      azure: {
        fields: [
          { key: "subscription_id", label: "Subscription ID", type: "text", required: true },
          { key: "client_id", label: "Client ID (Application ID)", type: "text", required: true },
          { key: "client_secret", label: "Client Secret", type: "password", required: true },
          { key: "tenant_id", label: "Tenant ID (Directory ID)", type: "text", required: true }
        ],
        docs: "https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal"
      },
      gcp: {
        fields: [
          { key: "project_id", label: "Project ID", type: "text", required: true },
          { key: "service_account_key", label: "Service Account Key (JSON)", type: "textarea", required: true },
          { key: "region", label: "Default Region", type: "select", options: ["us-central1", "us-east1", "europe-west1", "asia-southeast1"], required: true }
        ],
        docs: "https://cloud.google.com/iam/docs/creating-managing-service-accounts"
      }
    };
    return configs[provider as keyof typeof configs];
  };

  const handleAddConnection = () => {
    setShowAddForm(true);
    setFormData({ name: "", provider: "", credentials: {} });
  };

  const handleProviderSelect = (provider: string) => {
    setSelectedProvider(provider);
    setFormData({ ...formData, provider });
  };

  const handleCredentialChange = (key: string, value: string) => {
    setFormData({
      ...formData,
      credentials: { ...formData.credentials, [key]: value }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/cloud-providers/connections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer demo-token`,
        },
        body: JSON.stringify({
          name: formData.name,
          provider: formData.provider,
          credentials: formData.credentials,
          description: `${formData.provider.toUpperCase()} connection for ${formData.name}`,
          auto_sync: true,
          sync_frequency: 3600
        }),
      });

      if (response.ok) {
        const newConnection = await response.json();
        
        // Refresh data
        await fetchConnections();
        await fetchProviderStatus();
        
        setShowAddForm(false);
        setSelectedProvider("");
        alert("Cloud connection added successfully!");
      } else {
        const error = await response.json();
        alert(`Error adding connection: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error adding connection:", error);
      alert("Error adding connection. Please check your network connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (connectionId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/cloud-providers/connections/${connectionId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer demo-token`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert(`Connection test successful! ${result.message}`);
          // Refresh connections to get updated status
          await fetchConnections();
          await fetchProviderStatus();
        } else {
          alert(`Connection test failed: ${result.message}`);
        }
      } else {
        const error = await response.json();
        alert(`Connection test failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error testing connection:", error);
      alert("Connection test failed! Please check your network connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleSyncConnection = async (connectionId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/cloud-providers/connections/${connectionId}/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer demo-token`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Sync completed! ${result.message}`);
        // Refresh data to show updated resource counts and costs
        await fetchConnections();
        await fetchProviderStatus();
      } else {
        const error = await response.json();
        alert(`Sync failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error syncing connection:", error);
      alert("Sync failed! Please check your network connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConnection = async (connectionId: string) => {
    if (!confirm("Are you sure you want to delete this connection?")) return;

    try {
      const response = await fetch(`${API_URL}/api/cloud-providers/connections/${connectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer demo-token`,
        },
      });

      if (response.ok) {
        // Refresh data
        await fetchConnections();
        await fetchProviderStatus();
        alert("Connection deleted successfully!");
      } else {
        const error = await response.json();
        alert(`Error deleting connection: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error deleting connection:", error);
      alert("Error deleting connection. Please check your network connection.");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
      case "active":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "disconnected":
      case "inactive":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case "configuring":
        return <Settings className="h-5 w-5 text-yellow-500 animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
      case "active":
        return "bg-green-500/20 text-green-700 border-green-500/30";
      case "disconnected":
      case "inactive":
        return "bg-red-500/20 text-red-700 border-red-500/30";
      case "error":
        return "bg-red-500/20 text-red-700 border-red-500/30";
      case "configuring":
        return "bg-yellow-500/20 text-yellow-700 border-yellow-500/30";
      default:
        return "bg-gray-500/20 text-gray-700 border-gray-500/30";
    }
  };

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
            <h1 className="text-4xl font-bold tracking-tight">Cloud Onboarding</h1>
            <p className="text-muted-foreground mt-2">
              Connect and manage your cloud provider integrations
            </p>
          </div>
          <div className="flex gap-3">
            <ThemeToggle />
            <Button 
              variant="outline" 
              onClick={() => {
                fetchProviderStatus();
                fetchConnections();
              }}
              disabled={loading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              onClick={handleAddConnection} 
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Connection
            </Button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Card className="glass-card border-red-500/50 bg-red-500/10">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setError(null)}
                  className="ml-auto"
                >
                  ×
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Provider Overview */}
        <div className="grid gap-6 md:grid-cols-3">
          {providers.map((provider) => (
            <Card key={provider.id} className="glass-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-lg ${provider.color} flex items-center justify-center text-2xl`}>
                      {provider.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{provider.name}</CardTitle>
                      <Badge className={`${getStatusColor(provider.status)} border mt-1`}>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(provider.status)}
                          <span className="capitalize">{provider.status}</span>
                        </div>
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {provider.status === "connected" && (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Resources:</span>
                      <span className="font-medium">{provider.resourceCount || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Monthly Cost:</span>
                      <span className="font-medium">${provider.monthlyCost?.toLocaleString() || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Last Sync:</span>
                      <span className="font-medium">
                        {provider.lastSync ? new Date(provider.lastSync).toLocaleDateString() : "Never"}
                      </span>
                    </div>
                  </div>
                )}
                {provider.status === "disconnected" && (
                  <p className="text-sm text-muted-foreground">
                    No active connections. Add a connection to start monitoring resources.
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Add Connection Form */}
        {showAddForm && (
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>Add Cloud Connection</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Provider Selection */}
                {!selectedProvider && (
                  <div>
                    <label className="text-sm font-medium mb-3 block">Select Cloud Provider</label>
                    <div className="grid gap-3 md:grid-cols-3">
                      {providers.map((provider) => (
                        <Button
                          key={provider.id}
                          type="button"
                          variant="outline"
                          className="h-20 flex-col gap-2"
                          onClick={() => handleProviderSelect(provider.id)}
                        >
                          <div className="text-2xl">{provider.icon}</div>
                          <span className="text-sm">{provider.name}</span>
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Configuration Form */}
                {selectedProvider && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">
                        Configure {providers.find(p => p.id === selectedProvider)?.name}
                      </h3>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const config = getProviderConfig(selectedProvider);
                          if (config?.docs) {
                            window.open(config.docs, '_blank');
                          }
                        }}
                      >
                        <ExternalLink className="mr-2 h-4 w-4" />
                        Documentation
                      </Button>
                    </div>

                    <div>
                      <label className="text-sm font-medium mb-1 block">Connection Name *</label>
                      <Input
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder={`My ${providers.find(p => p.id === selectedProvider)?.name} Account`}
                        required
                      />
                    </div>

                    {getProviderConfig(selectedProvider)?.fields.map((field) => (
                      <div key={field.key}>
                        <label className="text-sm font-medium mb-1 block">
                          {field.label} {field.required && "*"}
                        </label>
                        {field.type === "select" ? (
                          <select
                            value={formData.credentials[field.key] || ""}
                            onChange={(e) => handleCredentialChange(field.key, e.target.value)}
                            required={field.required}
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          >
                            <option value="">Select {field.label}</option>
                            {'options' in field && field.options?.map((option: string) => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </select>
                        ) : field.type === "textarea" ? (
                          <textarea
                            value={formData.credentials[field.key] || ""}
                            onChange={(e) => handleCredentialChange(field.key, e.target.value)}
                            required={field.required}
                            rows={4}
                            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            placeholder={`Enter ${field.label}`}
                          />
                        ) : (
                          <div className="relative">
                            <Input
                              type={field.type === "password" && !showCredentials[field.key] ? "password" : "text"}
                              value={formData.credentials[field.key] || ""}
                              onChange={(e) => handleCredentialChange(field.key, e.target.value)}
                              required={field.required}
                              placeholder={`Enter ${field.label}`}
                            />
                            {field.type === "password" && (
                              <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6"
                                onClick={() => setShowCredentials({
                                  ...showCredentials,
                                  [field.key]: !showCredentials[field.key]
                                })}
                              >
                                {showCredentials[field.key] ? (
                                  <EyeOff className="h-4 w-4" />
                                ) : (
                                  <Eye className="h-4 w-4" />
                                )}
                              </Button>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  {selectedProvider && (
                    <Button type="submit" disabled={loading}>
                      {loading ? (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Connecting...
                        </>
                      ) : (
                        "Add Connection"
                      )}
                    </Button>
                  )}
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => {
                      setShowAddForm(false);
                      setSelectedProvider("");
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Existing Connections */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Active Connections</CardTitle>
          </CardHeader>
          <CardContent>
            {connections.length === 0 ? (
              <div className="text-center py-8">
                <Cloud className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No cloud connections configured yet.</p>
                <p className="text-sm text-muted-foreground mt-1">Add your first connection to start monitoring resources.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {connections.map((connection) => (
                  <div key={connection.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded ${providers.find(p => p.id === connection.provider)?.color} flex items-center justify-center text-lg`}>
                          {providers.find(p => p.id === connection.provider)?.icon}
                        </div>
                        <div>
                          <h4 className="font-semibold">{connection.name}</h4>
                          <p className="text-sm text-muted-foreground capitalize">{connection.provider}</p>
                        </div>
                        <Badge className={`${getStatusColor(connection.status)} border`}>
                          <div className="flex items-center gap-1">
                            {getStatusIcon(connection.status)}
                            <span className="capitalize">{connection.status}</span>
                          </div>
                        </Badge>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTestConnection(connection.id)}
                          disabled={loading}
                        >
                          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                          Test
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleSyncConnection(connection.id)}
                          disabled={loading || connection.status !== "active"}
                        >
                          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                          Sync
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteConnection(connection.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid gap-2 md:grid-cols-3 text-sm">
                      <div>
                        <span className="text-muted-foreground">Last Sync:</span>
                        <p className="font-medium">
                          {connection.lastSync ? new Date(connection.lastSync).toLocaleString() : "Never"}
                        </p>
                      </div>
                      {connection.regions && (
                        <div>
                          <span className="text-muted-foreground">Regions:</span>
                          <p className="font-medium">{connection.regions.length} configured</p>
                        </div>
                      )}
                      <div>
                        <span className="text-muted-foreground">Credentials:</span>
                        <p className="font-medium">{Object.keys(connection.credentials).length} fields configured</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}