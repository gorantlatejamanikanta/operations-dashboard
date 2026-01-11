"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  Loader2, 
  Calendar,
  DollarSign,
  Users,
  Building,
  Globe,
  Target,
  AlertCircle,
  CheckCircle,
  X
} from "lucide-react";

interface ProjectIntakeFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface IntakeFormData {
  // Basic Project Information
  project_name: string;
  project_description: string;
  project_type: string;
  business_justification: string;
  
  // Organizational Information
  member_firm: string;
  business_unit: string;
  department: string;
  cost_center: string;
  
  // Project Management
  project_sponsor: string;
  project_manager: string;
  engagement_manager: string;
  engagement_partner: string;
  technical_lead: string;
  
  // Timeline & Budget
  project_startdate: string;
  project_enddate: string;
  estimated_budget: string;
  budget_source: string;
  
  // Technical Requirements
  deployed_region: string;
  cloud_providers: string[];
  compliance_requirements: string[];
  security_classification: string;
  
  // Engagement Details
  engagement_code: string;
  opportunity_code: string;
  client_name: string;
  contract_type: string;
  
  // Risk & Compliance
  risk_assessment: string;
  data_classification: string;
  regulatory_requirements: string;
  
  // Additional Information
  success_criteria: string;
  assumptions: string;
  dependencies: string;
  constraints: string;
}

export default function ProjectIntakeForm({ onSuccess, onCancel }: ProjectIntakeFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  
  const [formData, setFormData] = useState<IntakeFormData>({
    project_name: "",
    project_description: "",
    project_type: "Internal",
    business_justification: "",
    
    member_firm: "",
    business_unit: "",
    department: "",
    cost_center: "",
    
    project_sponsor: "",
    project_manager: "",
    engagement_manager: "",
    engagement_partner: "",
    technical_lead: "",
    
    project_startdate: new Date().toISOString().split("T")[0],
    project_enddate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    estimated_budget: "",
    budget_source: "",
    
    deployed_region: "US",
    cloud_providers: [],
    compliance_requirements: [],
    security_classification: "Internal",
    
    engagement_code: "",
    opportunity_code: "",
    client_name: "",
    contract_type: "",
    
    risk_assessment: "Low",
    data_classification: "Internal",
    regulatory_requirements: "",
    
    success_criteria: "",
    assumptions: "",
    dependencies: "",
    constraints: ""
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const steps = [
    { id: 1, title: "Project Overview", icon: FileText },
    { id: 2, title: "Organization & Team", icon: Users },
    { id: 3, title: "Timeline & Budget", icon: Calendar },
    { id: 4, title: "Technical Requirements", icon: Globe },
    { id: 5, title: "Risk & Compliance", icon: AlertCircle },
    { id: 6, title: "Review & Submit", icon: CheckCircle }
  ];

  const handleInputChange = (field: string, value: string | string[]) => {
    setFormData({ ...formData, [field]: value });
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors({ ...errors, [field]: "" });
    }
  };

  const handleArrayToggle = (field: string, value: string) => {
    const currentArray = formData[field as keyof IntakeFormData] as string[];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    handleInputChange(field, newArray);
  };

  const validateStep = (step: number): boolean => {
    const newErrors: {[key: string]: string} = {};

    switch (step) {
      case 1:
        if (!formData.project_name.trim()) newErrors.project_name = "Project name is required";
        if (!formData.project_description.trim()) newErrors.project_description = "Project description is required";
        if (!formData.business_justification.trim()) newErrors.business_justification = "Business justification is required";
        break;
      
      case 2:
        if (!formData.member_firm.trim()) newErrors.member_firm = "Member firm is required";
        if (!formData.engagement_manager.trim()) newErrors.engagement_manager = "Engagement manager is required";
        break;
      
      case 3:
        if (!formData.project_startdate) newErrors.project_startdate = "Start date is required";
        if (!formData.project_enddate) newErrors.project_enddate = "End date is required";
        if (new Date(formData.project_startdate) >= new Date(formData.project_enddate)) {
          newErrors.project_enddate = "End date must be after start date";
        }
        break;
      
      case 4:
        if (formData.cloud_providers.length === 0) newErrors.cloud_providers = "At least one cloud provider must be selected";
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setLoading(true);
    try {
      // Convert form data to project format
      const projectData = {
        project_name: formData.project_name,
        project_type: formData.project_type,
        member_firm: formData.member_firm,
        deployed_region: formData.deployed_region,
        is_active: true,
        description: formData.project_description,
        engagement_code: formData.engagement_code,
        engagement_partner: formData.engagement_partner,
        opportunity_code: formData.opportunity_code,
        engagement_manager: formData.engagement_manager,
        project_startdate: formData.project_startdate,
        project_enddate: formData.project_enddate,
        
        // Additional intake fields (would need to extend backend schema)
        business_justification: formData.business_justification,
        business_unit: formData.business_unit,
        department: formData.department,
        cost_center: formData.cost_center,
        project_sponsor: formData.project_sponsor,
        project_manager: formData.project_manager,
        technical_lead: formData.technical_lead,
        estimated_budget: formData.estimated_budget ? parseInt(formData.estimated_budget) * 100 : null, // Convert to cents
        budget_source: formData.budget_source,
        cloud_providers: formData.cloud_providers.join(','),
        compliance_requirements: formData.compliance_requirements.join(','),
        security_classification: formData.security_classification,
        client_name: formData.client_name,
        contract_type: formData.contract_type,
        risk_assessment: formData.risk_assessment,
        data_classification: formData.data_classification,
        regulatory_requirements: formData.regulatory_requirements,
        success_criteria: formData.success_criteria,
        assumptions: formData.assumptions,
        dependencies: formData.dependencies,
        constraints: formData.constraints
      };

      const response = await fetch(`${API_URL}/api/projects/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(projectData),
      });

      if (response.ok) {
        onSuccess?.();
        alert("Project intake form submitted successfully!");
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || "Failed to submit project intake form"}`);
      }
    } catch (error) {
      console.error("Error submitting intake form:", error);
      alert("Error submitting project intake form");
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Project Overview</h3>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Project Name *</label>
              <Input
                value={formData.project_name}
                onChange={(e) => handleInputChange('project_name', e.target.value)}
                placeholder="Enter project name"
                className={errors.project_name ? "border-red-500" : ""}
              />
              {errors.project_name && <p className="text-red-500 text-xs mt-1">{errors.project_name}</p>}
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Project Type *</label>
              <select
                value={formData.project_type}
                onChange={(e) => handleInputChange('project_type', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="Internal">Internal</option>
                <option value="External">External</option>
                <option value="Client Demo">Client Demo</option>
                <option value="R&D">Research & Development</option>
                <option value="Proof of Concept">Proof of Concept</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Project Description *</label>
              <textarea
                value={formData.project_description}
                onChange={(e) => handleInputChange('project_description', e.target.value)}
                placeholder="Provide a detailed description of the project"
                className={`flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ${errors.project_description ? "border-red-500" : ""}`}
                rows={4}
              />
              {errors.project_description && <p className="text-red-500 text-xs mt-1">{errors.project_description}</p>}
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Business Justification *</label>
              <textarea
                value={formData.business_justification}
                onChange={(e) => handleInputChange('business_justification', e.target.value)}
                placeholder="Explain the business need and expected benefits"
                className={`flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ${errors.business_justification ? "border-red-500" : ""}`}
                rows={4}
              />
              {errors.business_justification && <p className="text-red-500 text-xs mt-1">{errors.business_justification}</p>}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Organization & Team</h3>
            
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1 block">Member Firm *</label>
                <Input
                  value={formData.member_firm}
                  onChange={(e) => handleInputChange('member_firm', e.target.value)}
                  placeholder="Enter member firm"
                  className={errors.member_firm ? "border-red-500" : ""}
                />
                {errors.member_firm && <p className="text-red-500 text-xs mt-1">{errors.member_firm}</p>}
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Business Unit</label>
                <Input
                  value={formData.business_unit}
                  onChange={(e) => handleInputChange('business_unit', e.target.value)}
                  placeholder="Enter business unit"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Department</label>
                <Input
                  value={formData.department}
                  onChange={(e) => handleInputChange('department', e.target.value)}
                  placeholder="Enter department"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Cost Center</label>
                <Input
                  value={formData.cost_center}
                  onChange={(e) => handleInputChange('cost_center', e.target.value)}
                  placeholder="Enter cost center code"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Project Sponsor</label>
                <Input
                  value={formData.project_sponsor}
                  onChange={(e) => handleInputChange('project_sponsor', e.target.value)}
                  placeholder="Enter project sponsor name"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Project Manager</label>
                <Input
                  value={formData.project_manager}
                  onChange={(e) => handleInputChange('project_manager', e.target.value)}
                  placeholder="Enter project manager name"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Engagement Manager *</label>
                <Input
                  value={formData.engagement_manager}
                  onChange={(e) => handleInputChange('engagement_manager', e.target.value)}
                  placeholder="Enter engagement manager name"
                  className={errors.engagement_manager ? "border-red-500" : ""}
                />
                {errors.engagement_manager && <p className="text-red-500 text-xs mt-1">{errors.engagement_manager}</p>}
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Engagement Partner</label>
                <Input
                  value={formData.engagement_partner}
                  onChange={(e) => handleInputChange('engagement_partner', e.target.value)}
                  placeholder="Enter engagement partner name"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Technical Lead</label>
                <Input
                  value={formData.technical_lead}
                  onChange={(e) => handleInputChange('technical_lead', e.target.value)}
                  placeholder="Enter technical lead name"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Timeline & Budget</h3>
            
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1 block">Project Start Date *</label>
                <Input
                  type="date"
                  value={formData.project_startdate}
                  onChange={(e) => handleInputChange('project_startdate', e.target.value)}
                  className={errors.project_startdate ? "border-red-500" : ""}
                />
                {errors.project_startdate && <p className="text-red-500 text-xs mt-1">{errors.project_startdate}</p>}
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Project End Date *</label>
                <Input
                  type="date"
                  value={formData.project_enddate}
                  onChange={(e) => handleInputChange('project_enddate', e.target.value)}
                  className={errors.project_enddate ? "border-red-500" : ""}
                />
                {errors.project_enddate && <p className="text-red-500 text-xs mt-1">{errors.project_enddate}</p>}
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Estimated Budget (USD)</label>
                <Input
                  type="number"
                  value={formData.estimated_budget}
                  onChange={(e) => handleInputChange('estimated_budget', e.target.value)}
                  placeholder="Enter estimated budget"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Budget Source</label>
                <select
                  value={formData.budget_source}
                  onChange={(e) => handleInputChange('budget_source', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select budget source</option>
                  <option value="Operating Budget">Operating Budget</option>
                  <option value="Capital Budget">Capital Budget</option>
                  <option value="Client Funded">Client Funded</option>
                  <option value="R&D Budget">R&D Budget</option>
                  <option value="Innovation Fund">Innovation Fund</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Engagement Code</label>
                <Input
                  value={formData.engagement_code}
                  onChange={(e) => handleInputChange('engagement_code', e.target.value)}
                  placeholder="Enter engagement code"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Opportunity Code</label>
                <Input
                  value={formData.opportunity_code}
                  onChange={(e) => handleInputChange('opportunity_code', e.target.value)}
                  placeholder="Enter opportunity code"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Client Name</label>
                <Input
                  value={formData.client_name}
                  onChange={(e) => handleInputChange('client_name', e.target.value)}
                  placeholder="Enter client name (if applicable)"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Contract Type</label>
                <select
                  value={formData.contract_type}
                  onChange={(e) => handleInputChange('contract_type', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select contract type</option>
                  <option value="Fixed Price">Fixed Price</option>
                  <option value="Time & Materials">Time & Materials</option>
                  <option value="Cost Plus">Cost Plus</option>
                  <option value="Internal">Internal</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Technical Requirements</h3>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Primary Deployment Region *</label>
              <select
                value={formData.deployed_region}
                onChange={(e) => handleInputChange('deployed_region', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="US">United States</option>
                <option value="EU">Europe</option>
                <option value="APAC">Asia Pacific</option>
                <option value="Global">Global</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-3 block">Cloud Providers *</label>
              <div className="grid gap-2 md:grid-cols-3">
                {['AWS', 'Azure', 'GCP', 'Multi-Cloud', 'On-Premises', 'Hybrid'].map((provider) => (
                  <label key={provider} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.cloud_providers.includes(provider)}
                      onChange={() => handleArrayToggle('cloud_providers', provider)}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">{provider}</span>
                  </label>
                ))}
              </div>
              {errors.cloud_providers && <p className="text-red-500 text-xs mt-1">{errors.cloud_providers}</p>}
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Security Classification</label>
              <select
                value={formData.security_classification}
                onChange={(e) => handleInputChange('security_classification', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="Public">Public</option>
                <option value="Internal">Internal</option>
                <option value="Confidential">Confidential</option>
                <option value="Restricted">Restricted</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-3 block">Compliance Requirements</label>
              <div className="grid gap-2 md:grid-cols-2">
                {['SOX', 'GDPR', 'HIPAA', 'PCI DSS', 'SOC 2', 'ISO 27001', 'FedRAMP', 'None'].map((requirement) => (
                  <label key={requirement} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.compliance_requirements.includes(requirement)}
                      onChange={() => handleArrayToggle('compliance_requirements', requirement)}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">{requirement}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Risk & Compliance</h3>
            
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1 block">Risk Assessment</label>
                <select
                  value={formData.risk_assessment}
                  onChange={(e) => handleInputChange('risk_assessment', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="Low">Low Risk</option>
                  <option value="Medium">Medium Risk</option>
                  <option value="High">High Risk</option>
                  <option value="Critical">Critical Risk</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-1 block">Data Classification</label>
                <select
                  value={formData.data_classification}
                  onChange={(e) => handleInputChange('data_classification', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="Public">Public</option>
                  <option value="Internal">Internal</option>
                  <option value="Confidential">Confidential</option>
                  <option value="Restricted">Restricted</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Regulatory Requirements</label>
              <textarea
                value={formData.regulatory_requirements}
                onChange={(e) => handleInputChange('regulatory_requirements', e.target.value)}
                placeholder="Describe any specific regulatory requirements"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Success Criteria</label>
              <textarea
                value={formData.success_criteria}
                onChange={(e) => handleInputChange('success_criteria', e.target.value)}
                placeholder="Define measurable success criteria for the project"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Key Assumptions</label>
              <textarea
                value={formData.assumptions}
                onChange={(e) => handleInputChange('assumptions', e.target.value)}
                placeholder="List key assumptions for the project"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Dependencies</label>
              <textarea
                value={formData.dependencies}
                onChange={(e) => handleInputChange('dependencies', e.target.value)}
                placeholder="Identify project dependencies"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Constraints</label>
              <textarea
                value={formData.constraints}
                onChange={(e) => handleInputChange('constraints', e.target.value)}
                placeholder="List any project constraints"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
              />
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold mb-4">Review & Submit</h3>
            
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Project Overview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div><strong>Name:</strong> {formData.project_name}</div>
                  <div><strong>Type:</strong> {formData.project_type}</div>
                  <div><strong>Description:</strong> {formData.project_description}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Team & Organization</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div><strong>Member Firm:</strong> {formData.member_firm}</div>
                  <div><strong>Engagement Manager:</strong> {formData.engagement_manager}</div>
                  <div><strong>Project Manager:</strong> {formData.project_manager || "Not specified"}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Timeline & Budget</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div><strong>Duration:</strong> {formData.project_startdate} to {formData.project_enddate}</div>
                  <div><strong>Budget:</strong> {formData.estimated_budget ? `$${parseInt(formData.estimated_budget).toLocaleString()}` : "Not specified"}</div>
                  <div><strong>Budget Source:</strong> {formData.budget_source || "Not specified"}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Technical Requirements</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div><strong>Region:</strong> {formData.deployed_region}</div>
                  <div><strong>Cloud Providers:</strong> {formData.cloud_providers.join(', ') || "None selected"}</div>
                  <div><strong>Security Classification:</strong> {formData.security_classification}</div>
                  <div><strong>Compliance:</strong> {formData.compliance_requirements.join(', ') || "None"}</div>
                </CardContent>
              </Card>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 mr-2" />
                <div className="text-sm">
                  <p className="font-medium text-yellow-800">Review Required</p>
                  <p className="text-yellow-700 mt-1">
                    Please review all information carefully before submitting. This intake form will be used to set up your project and cannot be easily modified after submission.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Card className="glass-card max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-6 w-6" />
          Project Intake Form
        </CardTitle>
        
        {/* Progress Steps */}
        <div className="flex items-center justify-between mt-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = currentStep === step.id;
            const isCompleted = currentStep > step.id;
            
            return (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                  isCompleted ? 'bg-green-500 border-green-500 text-white' :
                  isActive ? 'bg-primary border-primary text-white' :
                  'border-gray-300 text-gray-400'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <Icon className="h-4 w-4" />
                  )}
                </div>
                <div className="ml-2 hidden md:block">
                  <p className={`text-xs font-medium ${isActive ? 'text-primary' : 'text-gray-500'}`}>
                    {step.title}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-8 h-0.5 mx-2 ${isCompleted ? 'bg-green-500' : 'bg-gray-300'}`} />
                )}
              </div>
            );
          })}
        </div>
      </CardHeader>

      <CardContent>
        <div className="min-h-[500px]">
          {renderStepContent()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8 pt-6 border-t">
          <div>
            {currentStep > 1 && (
              <Button variant="outline" onClick={handlePrevious}>
                Previous
              </Button>
            )}
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={onCancel}>
              <X className="mr-2 h-4 w-4" />
              Cancel
            </Button>
            
            {currentStep < steps.length ? (
              <Button onClick={handleNext}>
                Next
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Submit Intake Form
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}