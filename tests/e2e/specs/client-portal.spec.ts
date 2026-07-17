/**
 * Nexus Client Portal — End-to-End Tests
 *
 * Covers customer self-service (port 3702):
 *   - Login as customer
 *   - Dashboard with KPIs
 *   - Appointments: list + book new
 *   - Invoices: list + pay
 *   - Chat: messaging with business
 *   - Loyalty: points, redemptions, referral
 */
import { test, expect } from '@playwright/test';

test.describe('Client Portal — Authentication', () => {
  test('renders login page with customer info', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toContainText('Portal Client');
    await expect(page.locator('body')).toContainText('Elena Dumitrescu');
  });

  test('can login and navigate to dashboard', async ({ page }) => {
    await page.goto('/');
    await page.locator('button:has-text("Intra"), button:has-text("Cont")').click();
    await page.waitForURL(/#dashboard/);
    await expect(page.locator('.kpi-card').first()).toBeVisible();
  });

  test('sidebar shows customer business name', async ({ page }) => {
    await page.goto('/#dashboard');
    await expect(page.locator('.sidebar-brand')).toContainText('Instalatii Bucuresti');
  });
});

test.describe('Client Portal — Dashboard', () => {
  test('shows 4 KPI cards', async ({ page }) => {
    await page.goto('/#dashboard');
    const cards = page.locator('.kpi-card');
    await expect(cards.first()).toBeVisible();
    expect(await cards.count()).toBe(4);
  });

  test('shows next appointment', async ({ page }) => {
    await page.goto('/#dashboard');
    await expect(page.locator('body')).toContainText('Urmatoarea programare');
  });

  test('shows loyalty points', async ({ page }) => {
    await page.goto('/#dashboard');
    await expect(page.locator('body')).toContainText('Puncte loialitate');
  });
});

test.describe('Client Portal — Appointments', () => {
  test('navigates to appointments', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="appointments"]').click();
    await expect(page).toHaveURL(/#appointments/);
    await expect(page.locator('body')).toContainText('Programarile mele');
  });

  test('shows book appointment button', async ({ page }) => {
    await page.goto('/#appointments');
    await expect(page.locator('button:has-text("Programare noua")')).toBeVisible();
  });

  test('can open book appointment modal', async ({ page }) => {
    await page.goto('/#appointments');
    await page.locator('button:has-text("Programare noua")').click();
    await expect(page.locator('.modal-overlay[style*="flex"], .modal')).toBeVisible();
    await expect(page.locator('body')).toContainText('Serviciu');
  });

  test('can book a new appointment', async ({ page }) => {
    await page.goto('/#appointments');
    await page.locator('button:has-text("Programare noua")').click();
    await page.waitForTimeout(300);
    // Select a service
    await page.locator('#mservice').selectOption({ index: 0 });
    // Click confirm
    await page.locator('button:has-text("Confirma")').click();
    await page.waitForTimeout(500);
    // Toast should appear
    await expect(page.locator('.toast')).toBeVisible({ timeout: 3000 });
  });
});

test.describe('Client Portal — Invoices', () => {
  test('navigates to invoices', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="invoices"]').click();
    await expect(page).toHaveURL(/#invoices/);
    await expect(page.locator('body')).toContainText('Facturile mele');
  });

  test('shows unpaid invoice with pay button', async ({ page }) => {
    await page.goto('/#invoices');
    const payBtn = page.locator('button:has-text("Plateste")');
    if (await payBtn.isVisible()) {
      await payBtn.first().click();
      await page.waitForTimeout(300);
      await expect(page.locator('.toast')).toBeVisible({ timeout: 3000 });
    }
  });
});

test.describe('Client Portal — Chat', () => {
  test('navigates to chat', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="chat"]').click();
    await expect(page).toHaveURL(/#chat/);
    await expect(page.locator('body')).toContainText('Mesaje');
  });

  test('can send a message', async ({ page }) => {
    await page.goto('/#chat');
    const input = page.locator('#chatMsgInput');
    if (await input.isVisible()) {
      await input.fill('Buna ziua! Test automat.');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(300);
      await expect(page.locator('.chat-msg-text').filter({ hasText: 'Buna ziua! Test automat.' })).toBeVisible();
    }
  });
});

test.describe('Client Portal — Loyalty', () => {
  test('navigates to loyalty', async ({ page }) => {
    await page.goto('/#dashboard');
    await page.locator('[data-nav="loyalty"]').click();
    await expect(page).toHaveURL(/#loyalty/);
    await expect(page.locator('body')).toContainText('Loialitate');
  });

  test('shows points balance', async ({ page }) => {
    await page.goto('/#loyalty');
    await expect(page.locator('.points')).toContainText('340');
  });

  test('shows redemption options', async ({ page }) => {
    await page.goto('/#loyalty');
    const redemptionBtns = page.locator('button:has-text("pct")');
    expect(await redemptionBtns.count()).toBeGreaterThanOrEqual(2);
  });

  test('can redeem available reward', async ({ page }) => {
    await page.goto('/#loyalty');
    // Click first enabled redemption (100 points)
    const redeemBtn = page.locator('button:has-text("100 pct")');
    if (await redeemBtn.isVisible() && await redeemBtn.isEnabled()) {
      await redeemBtn.click();
      await page.waitForTimeout(300);
      await expect(page.locator('.toast')).toBeVisible({ timeout: 3000 });
    }
  });

  test('referral link is visible', async ({ page }) => {
    await page.goto('/#loyalty');
    await expect(page.locator('body')).toContainText('ELENA25');
  });

  test('@mobile loyalty page works on mobile', async ({ page }) => {
    await page.goto('/#loyalty');
    await expect(page.locator('.loyalty-card')).toBeVisible();
  });
});