import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup...');
  
  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for backend to be ready
    console.log('⏳ Waiting for backend to be ready...');
    let backendReady = false;
    let attempts = 0;
    const maxAttempts = 30;
    
    while (!backendReady && attempts < maxAttempts) {
      try {
        const response = await page.request.get('http://localhost:8000/health');
        if (response.ok()) {
          backendReady = true;
          console.log('✅ Backend is ready');
        }
      } catch (error) {
        attempts++;
        await page.waitForTimeout(1000);
      }
    }
    
    if (!backendReady) {
      throw new Error('Backend failed to start within timeout');
    }
    
    // Wait for frontend to be ready
    console.log('⏳ Waiting for frontend to be ready...');
    let frontendReady = false;
    attempts = 0;
    
    while (!frontendReady && attempts < maxAttempts) {
      try {
        await page.goto('http://localhost:3001');
        await page.waitForSelector('body', { timeout: 5000 });
        frontendReady = true;
        console.log('✅ Frontend is ready');
      } catch (error) {
        attempts++;
        await page.waitForTimeout(1000);
      }
    }
    
    if (!frontendReady) {
      throw new Error('Frontend failed to start within timeout');
    }
    
    // Seed test data
    console.log('🌱 Seeding test data...');
    try {
      const seedResponse = await page.request.post('http://localhost:8000/api/projects/', {
        headers: {
          'Authorization': 'Bearer demo-token',
          'Content-Type': 'application/json'
        },
        data: {
          project_name: 'E2E Test Project',
          project_type: 'External',
          member_firm: 'Test Corporation',
          deployed_region: 'US',
          description: 'Project created for E2E testing',
          engagement_manager: 'Test Manager',
          project_startdate: '2024-01-01',
          project_enddate: '2024-12-31',
          budget_allocated: 100000,
          priority: 'medium'
        }
      });
      
      if (seedResponse.ok()) {
        console.log('✅ Test data seeded successfully');
      }
    } catch (error) {
      console.warn('⚠️ Failed to seed test data:', error);
    }
    
    console.log('✅ Global setup completed');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;