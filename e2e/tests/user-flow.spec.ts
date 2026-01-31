import { test, expect } from "@playwright/test";

test.describe("User Registration and Login Flow", () => {
  test("should register a new user and login", async ({ page }) => {
    // Navigate to homepage and wait for it to load
    await page.goto("/", { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector("text=Register", { timeout: 10000 });

    // Go to registration page
    await page.click("text=Register");
    await page.fill('input[placeholder="Email"]', "e2euser@example.com");
    await page.fill('input[placeholder="Password"]', "E2Epassword123!");
    await page.fill('input[placeholder="Full Name"]', "E2E User");
    await page.getByTestId("register-submit-button").click();

    // Wait for success message
    await expect(page.getByTestId("registration-message")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByTestId("registration-message")).toHaveText(
      "Registration successful"
    );

    // Go to login page
    await page.click("text=Login");
    await page.fill('input[placeholder="Email"]', "e2euser@example.com");
    await page.fill('input[placeholder="Password"]', "E2Epassword123!");
    await page.getByTestId("login-submit-button").click();
    await expect(page.locator("text=Welcome, E2E User")).toBeVisible();
  });

  test("should not register with invalid email", async ({ page }) => {
    await page.goto("/", { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector("text=Register", { timeout: 10000 });
    await page.click("text=Register");
    await page.fill('input[placeholder="Email"]', "not-an-email");
    await page.fill('input[placeholder="Password"]', "E2Epassword123!");
    await page.fill('input[placeholder="Full Name"]', "E2E User");
    await page.getByTestId("register-submit-button").click();

    // Wait for error message
    await expect(page.getByTestId("registration-message")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByTestId("registration-message")).toHaveText(
      "Invalid email"
    );
  });

  test("should not login with wrong password", async ({ page }) => {
    await page.goto("/", { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector("text=Login", { timeout: 10000 });
    await page.click("text=Login");
    await page.fill('input[placeholder="Email"]', "e2euser@example.com");
    await page.fill('input[placeholder="Password"]', "wrongpassword");
    await page.getByTestId("login-submit-button").click();

    // Wait for error message
    await expect(page.getByTestId("login-message")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByTestId("login-message")).toHaveText(
      "Invalid credentials"
    );
  });
});
