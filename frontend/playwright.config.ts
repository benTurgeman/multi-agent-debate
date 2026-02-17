import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for E2E tests
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',

  // Maximum time one test can run for
  timeout: 120 * 1000, // 2 minutes - debates can take time

  // Test execution settings
  fullyParallel: false, // Run tests serially to avoid port conflicts
  forbidOnly: !!process.env.CI, // Fail CI if test.only is committed
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker to avoid conflicts

  // Reporter configuration
  reporter: [
    ['html'],
    ['list'],
  ],

  // Shared settings for all projects
  use: {
    // Base URL for frontend
    baseURL: 'http://localhost:5173',

    // Collect trace on failure
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Extended timeout for actions
    actionTimeout: 10000,

    // Extended timeout for navigation
    navigationTimeout: 30000,
  },

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Uncomment to test in other browsers
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // Web server configuration - start frontend and backend automatically
  webServer: [
    {
      command: 'cd ../backend && poetry run uvicorn main:app --host 0.0.0.0 --port 8000',
      url: 'http://localhost:8000/docs',
      reuseExistingServer: !process.env.CI,
      timeout: 30 * 1000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 30 * 1000,
    },
  ],
});
