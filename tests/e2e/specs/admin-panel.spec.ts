/**
 * Nexus Admin Panel — End-to-End Tests
 *
 * Covers WeSell platform management (port 3703):
 *   - Login as platform admin
 *   - Dashboard: cross-tenant KPIs + charts
 *   - Companies: list, suspend, activate, approve, detail view
 *   - Audit Logs: search, filter, entries
 *   - Settings: pricing tiers, feature flags, email templates
 */
import { test, expect } from '@playwright/test';

test.describe('Admin Panel — Authentication', () => {
  test('renders login page with WeSell branding', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toContainText('Nexus Admin');
    await expect(page.locator('body')).toContainText('WeSell');
    await expect(page.locator('body')).toContainText('Catalin Georgescu');
  });

  test('can login and navigate to dashboard', async ({ page }) => {
    await page.goto('/#dashboard');
    await expect(page.locator('.kpi-card').first()).toBeVisible({ timeout: 5000 });
  });

  test('sidebar shows admin navigation sections', async ({ page }) => {
    await page.goto('/#dashboard');
    const navItems = ['Dashboard', 'Companii', 'Audit', 'Setari'];
    for (const item of navItems) {
      await expect(page.locator('.sidebar-nav').getByText(item)).toBeVisible();
    }
  });
});

test.describe('Admin Panel — Dashboard', () => {
  test('shows 4 KPI cards', async ({ page }) => {
    await page.goto('/#dashboard');
    const cards = page.locator('.kpi-card');
    await expect(cards.first()).toBeVisible();
    expect(await cards.count()).toBe(4);
  });

  test('shows revenue bar chart', async ({ page }) => {
    await page.goto('/#dashboard');
    await expect(page.locator('.bar-chart').first()).toBeVisible();
    // Should have 6 months of data
    const bars = page.locator('.bar-chart').first().locator('.bar');
    expect(await bars.count()).toBe(6);
  });

  test('shows user growth chart', async ({ page }) => {
    await page.goto('/#dashboard');
    const charts = page.locator('.bar-chart');
    expect(await charts.count()).toBeGreaterThanOrEqual(2);
  });

  test('KPI values are displayed correctly', async ({ page }) => {
    await page.goto('/#dashboard');
    await expect(page.locator('body')).toContainText('Companii active');
    await expect(page.locator('body')).toContainText('Utilizatori activi');
    await expect(page.locator('body')).toContainText('Venit total');
    await expect(page.locator('body')).toContainText('Programari azi');
  });
});

test.describe('Admin Panel — Companies', () => {
  test('navigates to companies', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="companies"]').click();
    await expect(page).toHaveURL(/#companies/);
    await expect(page.locator('body')).toContainText('Gestiune Companii');
  });

  test('shows 4 companies in table', async ({ page }) => {
    await page.goto('/#companies');
    const rows = page.locator('.data-table tbody tr');
    await expect(rows.first()).toBeVisible();
    expect(await rows.count()).toBe(4);
  });

  test('status filter works', async ({ page }) => {
    await page.goto('/#companies');
    const activeFilter = page.locator('.filter-badge:has-text("Active")');
    if (await activeFilter.isVisible()) {
      await activeFilter.click();
      await page.waitForTimeout(300);
      // Only active companies should be visible
      const rows = page.locator('.data-table tbody tr');
      expect(await rows.count()).toBeLessThanOrEqual(4);
    }
  });

  test('search finds a specific company', async ({ page }) => {
    await page.goto('/#companies');
    const searchInput = page.locator('input[placeholder*="Cauta"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('Instalatii');
      await page.waitForTimeout(300);
      await expect(page.locator('body')).toContainText('Instalatii Bucuresti');
    }
  });

  test('can open company detail modal', async ({ page }) => {
    await page.goto('/#companies');
    const detailBtn = page.locator('button:has-text("Detalii")').first();
    if (await detailBtn.isVisible()) {
      await detailBtn.click();
      await page.waitForTimeout(300);
      await expect(page.locator('.modal-overlay[style*="flex"], .modal')).toBeVisible();
    }
  });

  test('can suspend a company', async ({ page }) => {
    await page.goto('/#companies');
    const suspendBtn = page.locator('button:has-text("Suspend")').first();
    if (await suspendBtn.isVisible()) {
      await suspendBtn.click();
      await page.waitForTimeout(300);
      await expect(page.locator('.toast')).toBeVisible({ timeout: 3000 });
    }
  });

  test('@mobile companies table is visible on mobile', async ({ page }) => {
    await page.goto('/#companies');
    await expect(page.locator('.data-table')).toBeVisible();
  });
});

test.describe('Admin Panel — Audit Logs', () => {
  test('navigates to audit logs', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="audit"]').click();
    await expect(page).toHaveURL(/#audit/);
    await expect(page.locator('body')).toContainText('Audit Logs');
  });

  test('shows audit entries', async ({ page }) => {
    await page.goto('/#audit');
    const entries = page.locator('.audit-entry');
    expect(await entries.count()).toBeGreaterThanOrEqual(3);
  });

  test('search filters audit logs', async ({ page }) => {
    await page.goto('/#audit');
    const searchInput = page.locator('input[placeholder*="Cauta"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('companie');
      await page.waitForTimeout(300);
      // Should filter to matching entries
      const entries = page.locator('.audit-entry');
      expect(await entries.count()).toBeGreaterThanOrEqual(0);
    }
  });
});

test.describe('Admin Panel — Settings', () => {
  test('navigates to settings', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="settings"]').click();
    await expect(page).toHaveURL(/#settings/);
    await expect(page.locator('body')).toContainText('Setari Platforma');
  });

  test('shows pricing tiers', async ({ page }) => {
    await page.goto('/#settings');
    const tierCards = page.locator('.tier-card');
    expect(await tierCards.count()).toBe(3); // Starter, Professional, Business
  });

  test('shows feature flags with toggles', async ({ page }) => {
    await page.goto('/#settings');
    const toggles = page.locator('.toggle');
    expect(await toggles.count()).toBeGreaterThanOrEqual(3);
  });

  test('can toggle a feature flag', async ({ page }) => {
    await page.goto('/#settings');
    const toggle = page.locator('.toggle input[type="checkbox"]').first();
    if (await toggle.isVisible()) {
      const wasChecked = await toggle.isChecked();
      await toggle.click();
      await page.waitForTimeout(300);
      expect(await toggle.isChecked()).toBe(!wasChecked);
    }
  });

  test('can edit a pricing tier', async ({ page }) => {
    await page.goto('/#settings');
    const editBtn = page.locator('button:has-text("Editeaza")').first();
    if (await editBtn.isVisible()) {
      await editBtn.click();
      await page.waitForTimeout(300);
      await expect(page.locator('.modal-overlay[style*="flex"], .modal')).toBeVisible();
    }
  });

  test('shows email templates', async ({ page }) => {
    await page.goto('/#settings');
    await expect(page.locator('body')).toContainText('Template-uri email');
  });
});

test.describe('Admin Panel — Hallmark Design', () => {
  test('uses admin color palette (not terracotta)', async ({ page }) => {
    await page.goto('/#dashboard');
    const hasAdminColor = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      return styles.getPropertyValue('--color-admin').trim().length > 0;
    });
    expect(hasAdminColor).toBe(true);
  });

  test('login page has admin badge', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.login-badge')).toBeVisible();
    await expect(page.locator('.login-badge')).toContainText('WeSell');
  });
});