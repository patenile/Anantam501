
import { test, expect } from '@playwright/test';

// Health check utility
async function waitForFrontend(page, url, timeout = 20000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 3000 });
      if (await page.title()) return true;
    } catch (e) {
      // Wait and retry
      await page.waitForTimeout(1000);
    }
  }
  throw new Error('Frontend did not become ready in time');
}

test.describe('User Registration and Login Flow', () => {
  test('should register a new user and login', async ({ page }) => {
    // Health check: wait for frontend to be ready
    await waitForFrontend(page, '/');
    // Go to registration page
    await page.click('text=Register');
    await page.fill('input[type="email"]', 'e2euser@example.com');
    await page.fill('input[type="password"]', 'E2Epassword123!');
    await page.fill('input[placeholder="Full Name"], input[name="full_name"]', 'E2E User');
    await page.click('button:has-text("Register")');
    await expect(page.locator('text=Registration successful')).toBeVisible();

    // Go to login page
    await page.click('text=Login');
    await page.fill('input[type="email"]', 'e2euser@example.com');
    await page.fill('input[type="password"]', 'E2Epassword123!');
    await page.click('button:has-text("Login")');
    await expect(page.locator('text=Welcome, E2E User')).toBeVisible();
  });

  test('should not register with invalid email', async ({ page }) => {
    await waitForFrontend(page, '/');
    await page.click('text=Register');
    await page.fill('input[type="email"]', 'not-an-email');
    await page.fill('input[type="password"]', 'E2Epassword123!');
    await page.fill('input[placeholder="Full Name"], input[name="full_name"]', 'E2E User');
    await page.click('button:has-text("Register")');
    await expect(page.locator('text=Invalid email')).toBeVisible();
  });

  test('should not login with wrong password', async ({ page }) => {
    await waitForFrontend(page, '/');
    await page.click('text=Login');
    await page.fill('input[type="email"]', 'e2euser@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button:has-text("Login")');
    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });
});
