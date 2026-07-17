import { defineConfig, devices } from '@playwright/test';

/**
 * Nexus SaaS — Playwright Configuration
 *
 * Tests all 3 mock interfaces (ADR-0012):
 *   - Main App (3701): Business management — appointments, customers, invoices
 *   - Client Portal (3702): Customer self-service — booking, invoices, loyalty
 *   - Admin Panel (3703): WeSell platform — companies, audit, settings
 *
 * Prerequisites: `docker compose up -d mock client-portal admin-panel`
 */
export default defineConfig({
  testDir: './specs',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list'],
  ],
  timeout: 30_000,
  expect: { timeout: 10_000 },

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    locale: 'ro-RO',
  },

  projects: [
    // ── Main App (port 3701) ──
    {
      name: 'main-app',
      testMatch: 'main-app.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:3701',
        viewport: { width: 1440, height: 900 },
      },
    },

    // ── Client Portal (port 3702) ──
    {
      name: 'client-portal',
      testMatch: 'client-portal.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:3702',
        viewport: { width: 1280, height: 800 },
      },
    },

    // ── Admin Panel (port 3703) ──
    {
      name: 'admin-panel',
      testMatch: 'admin-panel.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:3703',
        viewport: { width: 1440, height: 900 },
      },
    },

    // ── Mobile viewport smoke test ──
    {
      name: 'mobile-smoke',
      testMatch: '**/*.spec.ts',
      use: {
        ...devices['Pixel 7'],
        viewport: { width: 412, height: 915 },
      },
      grep: /@mobile/,
    },
  ],

  // Local dev server — not needed (mocks run in Docker)
  // webServer: [],
});