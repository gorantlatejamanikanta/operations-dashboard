"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, AlertCircle, RefreshCw, ArrowLeft } from "lucide-react";
import { ThemeToggle } from "@/app/components/ThemeToggle";
import Link from "next/link";

interface ServiceStatus {
  name: string;
  status: "healthy" | "unhealthy" | "unknown";
  message: string;
  responseTime?: number;
}

export default function StatusPage() {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const checkServices = async () => {
    setLoading(true);
    const newServices: ServiceStatus[] = [];

    // Check Backend API
    try {
      const start = Date.now();
      const response = await fetch(`${API_URL}/health`, { 
        method: 'GET',
        cache: 'no-cache'
      });
      const responseTime = Date.now() - start;
      
      if (response.ok) {
        newServices.push({
          name: "Backend API",
          status: "healthy",
          message: "API is responding normally",
          responseTime
        });
      } else {
        newServices.push({
          name: "Backend API",
          status: "unhealthy",
          message: `HTTP ${response.status}: ${response.statusText}`,
          responseTime
        });
      }
    } catch (error) {
      newServices.push({
        name: "Backend API",
        status: "unhealthy",
        message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }

    // Check Database Connection
    try {
      const start = Date.now();
      const response = await fetch(`${API_URL}/api/dashboard/stats`);
      const responseTime = Date.now() - start;
      
      if (response.ok) {
        newServices.push({
          name: "Database",
          status: "healthy",
          message: "Database queries executing successfully",
          responseTime
        });
      } else {
        newServices.push({
          name: "Database",
          status: "unhealthy",
          message: "Database queries failing",
          responseTime
        });
      }
    } catch (error) {
      newServices.push({
        name: "Database",
        status: "unhealthy",
        message: "Cannot connect to database"
      });
    }

    // Check Azure Configuration
    try {
      const response = await fetch(`${API_URL}/api/azure/configured`);
      if (response.ok) {
        const data = await response.json();
        newServices.push({
          name: "Azure Integration",
          status: data.configured ? "healthy" : "unknown",
          message: data.message
        });
      } else {
        newServices.push({
          name: "Azure Integration",
          status: "unknown",
          message: "Cannot check Azure configuration"
        });
      }
    } catch (error) {
      newServices.push({
        name: "Azure Integration",
        status: "unknown",
        message: "Azure configuration check failed"
      });
    }

    // Check AI Chatbot
    try {
      const response = await fetch(`${API_URL}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: "health check" })
      });
      
      if (response.ok) {
        newServices.push({
          name: "AI Chatbot",
          status: "healthy",
          message: "Chatbot is responding"
        });
      } else if (response.status === 500) {
        newServices.push({
          name: "AI Chatbot",
          status: "unknown",
          message: "Azure OpenAI not configured"
        });
      } else {
        newServices.push({
          name: "AI Chatbot",
          status: "unhealthy",
          message: "Chatbot service error"
        });
      }
    } catch (error) {
      newServices.push({
        name: "AI Chatbot",
        status: "unhealthy",
        message: "Cannot connect to chatbot service"
      });
    }

    setServices(newServices);
    setLastCheck(new Date());
    setLoading(false);
  };

  useEffect(() => {
    checkServices();
  }, []);

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'unknown':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return 'text-green-500';
      case 'unhealthy':
        return 'text-red-500';
      case 'unknown':
        return 'text-yellow-500';
    }
  };

  const overallStatus = services.length > 0 ? (
    services.every(s => s.status === 'healthy') ? 'healthy' :
    services.some(s => s.status === 'unhealthy') ? 'unhealthy' : 'unknown'
  ) : 'unknown';

  return (
    <div className="min-h-screen p-6 md:p-8 lg:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <Link href="/">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
            <h1 className="text-4xl font-bold tracking-tight">System Status</h1>
            <p className="text-muted-foreground mt-2">
              Monitor the health of all system components
            </p>
          </div>
          <div className="flex gap-2">
            <ThemeToggle />
            <Button onClick={checkServices} disabled={loading} className="glass-card">
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Overall Status */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(overallStatus)}
              Overall System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-lg font-semibold ${getStatusColor(overallStatus)}`}>
                  {overallStatus === 'healthy' ? 'All Systems Operational' :
                   overallStatus === 'unhealthy' ? 'Some Systems Down' :
                   'System Status Unknown'}
                </p>
                {lastCheck && (
                  <p className="text-sm text-muted-foreground">
                    Last checked: {lastCheck.toLocaleString()}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Service Status */}
        <div className="grid gap-4">
          {services.map((service, index) => (
            <Card key={index} className="glass-card">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(service.status)}
                    <div>
                      <h3 className="font-semibold">{service.name}</h3>
                      <p className="text-sm text-muted-foreground">{service.message}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${getStatusColor(service.status)}`}>
                      {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
                    </p>
                    {service.responseTime && (
                      <p className="text-sm text-muted-foreground">
                        {service.responseTime}ms
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {loading && (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Checking system status...</p>
          </div>
        )}

        {/* System Information */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>System Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h4 className="font-medium mb-2">Frontend</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>Next.js 15 (App Router)</li>
                  <li>React 18</li>
                  <li>TypeScript</li>
                  <li>Tailwind CSS</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Backend</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>FastAPI (Python)</li>
                  <li>SQLAlchemy ORM</li>
                  <li>PostgreSQL Database</li>
                  <li>Azure OpenAI Integration</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Features</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>Project Management</li>
                  <li>Cost Tracking</li>
                  <li>AI Chatbot</li>
                  <li>Azure Integration</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Configuration</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>API URL: {API_URL}</li>
                  <li>Environment: {process.env.NODE_ENV || 'development'}</li>
                  <li>Build: {new Date().toISOString().split('T')[0]}</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}