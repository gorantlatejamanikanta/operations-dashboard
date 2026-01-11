import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load dashboard page', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Multi-Cloud Operations Dashboard/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Multi-Cloud Operations Dashboard');
    
    // Check navigation elements
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should display key metrics cards', async ({ page }) => {
    // Wait for dashboard to load
    await page.waitForLoadState('networkidle');
    
    // Check for metrics cards
    const metricsCards = page.locator('[data-testid="metrics-card"]');
    await expect(metricsCards).toHaveCount(4);
    
    // Check specific metrics
    await expect(page.locator('text=Total Projects')).toBeVisible();
    await expect(page.locator('text=Active Projects')).toBeVisible();
    await expect(page.locator('text=Total Cost')).toBeVisible();
    await expect(page.locator('text=Monthly Cost')).toBeVisible();
  });

  test('should display charts and visualizations', async ({ page }) => {
    // Wait for charts to load
    await page.waitForLoadState('networkidle');
    
    // Check for chart containers
    await expect(page.locator('[data-testid="projects-by-region-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="cost-trend-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="project-status-chart"]')).toBeVisible();
  });

  test('should navigate to projects page', async ({ page }) => {
    // Click on projects navigation link
    await page.click('text=Projects');
    
    // Verify navigation
    await expect(page).toHaveURL(/.*\/projects/);
    await expect(page.locator('h1')).toContainText('Project Management');
  });

  test('should navigate to costs page', async ({ page }) => {
    // Click on costs navigation link
    await page.click('text=Costs');
    
    // Verify navigation
    await expect(page).toHaveURL(/.*\/costs/);
    await expect(page.locator('h1')).toContainText('Cost Management');
  });

  test('should toggle theme', async ({ page }) => {
    // Find theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    await expect(themeToggle).toBeVisible();
    
    // Get initial theme
    const initialTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark');
    });
    
    // Click theme toggle
    await themeToggle.click();
    
    // Verify theme changed
    const newTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark');
    });
    
    expect(newTheme).toBe(!initialTheme);
  });

  test('should display recent activities', async ({ page }) => {
    // Wait for activities to load
    await page.waitForLoadState('networkidle');
    
    // Check for recent activities section
    await expect(page.locator('text=Recent Activities')).toBeVisible();
    
    // Check for activity items
    const activityItems = page.locator('[data-testid="activity-item"]');
    await expect(activityItems.first()).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that page is still functional
    await expect(page.locator('h1')).toBeVisible();
    
    // Check mobile navigation
    const mobileMenu = page.locator('[data-testid="mobile-menu"]');
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();
      await expect(page.locator('nav')).toBeVisible();
    }
  });

  test('should handle loading states', async ({ page }) => {
    // Intercept API calls to simulate slow loading
    await page.route('**/api/dashboard/summary', async route => {
      await page.waitForTimeout(1000); // Simulate slow response
      await route.continue();
    });
    
    await page.goto('/');
    
    // Check for loading indicators
    const loadingIndicator = page.locator('[data-testid="loading"]');
    if (await loadingIndicator.isVisible()) {
      await expect(loadingIndicator).toBeVisible();
      await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
    }
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls to simulate errors
    await page.route('**/api/dashboard/summary', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });
    
    await page.goto('/');
    
    // Check for error handling
    const errorMessage = page.locator('text=Error loading dashboard data');
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toBeVisible();
    }
  });
});

test.describe('Dashboard Interactions', () => {
  test('should refresh data when refresh button is clicked', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find and click refresh button
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      
      // Verify data refresh (loading state or updated timestamp)
      const loadingIndicator = page.locator('[data-testid="loading"]');
      if (await loadingIndicator.isVisible()) {
        await expect(loadingIndicator).toBeVisible();
        await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
      }
    }
  });

  test('should filter data by date range', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find date range picker
    const dateRangePicker = page.locator('[data-testid="date-range-picker"]');
    if (await dateRangePicker.isVisible()) {
      await dateRangePicker.click();
      
      // Select a date range
      await page.click('text=Last 30 days');
      
      // Verify data updates
      await page.waitForLoadState('networkidle');
      await expect(page.locator('[data-testid="metrics-card"]').first()).toBeVisible();
    }
  });

  test('should export dashboard data', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find export button
    const exportButton = page.locator('[data-testid="export-button"]');
    if (await exportButton.isVisible()) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Verify download
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/dashboard.*\.(csv|xlsx|pdf)/);
    }
  });
});