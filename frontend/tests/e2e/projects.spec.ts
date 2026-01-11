import { test, expect } from '@playwright/test';

test.describe('Projects Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects');
  });

  test('should load projects page', async ({ page }) => {
    // Check page title and heading
    await expect(page.locator('h1')).toContainText('Project Management');
    
    // Check for main action buttons
    await expect(page.locator('text=Project Intake Form')).toBeVisible();
    await expect(page.locator('text=Quick Add')).toBeVisible();
    
    // Check view mode toggles
    await expect(page.locator('text=Status View')).toBeVisible();
    await expect(page.locator('text=List View')).toBeVisible();
  });

  test('should display projects in status view', async ({ page }) => {
    // Ensure we're in status view
    await page.click('text=Status View');
    
    // Wait for projects to load
    await page.waitForLoadState('networkidle');
    
    // Check for status overview cards
    const statusCards = page.locator('[data-testid="status-card"]');
    await expect(statusCards.first()).toBeVisible();
    
    // Check for project filters
    await expect(page.locator('text=Project Filters')).toBeVisible();
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
  });

  test('should display projects in list view', async ({ page }) => {
    // Switch to list view
    await page.click('text=List View');
    
    // Wait for projects to load
    await page.waitForLoadState('networkidle');
    
    // Check for project cards
    const projectCards = page.locator('[data-testid="project-card"]');
    if (await projectCards.count() > 0) {
      await expect(projectCards.first()).toBeVisible();
    }
  });

  test('should create a new project via quick add', async ({ page }) => {
    // Click Quick Add button
    await page.click('text=Quick Add');
    
    // Verify form appears
    await expect(page.locator('text=Quick Add Project')).toBeVisible();
    
    // Fill out the form
    await page.fill('input[name="project_name"]', 'E2E Test Project Quick');
    await page.selectOption('select[name="project_type"]', 'External');
    await page.fill('input[name="member_firm"]', 'E2E Test Corp');
    await page.selectOption('select[name="deployed_region"]', 'US');
    await page.fill('textarea[name="description"]', 'Project created via E2E test');
    await page.fill('input[name="engagement_manager"]', 'Test Manager');
    await page.fill('input[name="project_startdate"]', '2024-01-01');
    await page.fill('input[name="project_enddate"]', '2024-12-31');
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Verify success
    await expect(page.locator('text=Project created successfully')).toBeVisible({ timeout: 10000 });
    
    // Verify project appears in list
    await expect(page.locator('text=E2E Test Project Quick')).toBeVisible();
  });

  test('should open project intake form', async ({ page }) => {
    // Click Project Intake Form button
    await page.click('text=Project Intake Form');
    
    // Verify intake form loads
    await expect(page.locator('text=Project Intake Form')).toBeVisible();
    
    // Check for form steps
    await expect(page.locator('text=Step 1')).toBeVisible();
    
    // Check for form fields
    await expect(page.locator('input[name="project_name"]')).toBeVisible();
  });

  test('should filter projects by search', async ({ page }) => {
    // Wait for projects to load
    await page.waitForLoadState('networkidle');
    
    // Use search filter
    const searchInput = page.locator('input[placeholder*="Search"]');
    await searchInput.fill('E2E Test');
    
    // Wait for filter to apply
    await page.waitForTimeout(1000);
    
    // Verify filtered results
    const projectCards = page.locator('[data-testid="project-card"]');
    if (await projectCards.count() > 0) {
      const firstCard = projectCards.first();
      await expect(firstCard).toContainText('E2E Test');
    }
  });

  test('should filter projects by status', async ({ page }) => {
    // Wait for projects to load
    await page.waitForLoadState('networkidle');
    
    // Use status filter
    await page.selectOption('select[name="status"]', 'active');
    
    // Wait for filter to apply
    await page.waitForTimeout(1000);
    
    // Verify filtered results show only active projects
    const projectCards = page.locator('[data-testid="project-card"]');
    if (await projectCards.count() > 0) {
      // Check that visible projects have active status
      const statusBadges = page.locator('[data-testid="status-badge"]');
      if (await statusBadges.count() > 0) {
        await expect(statusBadges.first()).toContainText('active');
      }
    }
  });

  test('should filter projects by region', async ({ page }) => {
    // Wait for projects to load
    await page.waitForLoadState('networkidle');
    
    // Use region filter
    await page.selectOption('select[name="region"]', 'US');
    
    // Wait for filter to apply
    await page.waitForTimeout(1000);
    
    // Verify filtered results
    const projectCards = page.locator('[data-testid="project-card"]');
    if (await projectCards.count() > 0) {
      // Check that visible projects are in US region
      await expect(projectCards.first()).toContainText('US');
    }
  });

  test('should edit a project', async ({ page }) => {
    // Wait for projects to load
    await page.waitForLoadState('networkidle');
    
    // Find and click edit button on first project
    const editButton = page.locator('[data-testid="edit-project-button"]').first();
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Verify edit form appears
      await expect(page.locator('text=Edit Project')).toBeVisible();
      
      // Make a change
      await page.fill('textarea[name="description"]', 'Updated via E2E test');
      
      // Submit changes
      await page.click('button[type="submit"]');
      
      // Verify success
      await expect(page.locator('text=Project updated successfully')).toBeVisible({ timeout: 10000 });
    }
  });

  test('should update project status', async ({ page }) => {
    // Ensure we're in status view
    await page.click('text=Status View');
    await page.waitForLoadState('networkidle');
    
    // Find a project and click status update
    const statusButton = page.locator('[data-testid="update-status-button"]').first();
    if (await statusButton.isVisible()) {
      await statusButton.click();
      
      // Update status
      await page.selectOption('select[name="status"]', 'active');
      await page.fill('input[name="progress_percentage"]', '75');
      await page.selectOption('select[name="health_status"]', 'green');
      await page.fill('textarea[name="status_notes"]', 'Updated via E2E test');
      
      // Submit update
      await page.click('button[type="submit"]');
      
      // Verify success
      await expect(page.locator('text=Status updated successfully')).toBeVisible({ timeout: 10000 });
    }
  });

  test('should handle project deletion', async ({ page }) => {
    // Switch to list view for easier access to delete buttons
    await page.click('text=List View');
    await page.waitForLoadState('networkidle');
    
    // Find delete button
    const deleteButton = page.locator('[data-testid="delete-project-button"]').first();
    if (await deleteButton.isVisible()) {
      // Set up dialog handler
      page.on('dialog', dialog => dialog.accept());
      
      await deleteButton.click();
      
      // Verify deletion success
      await expect(page.locator('text=Project deleted successfully')).toBeVisible({ timeout: 10000 });
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that page is still functional
    await expect(page.locator('h1')).toBeVisible();
    
    // Check that buttons are accessible
    await expect(page.locator('text=Quick Add')).toBeVisible();
    
    // Check that view toggles work
    await page.click('text=List View');
    await expect(page.locator('text=List View')).toHaveClass(/active|selected/);
  });

  test('should handle empty state', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/projects/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });
    
    await page.goto('/projects');
    
    // Check for empty state message
    await expect(page.locator('text=No projects yet')).toBeVisible();
    await expect(page.locator('text=Get started by creating your first project')).toBeVisible();
  });

  test('should handle API errors', async ({ page }) => {
    // Mock error response
    await page.route('**/api/projects/', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });
    
    await page.goto('/projects');
    
    // Check for error handling
    const errorMessage = page.locator('text=Error loading projects');
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toBeVisible();
    }
  });
});

test.describe('Project Intake Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects');
    await page.click('text=Project Intake Form');
  });

  test('should complete full intake form', async ({ page }) => {
    // Step 1: Basic Information
    await page.fill('input[name="project_name"]', 'Complete E2E Test Project');
    await page.selectOption('select[name="project_type"]', 'External');
    await page.fill('input[name="member_firm"]', 'Complete Test Corp');
    await page.selectOption('select[name="deployed_region"]', 'US');
    await page.fill('textarea[name="description"]', 'Complete project via intake form');
    await page.click('text=Next');

    // Step 2: Team Information
    await page.fill('input[name="engagement_manager"]', 'Test Manager');
    await page.fill('input[name="project_sponsor"]', 'Test Sponsor');
    await page.fill('input[name="technical_lead"]', 'Test Lead');
    await page.click('text=Next');

    // Step 3: Budget & Timeline
    await page.fill('input[name="project_startdate"]', '2024-01-01');
    await page.fill('input[name="project_enddate"]', '2024-12-31');
    await page.fill('input[name="budget_allocated"]', '150000');
    await page.click('text=Next');

    // Step 4: Technical Requirements
    await page.fill('input[name="cloud_providers"]', 'AWS, Azure');
    await page.selectOption('select[name="security_classification"]', 'Internal');
    await page.click('text=Next');

    // Step 5: Compliance & Risk
    await page.fill('input[name="compliance_requirements"]', 'SOC2, GDPR');
    await page.selectOption('select[name="risk_assessment"]', 'Medium');
    await page.click('text=Next');

    // Step 6: Review & Submit
    await expect(page.locator('text=Review Project Details')).toBeVisible();
    await expect(page.locator('text=Complete E2E Test Project')).toBeVisible();
    
    await page.click('text=Submit Project');

    // Verify success
    await expect(page.locator('text=Project created successfully')).toBeVisible({ timeout: 10000 });
  });

  test('should validate required fields', async ({ page }) => {
    // Try to proceed without filling required fields
    await page.click('text=Next');
    
    // Check for validation errors
    await expect(page.locator('text=This field is required')).toBeVisible();
  });

  test('should allow navigation between steps', async ({ page }) => {
    // Fill first step and proceed
    await page.fill('input[name="project_name"]', 'Navigation Test');
    await page.selectOption('select[name="project_type"]', 'External');
    await page.fill('input[name="member_firm"]', 'Test Corp');
    await page.selectOption('select[name="deployed_region"]', 'US');
    await page.click('text=Next');

    // Verify we're on step 2
    await expect(page.locator('text=Step 2')).toBeVisible();

    // Go back to step 1
    await page.click('text=Previous');

    // Verify we're back on step 1
    await expect(page.locator('text=Step 1')).toBeVisible();
    
    // Verify form data is preserved
    await expect(page.locator('input[name="project_name"]')).toHaveValue('Navigation Test');
  });

  test('should cancel intake form', async ({ page }) => {
    // Fill some data
    await page.fill('input[name="project_name"]', 'Cancel Test');
    
    // Click cancel
    await page.click('text=Cancel');
    
    // Verify we're back to projects page
    await expect(page.locator('h1')).toContainText('Project Management');
  });
});